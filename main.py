from fastapi import FastAPI, Request, Form, UploadFile,File, HTTPException, Depends,  status, Query
from fastapi.responses import HTMLResponse, JSONResponse,FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from botocore.exceptions import ClientError
import requests
import random
import smtplib
import pymysql
from starlette.middleware.sessions import SessionMiddleware 
import secrets
import boto3
from datetime import datetime
import datetime
import bcrypt
import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import os
import json
import pandas as pd
import asyncio
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
templates = Jinja2Templates(directory="templates")


#==========================================================================

app.mount("/static", StaticFiles(directory=os.path.join(os.getcwd(), "static")), name="static")
app.mount("/static", StaticFiles(directory="static"), name="static")
# Database connection settings
DB_USER = "praveend"
DB_PASSWORD = "Praveend@jn2"
DB_HOST = "gofin-aurora-instance-1.ci0rkg2zgzsd.us-east-1.rds.amazonaws.com"
DB_NAME = "usda"

# Create a pymysql connection
conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, db=DB_NAME)

current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#------------------------------------------------------------------
# Define the maximum session duration (5 minutes)
SESSION_TIMEOUT_MINUTES = 5

# Generate a secret key securely and use it consistently
SECRET_KEY = secrets.token_urlsafe(32)


# Add SessionMiddleware to your app
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Function to check if the user is still active
async def check_user_activity(request: Request):
    last_activity = request.session.get("last_activity")
    if last_activity:
        current_time = datetime.datetime.now()
        if (current_time - last_activity) > datetime.timedelta(minutes=SESSION_TIMEOUT_MINUTES):
            # User is inactive, clear session and log them out
            request.session.clear()
    request.session["last_activity"] = datetime.datetime.now()

# Middleware to check user activity
@app.middleware("http")
async def check_activity_middleware(request: Request, call_next):
    check_user_activity(request)
    response = await call_next(request)
    return response

# Function to get the current user's session
def get_current_user_session(request: Request = Depends()):
    session = request.session
    if "user_id" not in session:
        # If "user_id" is not in the session, it means the user is not logged in.
        raise HTTPException(status_code=401, detail="User is not logged in")
    return session

# Function to get the current user's ID
def get_current_user_id(request: Request = Depends(get_current_user_session)):
    user_id = request.session.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not logged in")
    return user_id


#======================================================================================================================

@app.post("/admin_login")
async def admin_login(request: Request):
    try:
        form_data = await request.json()

        userId = form_data.get("userId")
        password = form_data.get("password")

        # Check if the user ID exists in the database
        aws_api_url = f"https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Admin/Admin_Login?userId={userId}"
        response = requests.get(aws_api_url)

        if not response:
            # User ID not found
            return JSONResponse(status_code=401, content="Invalid User ID")

        # Check the password
        db_user = response.json() # Assuming the procedure returns user data
        db_password = db_user.get('PASSWORD')  # Get the PASSWORD attribute
        if db_password == password:
            # Password matches
            request.session["userId"] = userId
            return templates.TemplateResponse("adminDashboard.html", {"request": request, "userId": userId})
        else:
                # Password does not match
                return JSONResponse(status_code=401, content="Invalid Credentials")

    except Exception as e:
        # Handle other exceptions with a 500 Internal Server Error response
        return JSONResponse(status_code=500, content={"error": f"An error occurred: {str(e)}"})

#==========================================================================================================================
#REGISTER COMPANY

@app.post("/register_company")
async def register_company(request: Request):
    userId = request.session.get("userId")
    if not userId:
        return JSONResponse(status_code=401, content={"error": "User is not logged in"})
 
    try:
        form_data = await request.json()
 
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        email = form_data.get("companyEmail")
        role= form_data.get("role")
        userName= form_data.get("userName")
        FLAG=1
        salt = bcrypt.gensalt()
        password = email.split('@')[0]
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        salt_base64 = base64.b64encode(salt).decode('utf-8')
      

        hashed_password_base64 = base64.b64encode(hashed_password).decode('utf-8')

        company_name = form_data.get("companyName")  # Correct the key to match the HTML form
        
        aws_api_url = f"https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Company/Company_registration?email={email}&company_name={company_name}"
        A = role
        B = userName
        C = company_name  # Use the corrected key
        D = email
        E = form_data.get("contact")
        H = FLAG
        X = userId
        Y = current_datetime
        Z = current_datetime

        request_body = {
            "A" : A,
            "B" : B,
            "C" : C,
            "D" : D,
            "E" : E,
            "H" : H,
            "X" : X,
            "Y" : Y,
            "Z" : Z,
            "hashed_password" : hashed_password_base64,
            "salt" : salt_base64
        }

        
        response = requests.post(aws_api_url, json=request_body)
    
        user_data = response.json()

        CADMIN_ID = user_data.get('CADMIN_ID')
        if response.status_code == 200:
            send_email_to_company(email, company_name, CADMIN_ID, password) 
            return {"message": f"{response.text}"}
        else:
            return {"error": f"HTTP Error: {response.status_code}", "message": f"HTTP Error: {response.text}"}
        
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}

def send_email_to_company(receiver_email, company_name, userName, password):
    sender_email = "pkd17789@gmail.com"  # Replace with your Gmail email address
    sender_password = "trhk qgfy hwyw jpze"  # Replace with your Gmail password

    message = MIMEMultipart("alternative")
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Welcome to Our Platform"

    # Email content
    text = f"Hi {company_name},\n\nWelcome to GoFin:Fast & Easy Funding!\n\nYour login details:\n\nUser Name: {userName}\nPassword: {password}\n\nRemember, This is a Temporary Password. Please chage the password after logging in for First time.\nThank you."
    html = f"""\
    <html>
      <body>
        <p>Hi {company_name},</p>
        <p>Welcome to GoFin:Fast & Easy Funding!</p>
        <p>Your login details:</p>
        <ul>
          <li><strong>User ID:</strong> {userName}</li>
          <li><strong>Password:</strong> {password}</li>
        </ul>
        <p>Remember, This is a Temporary Password. Please chage the password after logging in for First time.</p>
        <p>Thank you.</p>
      </body>
    </html>
    """

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    message.attach(part1)
    message.attach(part2)

    # Connect to Gmail's SMTP server
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())

#=========================================================================================================================
# EXISTING COMPANIES
    

@app.get("/get_existing_companies", response_class=JSONResponse)
async def get_existing_companies(request: Request):
    userId = request.session.get("userId")
    if not userId:
        return JSONResponse(status_code=401, content={"error": "User is not logged in"})
    try:
        aws_api_url = f"https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Company/Existing_Companies"
        response = requests.get(aws_api_url)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            error_message = f"Failed to fetch data. Status code: {response.status_code}"
            return JSONResponse(status_code=500, content={"error": error_message})

    except Exception as e:
        error_message = f"An error occurred while fetching data: {str(e)}"
        return JSONResponse(status_code=500, content={"error": error_message})
    
#=====================================================================================================================================
#Company Admin Login Page:(archna)        

@app.post("/cadmin_login")
async def signin(request: Request):
    try:
        form_data = await request.json()

        userName = form_data.get("userName")
        password = form_data.get("password")
        
        aws_api_url = f"https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Company/Company_Admin_Login?userName={userName}"
        response = requests.get(aws_api_url)
       
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="User Not Found")
 
        user_data = response.json()
        userID = user_data.get('ADMIN_ID')
        hashed_password_base64 = user_data.get('PASSWORD')
        print("hashed password base64", hashed_password_base64)

        salt_base64 = user_data.get('SALT')
        print("salt_base64",salt_base64)

        role = user_data.get('ROLE')  # Assuming ROLE is the field for the role
        flag = user_data.get('FLAG')
 
        if hashed_password_base64 is None or salt_base64 is None:
            raise HTTPException(status_code=401, detail="Invalid user data")
 
        # Decode the base64 encoded salt and hashed_password
        try:
            salt = base64.b64decode(salt_base64 + '==')  # Add padding
            print("salt",salt)
        except Exception as decode_error:
            raise HTTPException(status_code=500, detail="Error decoding salt")
 
        try:
            hashed_password_bytes = base64.b64decode(hashed_password_base64 + '==')  # Add padding
            print("hashed_password_bytes",hashed_password_bytes)
        except Exception as decode_error:
            raise HTTPException(status_code=500, detail="Error decoding hashed_password")
 
        # Hash the input password with the decoded salt
        input_password = password.encode('utf-8')
        print("Input Password", input_password)
        # Debugging output
        hashed_input_password = bcrypt.hashpw(input_password, salt)
 
        print("Hashed Input Pass",hashed_input_password)
        print(bcrypt.checkpw(input_password, hashed_password_bytes))
        # Compare hashed passwords directly
        if role != 'Company':
            return JSONResponse(status_code=401, content="Invalid Role")
        elif bcrypt.checkpw(input_password, hashed_password_bytes):
            request.session["userName"] = userName
            request.session["compId"] = userID
            if flag == 1:
                return {"redirect": "/resetPass.html"}  # Indicate redirection in the response
            
            return {"message": "Login successful", "redirect": "/compDashboard.html"}  # Modify redirect URL as needed
        else:
            raise HTTPException(status_code=401, detail="Login failed. Incorrect password")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during login: {str(e)}")




#===================================Investor Login:(archna)  ================      

# Assuming you have the necessary imports already present in your code
@app.post("/investor_login")
async def investor_login(request: Request):
    try:
        form_data = await request.json()

        userName = form_data.get("userName")
        password = form_data.get("password")
 
        aws_api_url = f"https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Company/Company_Admin_Login?userName={userName}"
        response = requests.get(aws_api_url)
       
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="User Not Found")
 
        user_data = response.json()
        userID = user_data.get('ADMIN_ID')
        hashed_password_base64 = user_data.get('PASSWORD')
        salt_base64 = user_data.get('SALT')
        role = user_data.get('ROLE')  # Assuming ROLE is the field for the role
        flag = user_data.get('FLAG')
 
        if hashed_password_base64 is None or salt_base64 is None:
            raise HTTPException(status_code=401, detail="Invalid user data")
 
        # Decode the base64 encoded salt and hashed_password
        try:
            salt = base64.b64decode(salt_base64 + '==')  # Add padding
        except Exception as decode_error:
            raise HTTPException(status_code=500, detail="Error decoding salt")
 
        try:
            hashed_password_bytes = base64.b64decode(hashed_password_base64 + '==')  # Add padding
        except Exception as decode_error:
            raise HTTPException(status_code=500, detail="Error decoding hashed_password")
 
        # Hash the input password with the decoded salt
        input_password = password.encode('utf-8')

 
        # Debugging output
        hashed_input_password = bcrypt.hashpw(input_password, salt)

        # Compare hashed passwords directly
        if role != 'Investor':
            return JSONResponse(status_code=401, content="Invalid Role")
        elif hashed_input_password == hashed_password_bytes:
            request.session["userName"] = userName
            request.session["cmpId"] = userID

            if flag == 1:  
                return {"redirect": "/resetPass.html"}  
            
            return {"message": "Login successful", "redirect": "/investorDashboard.html"}  # Modify redirect URL as needed
        else:
            raise HTTPException(status_code=401, detail="Login failed. Incorrect password")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during login: {str(e)}")

#========================================================================
@app.post("/set_password")
async def set_password(
    request: Request,
    securityQuestion: str = Form(...),
    answer: str = Form(...),
    newPassword: str = Form(...),
    confirmPassword: str = Form(...),
):
    userName = request.session.get("userName")
    if not userName:
        return JSONResponse(status_code=401, content="User is not logged in")

    try:
        # Validate passwords match
        if newPassword != confirmPassword:
            return {"error": "Passwords do not match"}

        # Get current datetime
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        Flag = 0
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(newPassword.encode('utf-8'), salt)

        salt_base64 = base64.b64encode(salt).decode('utf-8')
        hashed_password_base64 = base64.b64encode(hashed_password).decode('utf-8')

        aws_api_url = f"https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Company/Cadmin_set_password"

        request_body = {
            "user_id": userName,  
            "security_question": securityQuestion,
            "security_answer": answer,
            "Flag": Flag,
            "hashed_password": hashed_password_base64,
            "salt": salt_base64
        }

        response = requests.post(aws_api_url, json=request_body)

        if response.status_code == 200:
            return {"success": True, "message": "Password reset successfully"}
        else:
            error_message = f"Error resetting password. AWS API Response: {response.content}"
            return {"success": False, "message": error_message}


    except Exception as e:
        return {"error": str(e)}


#==========================================================================================
# EXISTING Employees
    
@app.get("/get_existing_employees", response_class=JSONResponse)
async def get_existing_companies(request: Request):
    userId = request.session.get("compId")
    if not userId:
        return JSONResponse(status_code=401, content={"error": "User is not logged in"})
    try:
        aws_api_url = f"https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Company_Employee/Existing_Employee?userId={userId}"
        response = requests.get(aws_api_url)

        if response.status_code == 200:
            data = response.json()
            print(data)
            return data
        else:
            error_message = f"Failed to fetch data. Status code: {response.status_code}"
            return JSONResponse(status_code=500, content={"error": error_message})

    except Exception as e:
        error_message = f"An error occurred while fetching data: {str(e)}"
        return JSONResponse(status_code=500, content={"error": error_message})

#=================================================================================================
    
@app.post("/register_company_employee")
async def register_company_employee(request: Request):
    userId = request.session.get("compId")
    if not userId:
        return JSONResponse(status_code=401, content="User is not logged in")
    try:
        form_data = await request.json()
 
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        salt = bcrypt.gensalt()
        email = form_data.get("empEmail")
        password = email.split('@')[0]
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        salt_base64 = base64.b64encode(salt).decode('utf-8')
        hashed_password_base64 = base64.b64encode(hashed_password).decode('utf-8')

        COMP_ID = userId
        aws_api_url = f"https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Company_Employee/Register_Company_Employee?email={email}&COMP_ID={COMP_ID}"
 
        empName = form_data.get("empName")
        role = None
        D = str(form_data.get("contact"))
        flag = 1
        U = form_data.get("userName")
        X = userId
        Y = current_datetime
        Z = current_datetime

        request_body = {
            "B" : empName,
            "C" : role,
            "D" : D,
            "E":  flag,
            "U" : U,
            "X" : X,
            "Y" : Y,
            "Z" : Z,
            "hashed_password" : hashed_password_base64,
            "salt" : salt_base64
        }

        response = requests.post(aws_api_url, json=request_body)

        user_data = response.json()

        E_ID = user_data.get('E_ID')

        if response.status_code == 200:
            send_email_to_company(email,empName, E_ID, password)
            return {"message": f"{response.text}"}
        else:
            return {"error": f"HTTP Error: {response.status_code}", "message": f"HTTP Error: {response.text}"}

    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}

#---------------------------------------------------------------------------
def send_email_to_employee(receiver_email, empName, user_id, password):
    sender_email = "pkd17789@gmail.com"  # Replace with your Gmail email address
    sender_password = "trhk qgfy hwyw jpze"  # Replace with your Gmail password

    message = MIMEMultipart("alternative")
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Welcome to Our Platform"

    # Email content
    text = f"Hi {empName},\n\nWelcome to GoFin:Fast & Easy Funding!\n\nYour login details:\n\nUser ID: {user_id}\nPassword: {password}\n\nRemember, This is a Temporary Password. Please chage the password after logging in for First time.\nThank you."
    html = f"""\
    <html>
      <body>
        <p>Dear {empName},</p>
        <p>Welcome to GoFin:Fast & Easy Funding!</p>
        <p>A Login Detail has been created for your Gofin account:</p>
        <ul>
          <li><strong>User ID:</strong> {user_id}</li>
          <li><strong>Temporary Password:</strong> {password}</li>
        </ul>
        <p>This password is valid for First time login only. Please reset your password when you log in to your account for the first time.</p>
        <p>For help, please contact us at:</p>
        <p>support@Gofin.com.</p>
        <p>Regards,</p>
        <img src="https://gofin.ai/wp-content/uploads/2022/10/GoFin-Data-Solutions-1.png"  alt="GoFin" width="200px">
      </body>
    </html>
    """

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    message.attach(part1)
    message.attach(part2)

    # Connect to Gmail's SMTP server
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())

#============================================================================================================================
# Company employee login

@app.post("/cemployee_login")
async def signin(request: Request):
    try:
        form_data = await request.json()

        userName = form_data.get("userName")
        password = form_data.get("password")
        print(f"userId: {userName}, password: {password}")


        aws_api_url = f"https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Company_Employee/Company_Employee_Login?userName={userName}"
        response = requests.get(aws_api_url)
        print(response)

        if response.status_code != 200:
            # print("Invalid User ID")
            raise HTTPException(status_code=401, detail="Invalid User ID")

        user_data = response.json()
        print(f"user_data: {user_data}")

        hashed_password_base64 = user_data.get('PASSWORD')
        print(f"hashed_password_base64: {hashed_password_base64}")
        salt_base64 = user_data.get('SALT')
        
        print(f"salt_base64: {salt_base64}")
        userId=user_data.get('EMP_ID')
        flag = user_data.get('FLAG') 

        if hashed_password_base64 is None or salt_base64 is None:
            raise HTTPException(status_code=401, detail="Invalid user data")

        # Decode the base64 encoded salt and hashed_password
        try:
            salt = base64.b64decode(salt_base64 + '==')  # Add padding
            print("salt",salt)
        except Exception as decode_error:

            raise HTTPException(status_code=500, detail="Error decoding salt")

        try:
            hashed_password_bytes = base64.b64decode(hashed_password_base64 + '==')  # Add padding
            print("Hashed Password Bytes", hashed_password_bytes)
        except Exception as decode_error:

            raise HTTPException(status_code=500, detail="Error decoding hashed_password")

        # Hash the input password with the decoded salt
        input_password = password.encode('utf-8')
        print("Input Password", input_password)

        # Debugging output
        hashed_input_password = bcrypt.hashpw(input_password, salt)
        print("Hashed Input Pass",hashed_input_password)

        print(bcrypt.checkpw(input_password, hashed_password_bytes))
        # Compare hashed passwords directly
        if bcrypt.checkpw(input_password, hashed_password_bytes):

            request.session["empId"] = userId
            request.session["userName"] = userName
            login_time = datetime.datetime.now()

            if flag == 1:
                # Redirect to setpassemp.html
                return {"redirect": "/setPassEmp.html"}

            # with get_db_connection() as conn:
            #     cursor = conn.cursor()
            #     cursor.callproc("INSERT_COMPANY_EMP_LOGIN_STATUS", (userId, login_time, None))  
            #     conn.commit()
            return {"message": "Login successful", "redirect": "/empDashboard.html"}
        else:
            print("Login Failed: Incorrect password")
            raise HTTPException(status_code=401, detail="Login failed. Incorrect password")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during login: {str(e)}")
    

from fastapi.responses import HTMLResponse, JSONResponse

@app.post("/set_password_emp", response_class=HTMLResponse)
async def set_password_emp(request: Request):
    userId = request.session.get("empId")
    if not userId:
        return JSONResponse(status_code=401, content="User is not logged in") 
    try:
        userName = request.session.get("userName")
        form_data = await request.form()
        security_question = form_data.get("securityQuestion")
        answer = form_data.get("answer")
        new_password = form_data.get("newPassword")
        confirm_password = form_data.get("confirmPassword")
        user_id = userId  # Get the user ID from session or wherever it's stored
         
        # Validate passwords match
        if new_password != confirm_password:
            return HTMLResponse(content="Passwords do not match")
        
        # Get current datetime
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Assuming the salt and hashed password are generated in the backend
        salt = bcrypt.gensalt()  # Replace with your salt generation logic
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), salt)
        
        salt_base64 = base64.b64encode(salt).decode('utf-8')
        hashed_password_base64 = base64.b64encode(hashed_password).decode('utf-8')

        # Call the stored procedure to update the password
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.callproc(
                "IST_UPDATE_PASS_COMP_EMP",
                (userName, security_question, answer, '0', hashed_password_base64, salt_base64, current_datetime)
            )
            conn.commit()
        
        return HTMLResponse(content="Password updated successfully")
    
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        print(error_message)  # Add this line for debugging
        return HTMLResponse(content=error_message)




    
#===============================================================================================

@app.post("/cemp_reset_password")
async def cemp_reset_password(request: Request):
    userId = request.session.get("userId")
    if not userId:
        return JSONResponse(status_code=401, content="User is not logged in")

    try:
        # Parse the form data
        form_data = await request.json()

        password = form_data.get("oldPassword")

        # Get the current date and time
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Fetch old hashed password from the database for the provided admin ID (userId)
        aws_api_url = f"https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Company_Employee/Company_Employee_Login?userId={userId}"
        response = requests.get(aws_api_url)
        
        if response.status_code != 200:

            raise HTTPException(status_code=401, detail="Old Password Doesn't match")

        old_hashed_password = response.json()
        hashed_password_base64 = old_hashed_password.get('PASSWORD')
        salt_base64 = old_hashed_password.get('SALT')

        if hashed_password_base64 is None or salt_base64 is None:
            raise HTTPException(status_code=401, detail="Invalid user data")

        # Decode the base64 encoded salt and hashed_password
        try:
            salt = base64.b64decode(salt_base64 + '==')  # Add padding
        except Exception as decode_error:
            raise HTTPException(status_code=500, detail="Error decoding salt")

        try:
            hashed_password_bytes = base64.b64decode(hashed_password_base64 + '==')  # Add padding
        except Exception as decode_error:
            raise HTTPException(status_code=500, detail="Error decoding hashed_password")

        # Hash the input password with the decoded salt
        input_password = password.encode('utf-8')

        # Debugging output
        hashed_input_password = bcrypt.hashpw(input_password, salt)

        # Compare hashed passwords directly
        # Compare hashed passwords directly
        if bcrypt.checkpw(input_password, hashed_password_bytes):

            E_ID = userId
            PASS = form_data.get("cPassword")
            L_DATE = current_datetime
            SALT = bcrypt.gensalt()
            print("New salt", SALT)
            hashed_password = bcrypt.hashpw(PASS.encode('utf-8'), SALT)
            print("New hashed pass", hashed_password)
            salt_base64 = base64.b64encode(SALT).decode('utf-8')
            print("New_Salt_base64",salt_base64)
            hashed_password_base64 = base64.b64encode(hashed_password).decode('utf-8')
            print("New_hashed_passoword", hashed_password_base64)
            aws_api_url = f"https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Company_Employee/Cemp_Reset_Password"
            
            request_body = {
                "E_ID" : E_ID,
                "L_DATE" : L_DATE,
                "hashed_password" : hashed_password_base64,
                "salt" : salt_base64
            }

            
            response = requests.post(aws_api_url, json=request_body)
        
            user_data = response.json()

            A_ID = user_data.get('A_ID')
            if response.status_code == 200:
                return {"message": f"{response.text}"}
            else:
                
                return {"error": f"HTTP Error: {response.status_code}", "message": f"HTTP Error: {response.text}"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during login: {str(e)}")


#===============================================================================================

# Start New Application

@app.post("/start_application")
async def start_application(request: Request):
    userId = request.session.get("userId")
    if not userId:
        return JSONResponse(status_code=401, content="User is not logged in")
    try:
        # Parse the form data
        form_data = await request.json()

        # Get the current date and time
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Use the form data to call the stored procedure for business entity applicants
        APPLICATION_NAME = form_data.get("borrowerName")
        AMOUNT_REQUESTED = form_data.get("amountRequested")
        DATE_SUBMITTED   = current_datetime
        STATUS           = "Started"
        created_by       = userId
        CREATED_BY_COMP  = form_data.get("CompId")
        aws_api_url = (
            "https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Loan_Application_Form/Start_Application"
        )
        request_body = {
            "APPLICATION_NAME" : APPLICATION_NAME,
            "AMOUNT_REQUESTED" : AMOUNT_REQUESTED,
            "DATE_SUBMITTED" : DATE_SUBMITTED,
            "STATUS" : STATUS,
            "created_by" : created_by,
            "CREATED_BY_COMP" : CREATED_BY_COMP
        }
        
        response = requests.post(aws_api_url, json=request_body)
    
        if response.status_code == 200:
            return {"message": f"{response.text}"}
        else:
            return {"error": f"HTTP Error: {response.status_code}", "message": f"HTTP Error: {response.text}"}

    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}


# @app.post("/admin_reset_password")
# async def start_application(request: Request):
#     userId = request.session.get("userId")
#     if not userId:
#         return JSONResponse(status_code=401, content="User is not logged in")
#     try:
#         # Parse the form data
#         form_data = await request.json()
#      

#         # Get the current date and time
#         current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#         # Use the form data to call the stored procedure for business entity applicants
#         with get_db_connection() as conn:
#             with conn.cursor() as cursor: 
#                 A_ID=   form_data.get("user_id")
#                 print(f"userid: {A_ID}")
#                 PASSWORD = form_data.get("cPassword")
#                 LAST_UPDATE_DATE=current_datetime

#                 cursor.callproc("UPDATE_PASSWORD", (A_ID,PASSWORD ,LAST_UPDATE_DATE))

#                 conn.commit()
#             return {"message": "Password Updated Successfully"}

#     except Exception as e:
#         return {"error": f"An error occurred: {str(e)}"}
    
#-------------------------------------------------------------------
# @app.post("/cadmin_reset_password")
# async def cadmin_reset_password(request: Request):
#     userId = request.session.get("userId")
#     if not userId:
#         return JSONResponse(status_code=401, content="User is not logged in")

#     try:
#         # Parse the form data
#         form_data = await request.json()
#      

#         password = form_data.get("oldPassword")

#         # Get the current date and time
#         current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#         # Fetch old hashed password from the database for the provided admin ID (userId)
#         aws_api_url = f"https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Company/Company_Admin_Login?userId={userId}"
#         response = requests.get(aws_api_url)
        
#         if response.status_code != 200:
#             print("Old Password Doesn't match")
#             raise HTTPException(status_code=401, detail="Old Password Doesn't match")

#         old_hashed_password = response.json()
#         print(f"user_data: {old_hashed_password}")

#         hashed_password_base64 = old_hashed_password.get('PASSWORD')
#         print(f"hashed_password_base64: {hashed_password_base64}")
#         salt_base64 = old_hashed_password.get('SALT')
#         print(f"salt_base64: {salt_base64}")

#         if hashed_password_base64 is None or salt_base64 is None:
#             print("Missing password or salt in user data")
#             raise HTTPException(status_code=401, detail="Invalid user data")

#         # Decode the base64 encoded salt and hashed_password
#         try:
#             salt = base64.b64decode(salt_base64 + '==')  # Add padding
#             print(f"salt: {salt}")
#         except Exception as decode_error:
#             print(f"Error decoding salt: {decode_error}")
#             raise HTTPException(status_code=500, detail="Error decoding salt")

#         try:
#             hashed_password_bytes = base64.b64decode(hashed_password_base64 + '==')  # Add padding
#             print(f"hashed_password_bytes: {hashed_password_bytes}")
#         except Exception as decode_error:
#             print(f"Error decoding hashed_password: {decode_error}")
#             raise HTTPException(status_code=500, detail="Error decoding hashed_password")

#         # Hash the input password with the decoded salt
#         input_password = password.encode('utf-8')
#         print(f"input_password: {input_password}")

#         # Debugging output
#         hashed_input_password = bcrypt.hashpw(input_password, salt)
#         print(f"hashed_input_password: {hashed_input_password}")
#         print(f"stored_hashed_password: {hashed_password_bytes}")

#         # Compare hashed passwords directly
#         if bcrypt.checkpw(input_password, hashed_password_bytes):
#             A_ID = userId
#             PASS = form_data.get("cPassword")
#             L_DATE = current_datetime
#             SALT = bcrypt.gensalt()
#             print("New salt", SALT)
#             hashed_password = bcrypt.hashpw(PASS.encode('utf-8'), SALT)
#             print("New hashed pass", hashed_password)
#             salt_base64 = base64.b64encode(SALT).decode('utf-8')
#             print("New_Salt_base64",salt_base64)
#             hashed_password_base64 = base64.b64encode(hashed_password).decode('utf-8')
#             print("New_hashed_passoword", hashed_password_base64)
#             aws_api_url = f"https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Company/CAdmin_Reset_Password"
            
#             request_body = {
#                 "A_ID" : A_ID,
#                 "L_DATE" : L_DATE,
#                 "hashed_password" : hashed_password_base64,
#                 "salt" : salt_base64
#             }

            
#             response = requests.post(aws_api_url, json=request_body)
        
#             user_data = response.json()
#             print(f"user_data: {user_data}")

#             A_ID = user_data.get('A_ID')
#             print(f"A_ID:{A_ID}")
#             if response.status_code == 200:
#                 print(f"{response.text}")
#              #   send_email_to_company(email, company_name, CADMIN_ID, password) 
#                 return {"message": f"{response.text}"}
#             else:
#                 
#                 return {"error": f"HTTP Error: {response.status_code}", "message": f"HTTP Error: {response.text}"}
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"An error occurred during login: {str(e)}")

        
        # Check if the old password matches the hashed password stored in the database

#=========================================================================================================================
# EXISTING APPLICATION

@app.get("/get_existing_applications", response_class=JSONResponse)
async def get_existing_applications(request: Request):
    userId = request.session.get("empId")
    if not userId:
        return JSONResponse(status_code=401, content="User is not logged in")   
    try:
        # Make an HTTP GET request to the API Gateway endpoint
        aws_api_url = f"https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Loan_Application_Form/Existing_Applications"
        response = requests.get(aws_api_url)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            error_message = f"Failed to fetch data. Status code: {response.status_code}"
            return JSONResponse(status_code=500, content={"error": error_message})

    except Exception as e:
        error_message = f"An error occurred while fetching data: {str(e)}"
        return JSONResponse(status_code=500, content={"error": error_message})
    
#=========================================================================================================================

# Endpoint to store loan ID in session from JSON payload
@app.post("/store_loan_id")
async def store_loan_id(request: Request):
    try:
        loan_data = await request.json()
        loan_id = loan_data.get("loan_id")

        if loan_id is None:
            raise HTTPException(status_code=400, detail="Loan ID is missing in the request body")

        # Store loan_id in session or perform actions with it
        request.session["selectedLoanId"] = loan_id
        return {"message": "Loan ID stored in session"}
    except Exception as e:
        return {"error": f"Failed to store loan ID: {str(e)}"}

# EXISTING BORROWER    

@app.get("/get_existing_borrowers", response_class=JSONResponse)
async def get_existing_borrowers(request: Request):
    userId = request.session.get("userId")
    if not userId:
        return JSONResponse(status_code=401, content="User is not logged in")   
    
    selected_loan_id = request.session.get("selectedLoanId")
    if selected_loan_id is None:
        return JSONResponse(status_code=404, content={"error": "Loan ID not found in session"})
    try:

        ID = selected_loan_id
        aws_api_url = f"https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Loan_Application_Form/Borrower/Existing_Borrowers?ID={ID}"
        response = requests.get(aws_api_url)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            error_message = f"Failed to fetch data. Status code: {response.status_code}"
            return JSONResponse(status_code=500, content={"error": error_message})

    except Exception as e:
        error_message = f"An error occurred while fetching data: {str(e)}"
        return JSONResponse(status_code=500, content={"error": error_message})    

#=========================================================================================================================
# EXISTING LOAN
    
@app.get("/get_existing_loans", response_class=JSONResponse)
async def get_existing_loans(request: Request):
    userId = request.session.get("userId")
    if not userId:
        return JSONResponse(status_code=401, content="User is not logged in")   
    selected_loan_id = request.session.get("selectedLoanId")
    if selected_loan_id is None:
        return JSONResponse(status_code=404, content={"error": "Loan ID not found in session"})
    try:
        ID = selected_loan_id 
        aws_api_url = f"https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Loan_Application_Form/Loans/Existing_Loans?ID={ID}"
        response = requests.get(aws_api_url)

        if response.status_code == 200:
            data = response.json()
            print("existing loan", data)
            return data
        else:
            error_message = f"Failed to fetch data. Status code: {response.status_code}"
            return JSONResponse(status_code=500, content={"error": error_message})

    except Exception as e:
        error_message = f"An error occurred while fetching data: {str(e)}"
        return JSONResponse(status_code=500, content={"error": error_message})
#===============================================================================================================


def additional_info(request_body_AI):
    try:

        aws_api_url_AI = (
            "https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Loan_Application_Form/Borrower/Additional_Info"
        )
        response_AI = requests.post(aws_api_url_AI, json=request_body_AI)

        # Check the response status and return accordingly
        if response_AI.status_code == 200:

            return {"message": "Data successfully submitted to the AWS API Gateway"}
        else:

            return {"error": f"HTTP Error: {response_AI.status_code}"}

    except Exception as e:
        # Handle any exceptions that may occur during the API request

        return "0"
#-------------------------------------------------------------------------------
def generate_a_id():
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Fetch the maximum a_id from both tables
            cursor.execute("CALL FETCHING_MAX_A_ID();")
            result = cursor.fetchone()

            max_a_id = result['A_ID'] if result and 'A_ID' in result else 0

            # If no a_id found, start with 10001
            if max_a_id is None:
                new_a_id = 10001
            else:
                # Increment the max_a_id by 1
                new_a_id = max_a_id + 1

        return new_a_id

    except Exception as e:
        print(f"An error occurred while generating a_id: {str(e)}")
        return None   
    
#-------------------------------------------------------------------------------

@app.post("/submit_individual_borrower")
async def submit_individual_borrower(request: Request):
    userId = request.session.get("userId")
    if not userId:
        return JSONResponse(status_code=401, content="User is not logged in")
    selected_loan_id = request.session.get("selectedLoanId")
    if selected_loan_id is None:
        return JSONResponse(status_code=404, content={"error": "Loan ID not found in session"})
    
    try:
        # Parse the form data
        form_data = await request.json()

        a_Id = generate_a_id()
        if a_Id is None:
            return {"error": "Failed to generate a cumulative a_Id"}

        # Get the current date and time
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        A = form_data.get("applicantType")
        B = form_data.get("applicantIs")
        C = a_Id     
        D = form_data.get("relationshipWithPrimary")
        E = None
        F = selected_loan_id
        G = form_data.get("firstName")
        H = form_data.get("middleName")
        I = form_data.get("lastName")
        J = form_data.get("email")
        K = form_data.get("telephone")
        L = form_data.get("fax")
        M = form_data.get("streetAddress")
        N = form_data.get("city")
        O = form_data.get("state")
        P = form_data.get("zipCode")
        Q = form_data.get("county")
        R = form_data.get("socialSecurity")
        S = form_data.get("dateOfBirth")
        T = form_data.get("maritalStatus")
        U = form_data.get("yearBeginningFarming")
        V = form_data.get("yearAtCurrentAddress")
        W = form_data.get("citizenship")
        X = userId 
        Y = current_datetime
        Z = current_datetime

        # Additional application information
        AC = form_data.get("additionalComments")
        GF = form_data.get("grossFarmIncome")
        NF= form_data.get("netFarmIncome")
        NNF= form_data.get("netNonFarmIncome")
        D1 = form_data.get("source1")
        A1 = form_data.get("income1")
        D2 = form_data.get("source2")
        A2 = form_data.get("income2")
        D3 = form_data.get("source3")
        A3 = form_data.get("income3")
        D4 = form_data.get("source4")
        A4 = form_data.get("income4")
        D5 = form_data.get("source5")
        A5 = form_data.get("income5")
        TA = form_data.get("totalAssets")
        TL = form_data.get("totalLiabilities")

        aws_api_url_BI = (
            "https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Loan_Application_Form/Borrower/Submit_Individual_Borrower"
        )
        # Prepare the request body
        request_body_BI = {
            "A": A,
            "B": B,
            "C": C,
            "D": D,
            "E": E,
            "F": F,
            "G": G,
            "H": H,
            "I": I,
            "J": J,
            "K": K,
            "L": L,
            "M": M,
            "N": N,
            "O": O,
            "P": P,
            "Q": Q,
            "R": R,
            "S": S,
            "T": T,
            "U": U,
            "V": V,
            "W": W,
            "X": X,
            "Y": Y,
            "Z": Z
        }

        request_body_AI = {
            "C"  : C,
            "F"  : F,
            "AC" : AC,
            "GF" : GF,
            "NF" : NF,
            "NNF": NNF,
            "D1" : D1,
            "A1" : A1,
            "D2" : D2,
            "A2" : A2,
            "D3" : D3,
            "A3" : A3,
            "D4" : D4,
            "A4" : A4,
            "D5" : D5,
            "A5" : A5,
            "TA" : TA,
            "TL" : TL,
            "X"  : X,
            "Y"  : Y,
            "Z"  : Z
        }

        response_BI = requests.post(aws_api_url_BI, json=request_body_BI)
        additional_info(request_body_AI)

        # Check the response status and return accordingly
        if response_BI.status_code == 200:
            
            return {"message": "Data successfully submitted to the AWS API Gateway"}
        else:
            return {"error": f"HTTP Error: {response_BI.status_code}"}

    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}

@app.post("/submit_business_entity_borrower")
async def submit_business_entity_borrower(request: Request):
    userId = request.session.get("userId")
    if not userId:
        return JSONResponse(status_code=401, content="User is not logged in")
    selected_loan_id = request.session.get("selectedLoanId")
    if selected_loan_id is None:
        return JSONResponse(status_code=404, content={"error": "Loan ID not found in session"})
    try:
        # Parse the form data
        form_data = await request.json()

        a_Id = generate_a_id()
        if a_Id is None:
            return {"error": "Failed to generate a cumulative a_Id"}
        # Get the current date and time
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Use the form data to call the stored procedure for business entity applicants

        A = form_data.get("applicantType")
        B = form_data.get("applicantIs")
        C = a_Id
        D = form_data.get("relationshipWithPrimary")
        E = None
        F = selected_loan_id
        G = form_data.get("businessName")
        H = form_data.get("taxId")
        I = form_data.get("email")
        J = form_data.get("businessTelephone")
        L = form_data.get("businessFax")
        M = form_data.get("streetAddress")
        N = form_data.get("city")
        O = form_data.get("state")
        P = form_data.get("zipCode")
        Q = form_data.get("county")
        R = form_data.get("contactNameDetails")
        S = form_data.get("businessDescription")
        T = form_data.get("principalOfficer")
        U = form_data.get("homeAddress")
        V = form_data.get("ownedPercentage")
        W = form_data.get("ownershipTitle")
        X = userId  # Modify as needed
        Y = current_datetime
        Z = current_datetime

        # Additional application information
        AC = form_data.get("additionalComments")
        GF = form_data.get("grossFarmIncome")
        NF= form_data.get("netFarmIncome")
        NNF= form_data.get("netNonFarmIncome")
        D1 = form_data.get("source1")
        A1 = form_data.get("income1")
        D2 = form_data.get("source2")
        A2 = form_data.get("income2")
        D3 = form_data.get("source3")
        A3 = form_data.get("income3")
        D4 = form_data.get("source4")
        A4 = form_data.get("income4")
        D5 = form_data.get("source5")
        A5 = form_data.get("income5")
        TA = form_data.get("totalAssets")
        TL = form_data.get("totalLiabilities")

        aws_api_url_BI = (
            "https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Loan_Application_Form/Borrower/submit_BusinessEntity_Borrower"
        )

        # Prepare the request body
        request_body_BI = {
            "A": A,
            "B": B,
            "C": C,
            "D": D,
            "E": E,
            "F": F,
            "G": G,
            "H": H,
            "I": I,
            "J": J,
            "L": L,
            "M": M,
            "N": N,
            "O": O,
            "P": P,
            "Q": Q,
            "R": R,
            "S": S,
            "T": T,
            "U": U,
            "V": V,
            "W": W,
            "X": X,
            "Y": Y,
            "Z": Z
        }

        request_body_AI = {
            "C"  : C,
            "F"  : F,
            "AC" : AC,
            "GF" : GF,
            "NF" : NF,
            "NNF": NNF,
            "D1" : D1,
            "A1" : A1,
            "D2" : D2,
            "A2" : A2,
            "D3" : D3,
            "A3" : A3,
            "D4" : D4,
            "A4" : A4,
            "D5" : D5,
            "A5" : A5,
            "TA" : TA,
            "TL" : TL,
            "X"  : X,
            "Y"  : Y,
            "Z"  : Z
        }

        response = requests.post(aws_api_url_BI, json=request_body_BI)
        additional_info(request_body_AI)

        # Check the response status and return accordingly
        if response.status_code == 200:
            
            return {"message": "Data successfully submitted to the AWS API Gateway"}
        else:
            
            return {"error": f"HTTP Error: {response.status_code}"}

    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}    

#===============================================================================================================================
#LOANS POPUP PAGE

@app.post("/submit_loan")
async def submit_loan(request: Request):
    userId = request.session.get("userId")
    if not userId:
        return JSONResponse(status_code=401, content="User is not logged in")
    selected_loan_id = request.session.get("selectedLoanId")
    if selected_loan_id is None:
        return JSONResponse(status_code=404, content={"error": "Loan ID not found in session"})
    try:
        # Parse the form data
        form_data = await request.json()
 
        # Get the current date and time
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
 
        L_ID = selected_loan_id
        A = form_data.get("amountRequested")
        B = None
        C = form_data.get("loanToValue")
        D = form_data.get("closeDate")
        E = form_data.get("paymentFrequency")
        F = form_data.get("loanPurpose")
        G = form_data.get("otherPurpose")
        H = form_data.get("sourceOfFunds1")
        I = form_data.get("sourceOffundsAmount1")
        J = form_data.get("useOfFunds1")
        K = form_data.get("useOfFundsAmount1")
        L = form_data.get("sourceOfFunds2")
        M = form_data.get("sourceOffundsAmount2")
        N = form_data.get("useOfFunds2")
        O = form_data.get("useOfFundsAmount2")
        P = form_data.get("sourceOfFunds3")
        Q = form_data.get("sourceOffundsAmount3")
        R = form_data.get("useOfFunds3")
        S = form_data.get("useOfFundsAmount3")
        T = form_data.get("sourceOfFunds4")
        U = form_data.get("sourceOffundsAmount4")
        V = form_data.get("useOfFunds4")
        W = form_data.get("useOfFundsAmount4")
        Z = form_data.get("loanProduct")
        X = form_data.get("yearsAmortized")
        CREATED_BY = userId
        CREATED_DATE = current_datetime
        UPDATED_DATE = current_datetime
 
        aws_api_url = (
            "https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Loan_Application_Form/Loans/submit_loan"
        )
 
        # Prepare the request body
        request_body = {
            "L_ID" : L_ID,
            "A" : A,
            "B" : B,
            "C" : C,
            "D" : D,
            "E" : E,
            "F" : F,
            "G" : G,
            "H" : H,
            "I" : I,
            "J" : J,
            "K" : K,
            "L" : L,
            "M" : M,
            "N" : N,
            "O" : O,
            "P" : P,
            "Q" : Q,
            "R" : R,
            "S" : S,
            "T" : T,
            "U" : U,
            "V" : V,
            "W" : W,
            "Z" : Z,
            "X" : X,
            "CREATED_BY" : CREATED_BY,
            "CREATED_DATE" : CREATED_DATE,
            "UPDATED_DATE" : UPDATED_DATE
        }
 
        response = requests.post(aws_api_url, json=request_body)
   
        if response.status_code == 200:
            print("Loan Information form data successfully stored in the database")
            return {"message": "Loan Information form data successfully stored in the database"}
        else:
            
            return {"error": f"HTTP Error: {response.status_code}"}
 
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    
#=================================================================================================================================
# EXISTING Collateral   

@app.get("/get_existing_collaterals", response_class=JSONResponse)
async def get_existing_collaterals(request: Request):
    userId = request.session.get("userId")
    if not userId:
        return JSONResponse(status_code=401, content="User is not logged in")
    selected_loan_id = request.session.get("selectedLoanId")
    if selected_loan_id is None:
        return JSONResponse(status_code=404, content={"error": "Loan ID not found in session"})
    
    try:
        ID = selected_loan_id  # Hardcoded value for testing
        aws_api_url = f"https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Loan_Application_Form/Collaterals/existing_collateral?ID={ID}"
        response = requests.get(aws_api_url)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            error_message = f"Failed to fetch data. Status code: {response.status_code}"
            return JSONResponse(status_code=500, content={"error": error_message})

    except Exception as e:
        error_message = f"An error occurred while fetching data: {str(e)}"
        return JSONResponse(status_code=500, content={"error": error_message})
    
#-------------------------------------------------------------------------------------------------------
# COLLATERAL POPUP 

@app.post("/submit_collateral")
async def submit_collateral(request: Request):
    userId = request.session.get("userId")
    if not userId:
        return JSONResponse(status_code=401, content="User is not logged in")
    selected_loan_id = request.session.get("selectedLoanId")
    if selected_loan_id is None:
        return JSONResponse(status_code=404, content={"error": "Loan ID not found in session"})
    try:
        # Parse the form data
        form_data = await request.json()

        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        A = None
        B = selected_loan_id
        PS = form_data.get("propertyState")
        PC = form_data.get("propertyCounty")
        SEC = form_data.get("section")
        TWN = form_data.get("township")
        RNG = form_data.get("range")
        ALD = form_data.get("abriviatedlegaldescription")
        LV = form_data.get("landValue")
        RV = form_data.get("residenceValue")
        IV = form_data.get("improvementsValue")
        PV = form_data.get("plantingsValue")
        TV = form_data.get("totalValue")
        PL = form_data.get("propertyLeases")
        RT = form_data.get("remainingTerm")
        PA = form_data.get("purchaseAgreements")
        ME = form_data.get("manureEasements")
        WL = form_data.get("windLeases")
        CT = form_data.get("cellTower")
        OMGL = form_data.get("oilMineralGasLeases")
        OL = form_data.get("otherLeases")
        OLD = form_data.get("otherLeasesDescription")
        OWN = form_data.get("ownership")
        CR = form_data.get("cashRent")
        RET = form_data.get("realEstateTaxes")  
        PIA = form_data.get("pastureIrrigatedAcres")
        PIVPA = form_data.get("pastureIrrigatedValuePerAcre")
        PNA = form_data.get("pastureNonIrrigatedAcres")
        PNVPA = form_data.get("pastureNonirrigatedValuePerAcre")
        CIA = form_data.get("crpIrrigatedAcres")
        CIVPA = form_data.get("crpIrrigatedValuePerAcre")
        CNA = form_data.get("crpNonIrrigatedAcres")
        CNVPA = form_data.get("crpNonirrigatedValuePerAcre")
        WIA = form_data.get("woodedIrrigatedAcres")
        WIVPA = form_data.get("woodedIrrigatedValuePerAcre")
        WNA = form_data.get("woodedNonIrrigatedAcres")
        WNVPA = form_data.get("woodedNonirrigatedValuePerAcre")
        PPIA = form_data.get("plantingsIrrigatedAcres")
        PIV = form_data.get("plantingsIrrigatedValuePerAcre")
        PPNA = form_data.get("plantingsNonIrrigatedAcres")
        PNV = form_data.get("plantingsNonirrigatedValuePerAcre")
        TLIA = form_data.get("timberlandIrrigatedAcres")
        TIVPA = form_data.get("timberlandIrrigatedValuePerAcre")
        TLNA = form_data.get("timberlandNonIrrigatedAcres")
        TNVPA = form_data.get("timberlandNonirrigatedValuePerAcre")
        OIA = form_data.get("othersIrrigatedAcres")
        OIVPA = form_data.get("othersIrrigatedValuePerAcre")
        ONA = form_data.get("othersNonIrrigatedAcres")
        ONVPA = form_data.get("othersNonirrigatedValuePerAcre")
        TIA = form_data.get("totalIrrigatedAcres")
        TNA = form_data.get("totalNonIrrigatedAcres")
        TA = form_data.get("totalAcres")
        IMP = form_data.get("improvements")
        PP = form_data.get("permanentplantings")
        IR = form_data.get("irepayment")
        PPR = form_data.get("pprepayment")
        SMW = form_data.get("sixmonthwork")
        RES = form_data.get("residence")
        DESC = form_data.get("descriptiont")
        WR = form_data.get("waterRights")
        WRD = form_data.get("waterRightsDescription")
        EH = form_data.get("environmentalHazard")
        EHD = form_data.get("environmentalHazardDescription")
        X = userId
        Y = current_datetime
        Z = current_datetime

        aws_api_url = (
            "https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Loan_Application_Form/Collaterals/Submit_Collaterals"
        )

        # Prepare the request body
        request_body = {
        "A" : A,
        "B" : B,
        "PS" : PS,
        "PC" : PC,
        "SEC" : SEC,
        "TWN" : TWN,
        "RNG" : RNG,
        "ALD" : ALD,
        "LV" : LV,
        "RV" : RV,
        "IV" : IV,
        "PV" : PV,
        "TV" : TV,
        "PL" : PL,
        "RT" : RT,
        "PA" : PA,
        "ME" : ME,
        "WL" : WL,
        "CT" : CT,
        "OMGL" : OMGL,
        "OL" : OL,
        "OLD" : OLD,
        "OWN" : OWN,
        "CR" : CR,
        "RET" : RET,  
        "PIA" : PIA,
        "PIVPA" : PIVPA,
        "PNA" : PNA,
        "PNVPA" : PNVPA,
        "CIA" : CIA,
        "CIVPA" : CIVPA,
        "CNA" : CNA,
        "CNVPA" : CNVPA,
        "WIA" : WIA,
        "WIVPA" : WIVPA,
        "WNA" : WNA,
        "WNVPA" : WNVPA,
        "PPIA" : PPIA,
        "PIV" : PIV,
        "PPNA" : PPNA,
        "PNV" : PNV,
        "TLIA" : TLIA,
        "TIVPA" : TIVPA,
        "TLNA" : TLNA,
        "TNVPA" : TNVPA,
        "OIA" : OIA,
        "OIVPA" : OIVPA,
        "ONA" : ONA,
        "ONVPA" : ONVPA,
        "TIA" : TIA,
        "TNA" : TNA,
        "TA" : TA,
        "IMP" : IMP,
        "PP" : PP,
        "IR" : IR,
        "PPR" : PPR,
        "SMW" : SMW,
        "RES" : RES,
        "DESC" : DESC,
        "WR" : WR,
        "WRD" : WRD,
        "EH" : EH,
        "EHD" : EHD,
        "X" : X,  
        "Y" : Y,
        "Z" : Z
        }

        response = requests.post(aws_api_url, json=request_body)
    
        if response.status_code == 200:

            return {"message": "Collateral Information form data successfully stored in the database"}
        else:
            
            return {"error": f"HTTP Error: {response.status_code}"}

    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}

#=====================================================================================
@app.get("/get_existing_otherinfo", response_class=JSONResponse)
async def get_existing_otherinfo(request: Request):
    userId = request.session.get("userId")
    if not userId:
        return JSONResponse(status_code=401, content="User is not logged in")
    selected_loan_id = request.session.get("selectedLoanId")
    if selected_loan_id is None:
        return JSONResponse(status_code=404, content={"error": "Loan ID not found in session"})
    try:
        ID = selected_loan_id  # Hardcoded value for testing
        aws_api_url = f"https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Loan_Application_Form/Other_Info/Existing_Otherinfo?loan_id={ID}"
        response = requests.get(aws_api_url)
 
        if response.status_code == 200:
            data = response.json()

            return data
        else:
            error_message = f"Failed to fetch data. Status code: {response.status_code}"
            return JSONResponse(status_code=500, content={"error": error_message})
 
    except Exception as e:
        error_message = f"An error occurred while fetching data: {str(e)}"
        return JSONResponse(status_code=500, content={"error": error_message})

#-------------------------------------------------------------------------------------------------------
# OTHER INFO TAB

@app.post("/submit_otherInfo")
async def submit_otherInfo(request: Request):
    userId = request.session.get("userId")
    if not userId:
        return JSONResponse(status_code=401, content="User is not logged in")
    selected_loan_id = request.session.get("selectedLoanId")
    if selected_loan_id is None:
        return JSONResponse(status_code=404, content={"error": "Loan ID not found in session"})
    try:
        # Parse the form data
        form_data = await request.json()

        # Get the current date and time
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Use the form data to call the stored procedure for business entity applicants
        A_ID    = None
        PA_ID   = None
        LOAN_ID = selected_loan_id
        D = form_data.get("judgments")
        E = form_data.get("bankruptcy")
        F = form_data.get("lawsuits")
        G = form_data.get("pastDue")
        H = form_data.get("foreclosure")
        I = form_data.get("existingClient")
        J = form_data.get("totalAcresOwned")
        K = form_data.get("totalAcresRented")
        L = form_data.get("assetsPledged")
        M = form_data.get("contingentLiabilities")
        N = form_data.get("obligatedToPay")
        O = form_data.get("details")
        P = form_data.get("interestInCompanies")
        Q = form_data.get("residenceOnCollateral")
        X = userId  
        Y = current_datetime
        Z = current_datetime

        aws_api_url = (
            "https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Loan_Application_Form/Other_Info/submit_OtherInfo"
        )

        # Prepare the request body
        request_body = {
            "A": A_ID ,
            "B": PA_ID,
            "C": LOAN_ID,
            "D": D,
            "E": E,
            "F": F,
            "G": G,
            "H": H,
            "I": I,
            "J": J,
            "K": K,
            "L": L,
            "M": M,
            "N": N,
            "O": O,
            "P": P,
            "Q": Q,
            "X": X,
            "Y": Y,
            "Z": Z
        }

        response = requests.post(aws_api_url, json=request_body)
    
        if response.status_code == 200:
            return {"message": "OTHER INFO data successfully stored in the database"}
        else:
            
            return {"error": f"HTTP Error: {response.status_code}"}

    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}

AWS_ACCESS_KEY_ID='ASIASWWHWDG7J4CXLJPE'
AWS_SECRET_ACCESS_KEY='Kzw8oWM6Lw5QQhsm6e5ZNnCXWdYoYa6VTXqRlIBF'
AWS_SESSION_TOKEN='IQoJb3JpZ2luX2VjEGkaCXVzLWVhc3QtMSJHMEUCICHF3OEp9ML9wRxu6Jh0o/xHsTaS7BSTId0We5H+ozFoAiEA8CqaT4o9m9X+tVlTvbrwCQUr4cx7Gtm3+TFIO0b92r4q+AIIERAAGgwxODYxNzYxMTcxODIiDML/4srayBseoZ3ZEirVAuxShbV7cfayVg2ib4g7udORBNvPqZwJ1efybf39+PEj3V6TdLSPCkHwjPmmyBg0g3Lm7QY7a1Hl9UrJuDewJ5UovU3lPlsH1nlVMPR+AxbHNvor9CLNyIBPN7QCinWhG3B8GukJmQ5IvmGOj+UiRvXLbzm+ZraGIPzEIt5VYY+BntfLCgFKCj5WKMwP1CC95q+pM9RPlEr0pzIig8C4tn/4uNDUJgTCbfwrmr3GI1q/Jb9oJY4DC4QAPINK5jzcfU9ro99f+OoFxxBUOl3KgMX/bJa1rlWBMCvqGE4EZcdULJ3eemzfvYKbENMlGZ/8GpaKl5WIyVdYyy/XEax3SQLiufHjl1MF84m+ZdJ1RDFWy7ug3z7/fb+ZVEHhLDKp30SZzyV1Q5uCwk8SAuhUcUA1KSs8h2nQUijqFsgjj6fH4Ys7htVz8ajdhjVpq3zIS0wSstHHMJii+awGOqcB6dvjb7tSajdLg0woyT6RuU+wEnXMuHu+QnjOUvdbRL76TyvIFK1fTrE5qvfeLZvRvoGtSDdraS7SxbgRVun2mhdc/StGmR/IKVei+amRyho/Sp/l3sjK+RUxOlvlGE0h22gb7GGxZtTzg/e+zFIpMWYZsClVrUNw6pkYE2RwaYy7CLxlmWPC6/Vt+C5eaMKxCLFuF2NBnNpbQXPTnnfcT+FSb8+3HM0='


#========================================================================================================

def generate_presigned_url(bucket_name, object_key, expiration=3600):
    s3 = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        aws_session_token=AWS_SESSION_TOKEN if AWS_SESSION_TOKEN else None
    )

    url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket_name, 'Key': object_key},
        ExpiresIn=expiration
    )

    return url

@app.post("/uploadfile")
async def upload_file(file: UploadFile, request: Request):
    userId = request.session.get("userId")
    if not userId:
        return JSONResponse(status_code=401, content="User is not logged in")
    # Initialize AWS S3 client
    selected_loan_id = request.session.get("selectedLoanId")
    if selected_loan_id is None:
        return JSONResponse(status_code=404, content={"error": "Loan ID not found in session"})
    
    try:
        s3 = boto3.client(
            's3',
            region_name='us-east-1',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            aws_session_token=AWS_SESSION_TOKEN
        )

        # Upload the file to S3
        # Generate a new filename with the desired extension (e.g., pdf)
        new_filename = f"{file.filename}.pdf"
        # Upload the file to S3 with the new filename
        s3.upload_fileobj(file.file, 'gofin-loan-application-upload-document', new_filename)


        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Extract the selected document type from the form data
        form_data = await request.form()
        doc_type = form_data.get("documentType")


        emp_id = userId

        cursor = conn.cursor()
        cursor.execute(f"SELECT COMP_ID FROM COMPANY_EMP WHERE E_ID = {emp_id}")
        COMP_ID=cursor.fetchone()

        a_id = 11
        loan_id = selected_loan_id
        doc_name = form_data.get("doc_name")
        file_desc = form_data.get("file_Desc")
        doc_date = form_data.get("doc_date")
        file_name = form_data.get("file_name")
        
        version = 1.1
        uploaded_by = emp_id

        # Call the stored procedure to insert data into the database
        aws_api_url = (
            "https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Loan_Application_Form/Document/submit_Document_Details"
        )

        # Prepare the request body
        request_body = {
        "emp_id": emp_id,
        "company_id": COMP_ID,
        "a_id": a_id,
        "loan_id": loan_id,
        "doc_name":doc_name,
        "file_name":file_name,
        "doc_type":doc_type, 
        "file_desc":file_desc,
        "doc_date":doc_date,
        "version":version,
        "uploaded_by":uploaded_by,
        "uploaded_Date":current_datetime
        }
        response = requests.post(aws_api_url, json=request_body)
    
        if response.status_code == 200:
            return {"message": f"{response.text}"}
        else:
            
            return {"error": f"HTTP Error: {response.status_code}", "message": f"HTTP Error: {response.text}"}

    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}

   
@app.get("/get_Doc_url")
def get_template_url(file_name: str = Query(..., title="File Name")):
    S3_BUCKET_NAME = "gofin-loan-application-upload-document"

    try:
        object_key = f"{file_name}.pdf"
        Doc_url = generate_presigned_url(S3_BUCKET_NAME, object_key)
        return {"Doc_url": Doc_url}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}


@app.get("/get_previous_documents", response_class=JSONResponse)
async def get_existing_borrowers(request: Request):

    userId = request.session.get("userId")
    if not userId:
        return JSONResponse(status_code=401, content="User is not logged in")
    loan_id = request.session.get("selectedLoanId")
    if loan_id is None:
        return JSONResponse(status_code=404, content={"error": "Loan ID not found in session"})

    try:
        EMP_ID = userId  # Hardcoded value for testing
        
        Loan_ID = loan_id  # Correct the method to get query parameters

        aws_api_url = f"https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Loan_Application_Form/Document/existing_doc_info?EMP_ID={EMP_ID}&Loan_ID={Loan_ID}"


        response = requests.get(aws_api_url)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            error_message = f"Failed to fetch data. Status code: {response.status_code}"
            return JSONResponse(status_code=500, content={"error": error_message})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "An error occurred while fetching data."})
#===================================================================================================================================================================================================   
# Configure logging
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

@app.delete("/delete_Doc")
def delete_document(file_name: str = Query(..., title="File Name")):
    try:
        S3_BUCKET_NAME = "gofin-loan-application-upload-document"
        object_key = f"{file_name}.pdf"
        s3 = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            aws_session_token=AWS_SESSION_TOKEN if AWS_SESSION_TOKEN else None
        )
    
        response = s3.delete_object(Bucket=S3_BUCKET_NAME, Key=object_key)

        # Check if S3 deletion was successful
        if response['ResponseMetadata']['HTTPStatusCode'] != 204:
            raise HTTPException(status_code=response['ResponseMetadata']['HTTPStatusCode'], detail=f"S3 Error: {response}")

        # Delete file information from the database
        aws_api_url = (
            "https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Loan_Application_Form/Document/delete_doc_info"
        )
        request_body = {
            "file_name": file_name
        }
        db_response = requests.post(aws_api_url, json=request_body)

        # Check if database deletion was successful
        if db_response.status_code != 200:
            raise HTTPException(status_code=db_response.status_code, detail=f"Database Error: {db_response.text}")

        return JSONResponse(content={"message": f"File {file_name} deleted successfully"})

    except ClientError as e:
        # print("Error deleting object:", str(e))
        raise HTTPException(status_code=500, detail=f"S3 Error: {e}")
    except Exception as e:
        # print("Unexpected error:", str(e))
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


#-===================================================================================================

# Assuming similar route structures for individual and business data retrieval

@app.get("/individual_preview_data")
async def get_preview_data(request: Request):
    loan_id = request.session.get("selectedLoanId")
    if loan_id is None:
        return JSONResponse(status_code=404, content={"error": "Loan ID not found in session"})
    
    aws_api_url = f"https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Loan_Application_Form/Borrower/preview_individual_data?loan_id={loan_id}"
    response = requests.get(aws_api_url)

    if not response.json() or 'Result' not in response.json():
        # User ID not found or Result key not present
        return JSONResponse(status_code=401, content="Invalid User ID")

    # Extract the 'Result' key from the JSON response
    result = response.json()['Result']

    return result

@app.get("/business_preview_data")
async def get_preview_data(request: Request):
    loan_id = request.session.get("selectedLoanId")
    if loan_id is None:
        return JSONResponse(status_code=404, content={"error": "Loan ID not found in session"})
    
    aws_api_url = f"https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Loan_Application_Form/Borrower/preview_business_data?loan_id={loan_id}"
    response = requests.get(aws_api_url)
    

    if not response.json() or 'Result' not in response.json():
        # User ID not found or Result key not present
        return JSONResponse(status_code=401, content="Invalid User ID")

    # Extract the 'Result' key from the JSON response
    result = response.json()['Result']

    return result


#=======================================================================================================


@app.get("/loan_preview_data")
async def get_loan_preview_data(request: Request):
    loan_id = request.session.get("selectedLoanId")
    if loan_id is None:
        return JSONResponse(status_code=404, content={"error": "Loan ID not found in session"})
    
    aws_api_url = f"https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Loan_Application_Form/Loans/preview_loan_data?loan_id={loan_id}"
    response = requests.get(aws_api_url)

    if not response.json() or 'Result' not in response.json():
        # User ID not found or Result key not present
        return JSONResponse(status_code=401, content="Invalid User ID")

    # Extract the 'Result' key from the JSON response
    result = response.json()['Result']

    return result
#=====================================================================================
@app.get("/collateral_info")
async def get_collateral_info(request: Request):
    loan_id = request.session.get("selectedLoanId")
    if loan_id is None:
        return JSONResponse(status_code=404, content={"error": "Loan ID not found in session"})

    aws_api_url = f"https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Loan_Application_Form/Collaterals/preview_Collateral_Info?loan_id={loan_id}"
    response = requests.get(aws_api_url)
    

    if not response.json() or 'Result' not in response.json():
        # User ID not found or Result key not present
        return JSONResponse(status_code=401, content="Invalid User ID")

    # Extract the 'Result' key from the JSON response
    result = response.json()['Result']

    return result




#============================================================================================================


@app.get("/other_info")
async def get_other_info(request: Request):
    loan_id = request.session.get("selectedLoanId")
    if loan_id is None:
        return JSONResponse(status_code=404, content={"error": "Loan ID not found in session"})
    
    aws_api_url = f"https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Loan_Application_Form/Other_Info/preview_OtherInfo?loan_id={loan_id}"
    response = requests.get(aws_api_url)

    if not response.json() or 'Result' not in response.json():
        # User ID not found or Result key not present
        return JSONResponse(status_code=401, content="Invalid User ID")

    # Extract the 'Result' key from the JSON response
    result = response.json()['Result']

    return result
    
#==============================================================================================
@app.get("/document_upload")
async def get_document_upload(request: Request):
    loan_id = request.session.get("selectedLoanId")
    if loan_id is None:
        return JSONResponse(status_code=404, content={"error": "Loan ID not found in session"})
    
    aws_api_url = f"https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Loan_Application_Form/Document/preview_doc_info?loan_id={loan_id}"
    response = requests.get(aws_api_url)
    
    # print(f"userdata: {response.text}")

    if not response.json() or 'Result' not in response.json():
        return JSONResponse(status_code=401, content="Rsponse not ok!")

    # Extract the 'Result' key from the JSON response
    result = response.json()['Result']

    return result

#==============================================================================================

# Configure logging
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def transpose_excel_data(file):
    # Read Excel file and store each sheet into a dictionary of DataFrames
    excel_data = pd.read_excel(file, sheet_name=None, header=None)
    # print("Transposing Excel data...")
    
    # Extract the specific sheet names
    sheet_names = ["Schedule C","Schedule F","Schedule E","Balance Sheet","Schedule L"]
    column_mappings = {
        "Schedule C": {
            "Name":"NAME",
            "Code":"NAICS",
            "Principal Business":"PRINCIPAL_BUSINESS",
            "Tax Basis":"TAX_BASIS",
            "Year":"YEAR",
            "Status":"STATUS",
            "Business Name": "COMPANY",
            "Gross Receipts":"GROSS_RECEIPTS",
            "Returns & Allowances":"RETURNS_ALLOWANCE",
            "Line 1 - Line 2":"RECEIPTS_RETURNS",
            "Cost of Goods Sold (line 42)":"COST_OF_GOODS_SOLD_line_42",
            "Gross Profit (Line 3 - Line 4)":"GROSS_PROFIT",
            "Other Income":"OTHER_INCOME",
            "Gross Income (Line 5+Line 6)":"GROSS_INCOME",
                        "Advertising":"ADVERTISING",
            "Car and truck expenses (see instructions)":"CAR_TRUCK_EXPENSE",
            "Commissions and fees":"COMMISSIONS_FEES",
            "Contract labor (see instructions )":"CONTRACT_LABOUR",
            "Depletion":"DEPLETION",
            "Depreciation and section 179 expense deduction":"DEPRECIATION_S_179_EXPENSE_DEDUCTION",
            "Employee benefit programs":"EMP_BENEFIT_PROGRAM",
            "Insurance (other than health)":"INSURANCE_other_than_health",
            "Interest_Mortgage (paid to banks, etc.)":"INTEREST_MORTAGE",
            "Interest_Other":"INTEREST_OTHER",
            "Legal and professional services":"LEGAL_PROFESSIONAL_SERVICES",
            "Office expense (see instructions)":"OFFICE_EXPENSE",
            "Pension and profit-sharing plans":"PENSION_PROFIT_SHARING_PLAN",
            "Rent or lease_Vehicles, machinery, and equipment":"RENT_LEASE_VEHICLE_MACHINERY_EQIPMENTS",
            "Rent or lease_Other business property":"RENT_LEASE_OTHER_BUSINESS_PROPERTY",
            "Repairs and maintenance":"REPAIRS_MAINTENANCE",
            "Supplies (not included in Part III)":"SUPPLIES",
            "Taxes and licenses":"TAX_LICENSES",
            "Travel and meals_Travel":"TRAVEL_MEALS_TRAVEL",
            "Travel and meals_Deductible Meals":"TRAVEL_MEALS_DEDUCTIBLE_MEALS",
            "Utilities":"UTILITIES",
            "Wages (less employment credits)":"WAGES",
            "Other expenses Attribute1":"OTHER_EXPENSES_Attribute1",
            "Other expenses Value1":"OTHER_EXPENSES_Value1",
            "Other expenses Attribute2":"OTHER_EXPENSES_Attribute2",
            "Other expenses Value2":"OTHER_EXPENSES_Value2",
            "Other expenses Attribute3":"OTHER_EXPENSES_Attribute3",
            "Other expenses Value3":"OTHER_EXPENSES_Value3",
            "Other expenses Attribute4":"OTHER_EXPENSES_Attribute4",
            "Other expenses Value4":"OTHER_EXPENSES_Value4",
            "Other expenses Attribute5":"OTHER_EXPENSES_Attribute5",
            "Other expenses Value5":"OTHER_EXPENSES_Value5",
            "Other expenses Attribute6":"OTHER_EXPENSES_Attribute6",
            "Other expenses Value6":"OTHER_EXPENSES_Value6",
            "Other expenses Attribute7":"OTHER_EXPENSES_Attribute7",
            "Other expenses Value7":"OTHER_EXPENSES_Value7",
            "Other expenses Attribute8":"OTHER_EXPENSES_Attribute8",
            "Other expenses Value8":"OTHER_EXPENSES_Value8",
            "Other expenses Attribute9":"OTHER_EXPENSES_Attribute9",
            "Other expenses Value9":"OTHER_EXPENSES_Value9",
            "Other expenses Attribute10":"OTHER_EXPENSES_Attribute10",
            "Other expenses Value10":"OTHER_EXPENSES_Value10",
            "Total Other Expenses":"TOTAL_OTHER_EXPENSES",
            "Total expenses (add lines 8 to 27a)":"TOTAL_EXPENSES",
            "Tentative profit or (loss) (Line 7 - Line 28)":"TENTATIVE_PROFIT_LOSS",
            "Expenses for business use of your home":"EXPENSESS_BUSINESS_USE_OF_HOME",
            "Net profit or (loss) (Line 29 - Line 30)":"NET_PROFIT_LOSS",
        },

                    "Schedule F": {
            "Name":"NAME",
            "Code":"NAICS",
            "Principal Business":"PRINCIPAL_BUSINESS",
            "Tax Basis":"TAX_BASIS",
            "Year":"YEAR",
            "Status":"STATUS",
            "Business Name": "COMPANY",
            "Sales of purchased livestock and other resale items":"SALES_PURCHASED_LIVESTOCK_OTHER_RESALE_ITEMS",
            "Cost or other basis of purchased livestock or other items reported on line":"COST_OTHER_BASIS_LIVESTOCK_ITEMS_REPORTED_ON_LINE",
            "Line 1a - Line 1b":"SALES_COST",
            "Sales of livestock, produce, grains, and other products you raised":"SALES_LIVESTOCK_PRODUCE_GRAINS_OTHER_RAISED",
            "Cooperative distributions":"COOPERATIVE_DISTRIBUTIONS",
            "Agricultural program payments":"AGRICULTURAL_PROG_PAYMENTS",
            "Commodity Credit Corporation (CCC) loans reported under election":"CCC_LOANS_REPORTED_UNDER_ELECTION",
            "CCC loans forfeited":"CCC_LOANS_FORFEITED",
            "Crop insurance proceeds and federal crop disaster payments_Amount received":"CROP_INSURANCE_AMOUNT_RECEIVED",
            "Crop insurance proceeds and federal crop disaster payments_Taxable amount":"CROP_INSURANCE_TAXABLE_AMOUNT",
            "Custom hire (machine work) income":"CUSTOM_HIRE_INCOME",
            "Other income, including federal and state gasoline or fuel tax credit or refund":"OTHER_INCOME", 
            "Gross income":"GROSS_INCOME",
            "Car and truck expenses":"CAR_TRUCK_EXPENSE",
            "Chemicals":"CHEMICALS",
            "Conservation expenses":"CONSERVATION_EXPENSES",
            "Custom hire (machine work)":"CUSTOM_HIRE",
            "Depreciation and section 179 expense":"DEPRECIATION_S_179_EXPENSE",
            "Employee benefit programs other than line 23":"EMPLOYEE_BENEFIT_PROGRAM",
            "Feed":"FEED",
            "Fertilizers and lime":"FERTILIZERS__LIME",
            "Freight and trucking":"FREIGHT_TRUCKING",
            "Gasoline, fuel, and oil":"GASOLINE_FUEL_OIL",
            "Insurance (other than health)":"INSURANCE_OTHER_THAN_HEALTH",
            "Interest_Mortgage (paid to banks, etc.)":"INTEREST_MORTAGE",
            "Interest_Other":"INTEREST_OTHER",
            "Labor hired (less employment credits)":"LABOUR_HIRED",
            "Pension and profit-sharing plans":"PENSION_PROFIT_SHARING_PLAN",
            "Rent or lease_Vehicles, machinery, equipment":"RENT_LEASE_Vehicle_machinery_eqipments",
            "Rent or lease_Other (land, animals, etc.)":"RENT_LEASE_OTHER",
            "Repairs and maintenance":"REPAIRS_MAINTENANCE",
            "Seeds and plants":"SEEDS_PLANTS",
            "Storage and warehousing":"STORAGE_WAREHOSING",
            "Supplies":"SUPPLIES",
            "Taxes":"TAXES",
            "Utilities":"UTILITIES",
            "Veterinary, breeding, and medicine":"VETERINARY_BREEDING_MEDICINE",
            "Other expenses Attribute1":"OTHER_EXPENSES_Attribute1",
            "Other expenses Value1":"OTHER_EXPENSES_Value1",
            "Other expenses Attribute2":"OTHER_EXPENSES_Attribute2",
            "Other expenses Value2":"OTHER_EXPENSES_Value2",
            "Other expenses Attribute3":"OTHER_EXPENSES_Attribute3",
            "Other expenses Value3":"OTHER_EXPENSES_Value3",
            "Other expenses Attribute4":"OTHER_EXPENSES_Attribute4",
            "Other expenses Value4":"OTHER_EXPENSES_Value4",
            "Other expenses Attribute5":"OTHER_EXPENSES_Attribute5",
            "Other expenses Value5":"OTHER_EXPENSES_Value5",
            "Other expenses Attribute6":"OTHER_EXPENSES_Attribute6",
            "Other expenses Value6":"OTHER_EXPENSES_Value6",
            "Other expenses Attribute7":"OTHER_EXPENSES_Attribute7",
            "Other expenses Value7":"OTHER_EXPENSES_Value7",
            "Other expenses Attribute8":"OTHER_EXPENSES_Attribute8",
            "Other expenses Value8":"OTHER_EXPENSES_Value8",
            "Other expenses Attribute9":"OTHER_EXPENSES_Attribute9",
            "Other expenses Value9":"OTHER_EXPENSES_Value9",
            "Other expenses Attribute10":"OTHER_EXPENSES_Attribute10",
            "Other expenses Value10":"OTHER_EXPENSES_Value10",
            "Total Other Expenses":"TOTAL_OTHER_EXPENSES",
            "Total Expenses":"TOTAL_EXPENSES",
            "Net Farm":"NET_FARM_PROFIT_LOSS",
            },

         "Schedule E": {    
            "Name":"NAME",
            "Code":"NAICS",
            "Principal Business":"PRINCIPAL_BUSINESS",
            "Tax Basis":"TAX_BASIS",
            "Year":"YEAR",
            "Status":"STATUS",
            "Company":"COMPANY",
            "Property":"PROPERTY",
            "Rents":"RENT_RECEIVED",
            "Royalities":"ROYALTIES_RECEIVED",
            "Total Income":"TOTAL_INCOME",
            "Advertising":"ADVERTISING",
            "Auto Travel":"AUTO_TRAVEL",
            "Cleaning Maintenance":"CLEANING_MAINTENANCE",
            "Commissions":"COMMISSIONS",
            "Insurance":"INSURANCE",
            "Other Legal Fees":"LEGAL_OTHER_FEE",
            "Management Fees":"MANAGEMENT_FEES",
            "Mortage Interest":"MORTAGE_INTEREST",
            "Other Interest":"OTHER_INTEREST",
            "Repairs":"REPAIRS",
            "Supplies":"SUPPLIES",
            "Taxes":"TAXES",
            "Utilities":"UTILITIES",
            "Depreciation":"DEPRECIATION",
            "Other expenses Attribute1":"OTHER_EXPENSES_Attribute1",
            "Other expenses Value1":"OTHER_EXPENSES_Value1",
            "Other expenses Attribute2":"OTHER_EXPENSES_Attribute2",
            "Other expenses Value2":"OTHER_EXPENSES_Value2",
            "Other expenses Attribute3":"OTHER_EXPENSES_Attribute3",
            "Other expenses Value3":"OTHER_EXPENSES_Value3",
            "Other expenses Attribute4":"OTHER_EXPENSES_Attribute4",
            "Other expenses Value4":"OTHER_EXPENSES_Value4",
            "Other expenses Attribute5":"OTHER_EXPENSES_Attribute5",
            "Other expenses Value5":"OTHER_EXPENSES_Value5",
            "Other expenses Attribute6":"OTHER_EXPENSES_Attribute6",
            "Other expenses Value6":"OTHER_EXPENSES_Value6",
            "Other expenses Attribute7":"OTHER_EXPENSES_Attribute7",
            "Other expenses Value7":"OTHER_EXPENSES_Value7",
            "Other expenses Attribute8":"OTHER_EXPENSES_Attribute8",
            "Other expenses Value8":"OTHER_EXPENSES_Value8",
            "Other expenses Attribute9":"OTHER_EXPENSES_Attribute9",
            "Other expenses Value9":"OTHER_EXPENSES_Value9",
            "Other expenses Attribute10":"OTHER_EXPENSES_Attribute10",
            "Other expenses Value10":"OTHER_EXPENSES_Value10",
            "Total Other Expenses":"TOTAL_OTHER_EXPENSES",            
            "Total Expenses":"TOTAL_EXPENSES",
            "Net Income":"NET_INCOME",
         },

        "Balance Sheet": {  
            "Year":"YEAR",
            "Status":"STATUS",
            "Company":"COMPANY_NAME",
            "Cash & Equi":"C_CASH_EQUITY",
            "Crop Insurance Receivable":"C_CROP_INSURANCE_RECEIVABLE",
            "Trade Receiveable":"C_TRADE_RECEIVABLE",
            "Stocks and Bonds":"C_STOCKS_BONDS",
            "Fuel and fertilizer":"C_FUEL_FERTILIZER",
            "Due from Related Entity":"C_DUE_RELATED_ENTITY",
            "Farm Products and Feed on hand":"C_FARM_PRODUCTS_AND_FEED_ON_HAND",
            "Growing Crops":"C_GROWING_CROPS",
            "Prepaid Expenses":"C_PREPAID_EXPENSES",
            "Other Current Assets":"C_OTHER_CURRENT_ASSETS",
            "Total Current Assets":"C_TOTAL_CURRENT_ASSETS",
            "Building, Improvements, Equipment":"F_BUILDING_IMPROVEMENTS_EQIPMENTS", 
            "Less Accumulated Depreciation":"F_LESS_ACCUMULATED_DEPRECIATION",
            "Residence":"F_RESIDENCE",
            "Real Estate":"F_REAL_ESTATE",
            "Livestock":"F_LIVESTOCK",
            "Long term crop Inventory":"F_LONG_TERM_CROP_INVENTORY",
            "Investments and Partnerships":"F_INVESTMENTS_PARTNERSHIPS",
            "Total Fixed Assets":"F_TOTAL_FIXED_ASSETS",
            "Investment in Life Insurance":"O_INVESTMENTS_IN_LIFE_INSURANCE",
            "Patronage Stocks":"O_PATRONAGE_STOCKS",
            "O&G Royalties":"O_O_and_G_ROYALTIES",
            "Personal Property":"O_PERSONAL_PROPERTY",
            "USDA Payments crp plc/arc":"O_USDA_PAYMENTS_CRP_PLC_ARC",
            "Stock in CO-OPS":"O_STOCK_IN_CO_OPS",
            "Other Long term assets":"O_OTHER_LONG_TERM_ASSETS",
            "Total Other Assets":"O_TOTAL_OTHER_ASSETS",
            "Total Assets":"TOTAL_ASSETS",
            "Accrued Expense":"CL_ACCURED_EXPENSE",
            "Due to Related Entity":"CL_DUE_TO_RELATED_ENTITY",
            "Accounts Payable":"CL_ACCOUNTS_PAYABLE",
            "Insurance payments":"CL_INSURANCE_PAYMENTS",
            "Current portion of long term debt- Equipment":"CL_CURRENT_PORTION_OF_LONG_TERM_DEBT_EQUIPMENT",
            "Current portion of long-term debt- Operating":"CL_CURRENT_PORTION_OF_LONG_TERM_DEBT_OPERATING",
            "Current portion of long term debt- Real Estate":"CL_CURRENT_PORTION_OF_LONG_TERM_DEBT_REAL_ESTATE",
            "Other Current Liabilities":"CL_OTHER_CURRENT_LIABILITIES",
            "Total Current Liabilities":"CL_TOTAL_CURRENT_LIABILITIES",
            "Notes Payable - Equipment":"LL_NOTES_PAYABLE_EQUIPMENT",
            "Notes Payable - Operating":"LL_NOTES_PAYABLE_OPERATING",
            "Notes Payable - Land":"LL_NOTES_PAYABLE_LAND",
            "Property taxes":"LL_PROPERTY_TAXES",
            "Long term leases":"LL_LONG_TERM_LEASE",
            "Other long term liabilities":"LL_OTHER_LONG_TERM_LIABILITIES",
            "Total Long Term Liabilities":"LL_TOTAL_LONGTERM_LIABILITIES",
            "Total Liabilties":"TOTAL_LIABILITIES",
            "Common Stock":"E_COMMON_STOCK",
            "Dividends / Distributions Paid":"E_DIVIDENDS_OR_DISTRIBUTIONS_PAID",
            "Owners' Equity / Retained Earnings":"E_OWNERS_EQUITY_OR_RETAINED_EARNINGS",
            "Treasury Stock":"E_TREASURY_STOCK",
            "Total Equity":"TOTAL_EQUITY",
            "Total Liabilities and Equity":"TOTAL_LIABILITIES_EQUITY"
         },

        "Schedule L": {  
            "Year":"YEAR",
            "Status":"STATUS",
            "Business Name":"COMPANY_NAME",
            "Cash":"Cash",                                                                
            "Trade notes and accounts receivable":"Trade_notes_and_accounts_receivable",                     
            "Less allowance for bad debts":"Less_allowance_for_bad_debts",                                
            "Inventories":"Inventories",                                                        
            "US Government obligations":"US_Government_obligations",                                
            "Tax-exempt securities":"Tax_exempt_securities",                                          
            "Other current assets (attach statement)":"Other_current_assets_attach_statement",                  
            "Loans to partners (or persons related to partners)":"Loans_to_partners_or_persons_related_to_partners",     
            "Mortgage and real estate loans":"Mortgage_and_real_estate_loans",                              
            "Other investments (attach statement)":"Other_investments_attach_statement",                     
            "Buildings and other depreciable assets":"Buildings_and_other_depreciable_assets",                   
            "Less accumulated depreciation":"Less_accumulated_depreciation",                             
            "Depletable assets":"Depletable_assets",                                               
            "Less accumulated depletion":"Less_accumulated_depletion",                                  
            "Land (net of any amortization)":"Land_net_of_any_amortization",                               
            "Intangible assets (amortizable only)":"Intangible_assets_amortizable_only",                        
            "Less accumulated amortization":"Less_accumulated_amortization",                             
            "Other assets (attach statement)":"Other_assets",                             
            "Total assets":"Total_assets",
            "Accounts payable":"Accounts_payable",                                           
            "Mortgages, notes, bonds payable in less than 1 year":"Mortgages_notes_bonds_payable_in_less_than_1_year",
            "Other current liabilities (attach statement)":"Other_current_liabilities",                
            "All nonrecourse loans":"All_nonrecourse_loans",                                          
            "Loans from partners (or persons related to partners)":"Loans_from_partners_or_persons_related_to_partners", 
            "Mortgages, notes, bonds payable in 1 year or more":"Mortgages_notes_bonds_payable_in_1_year_or_more",  
            "Other liabilities (attach statement)":"Other_liabilities",                          
            "Partners’ capital accounts":"Partners_capital_accounts",                                    
            "Total liabilities and capital":"Total_liabilities_and_capital"                                     
        }

    }

    # Transpose data in each sheet
    transposed_data = {}
    for sheet_name, sheet_data in excel_data.items():
        if sheet_name in column_mappings:
            column_mapping = column_mappings[sheet_name]
            transposed_data[sheet_name] = sheet_data.iloc[:, 1:].transpose()
            transposed_data[sheet_name].columns = transposed_data[sheet_name].iloc[0]  # Set the first row as the column names
            transposed_data[sheet_name] = transposed_data[sheet_name].iloc[1:]  # Remove the first row
            transposed_data[sheet_name] = transposed_data[sheet_name].rename(columns=column_mapping)

    return transposed_data


def create_config_file(A_ID, LOAN_ID, User):
    config_data = {
        "USER": User,
        "A_ID": A_ID,
        "LOAN_ID": LOAN_ID
    }

    with open("config.json", "w") as file:
        json.dump(config_data, file)


# Make API call to API Gateway
def make_api_call(url, data):

    try:
        logging.info(f"Making API call to {url}")
        logging.debug(f"API Request Data: {data}")
        response = requests.post(url, json=data)
        response.raise_for_status()
        logging.info(f"API call successful: {response.json()}")
    except requests.exceptions.RequestException as e:
        logging.error(f"API call failed: {e}")
        if isinstance(e, requests.exceptions.HTTPError):
            logging.error(f"HTTP Error Response: {e.response.text}")
        raise HTTPException(status_code=500, detail="API call failed")

@app.post("/form")
async def process_data(request: Request, file: UploadFile = File(...), A_ID: int = Form(...), LOAN_ID: int = Form(...), Name: str = Form(...)):
    try:    
        transposed_data = transpose_excel_data(file.file)
        form_data = await request.form()

        A_ID = int(form_data["A_ID"])
        LOAN_ID = int(form_data["LOAN_ID"])
        User = form_data["Name"]

        logging.info("Received form data:")
        logging.info(f"A_ID: {A_ID}")
        logging.info(f"LOAN_ID: {LOAN_ID}")
        logging.info(f"User: {Name}")

        logging.info(f"Transposed data: {transposed_data}")

        # Read Excel file into a pandas DataFrame
        
        data_SC = transposed_data["Schedule C"].to_json(orient='split')

        data_SF = transposed_data["Schedule F"].to_json(orient='split')

        data_SE = transposed_data["Schedule E"].to_json(orient='split')

        data_SL = transposed_data["Schedule L"].to_json(orient='split')

        data_BS = transposed_data["Balance Sheet"].to_json(orient='split')

        logging.info("Data read from Excel files:")
        logging.info(f"Data_SC: {data_SC}")
        logging.info(f"Data_SF: {data_SF}")
        logging.info(f"Data_SE: {data_SE}")
        logging.info(f"Data_SL: {data_SL}")
        logging.info(f"Data_BS: {data_BS}")
        # Make API call to API Gateway
        api_url_sc = "https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Financials/insert_financials_data/scheduleC"

        api_url_sf = "https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Financials/insert_financials_data/scheduleF"

        api_url_se = "https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Financials/insert_financials_data/scheduleE"

        api_url_sl = "https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Financials/insert_financials_data/scheduleL"

        api_url_bs = "https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Financials/insert_financials_data/balanceSheet"

        api_url_cal_BS_IS = "https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Financials/insert_financials_data/Calculative_Fields"

        payload_sc = {
            "Data": data_SC,
            "A_ID": A_ID,
            "LOAN_ID": LOAN_ID,
            "User": User
        }
        logging.info(f"Payload SC: {payload_sc}")
        payload_sf = {
            "Data": data_SF,
            "A_ID": A_ID,
            "LOAN_ID": LOAN_ID,
            "User": User
        }
        logging.info(f"Payload SF: {payload_sf}")
        payload_se = {
            "Data": data_SE,
            "A_ID": A_ID,
            "LOAN_ID": LOAN_ID,
            "User": User
        }

        payload_sl = {
            "Data": data_SL,
            "A_ID": A_ID,
            "LOAN_ID": LOAN_ID,
            "User": User
        }

        payload_bs = {
            "Data": data_BS,
            "A_ID": A_ID,
            "LOAN_ID": LOAN_ID,
            "User": User
        }

        payload_cal_BS_IS = {
            "Data_SC": data_SC,
            "Data_SF": data_SF,
            "Data_SE": data_SE,
            "Data_SL": data_SL,
            "Data_BS": data_BS,
            "A_ID": A_ID,
            "LOAN_ID": LOAN_ID,
            "User": User
        } 

        make_api_call(api_url_sc, payload_sc)
        make_api_call(api_url_sf, payload_sf)
        make_api_call(api_url_se, payload_se)
        make_api_call(api_url_sl, payload_sl)
        make_api_call(api_url_bs, payload_bs)
        make_api_call(api_url_cal_BS_IS, payload_cal_BS_IS)

        create_config_file(A_ID, LOAN_ID, User)

        return {"message": "Data inserted successfully"}
    except pd.errors.EmptyDataError:
        logging.error("Excel file is empty.")
        raise HTTPException(status_code=400, detail="Excel file is empty.")
    except pd.errors.ParserError:
        logging.error("Error parsing Excel file.")
        raise HTTPException(status_code=400, detail="Error parsing Excel file.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error processing data: {e}")
        raise HTTPException(status_code=500, detail="Error processing data")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error")
    

#---------------------------------------------------------------------------------------------
#Export
# Sample column mappings
column_mapping_BS = {
    "YEAR":" YEAR",
    "STATUS": "Status",
    "C_CASH_EQUITY":"Cash & Equi",
    "C_CROP_INSURANCE_RECEIVABLE":"Crop Insurance Receivable",
    "C_TRADE_RECEIVABLE":"Trade Receiveable",
    "C_STOCKS_BONDS":"Stocks and Bonds",
    "C_FUEL_FERTILIZER":"Fuel & Fertilizer",
    "C_DUE_RELATED_ENTITY": "Due Related Entity",
    "C_FARM_PRODUCTS_AND_FEED_ON_HAND":"Farm Products and Feed on hand",
    "C_GROWING_CROPS":"Growing Crops",
    "C_PREPAID_EXPENSES":"Prepaid Expenses",
    "C_OTHER_CURRENT_ASSETS":"Other Current Assets",
    "C_TOTAL_CURRENT_ASSETS":"Total Current Assets",
    "F_BUILDING_IMPROVEMENTS_EQIPMENTS":"Building, Improvements, Equipment ",
    "F_LESS_ACCUMULATED_DEPRECIATION":"Less Accumulated Depreciation",
    "F_RESIDENCE":"Residence (Homestead)+2 Residental plots",
    "F_REAL_ESTATE":"Real Estate including Improvements",
    "F_LIVESTOCK":"Livestock",
    "F_LONG_TERM_CROP_INVENTORY": "Long Term Crop Inventory",
    "F_INVESTMENTS_PARTNERSHIPS":"Investments and Partnerships",
    "F_TOTAL_FIXED_ASSETS":"Total Fixed Assets",
    "O_INVESTMENTS_IN_LIFE_INSURANCE":"Investment in Life Insurance",
    "O_PATRONAGE_STOCKS":"Patronage Stocks",
    "O_O_and_G_ROYALTIES":"O&G Royalties",
    "O_PERSONAL_PROPERTY":"Personal Property",
    "O_USDA_PAYMENTS_CRP_PLC_ARC":"USDA Payments crp plc/arc",
    "O_STOCK_IN_CO_OPS":"Stock in CO-OPS",
    "O_OTHER_LONG_TERM_ASSETS":"Other Long Term Assets",
    "O_TOTAL_OTHER_ASSETS":"Total Other Assets",
    "TOTAL_ASSETS":"Total Assets",
    "CL_ACCURED_EXPENSE":"Accrued Expense",
    "CL_DUE_TO_RELATED_ENTITY":"Due to Related Entity",
    "CL_ACCOUNTS_PAYABLE":"Accounts Payable",
    "CL_INSURANCE_PAYMENTS":"Insurance Payments",
    "CL_CURRENT_PORTION_OF_LONG_TERM_DEBT_EQUIPMENT":"Current POrtion of Long Term Debt Equipment",
    "CL_CURRENT_PORTION_OF_LONG_TERM_DEBT_OPERATING":"Current POrtion of Long Term Debt Operating",
    "CL_CURRENT_PORTION_OF_LONG_TERM_DEBT_REAL_ESTATE":"Current POrtion of Long Term Debt Real-Estate",
    "CL_OTHER_CURRENT_LIABILITIES":"Other Current Liabilities",
    "CL_TOTAL_CURRENT_LIABILITIES":"Total Current Liabilities",
    "LL_NOTES_PAYABLE_EQUIPMENT":"Notes Payable - Equipment",
    "LL_NOTES_PAYABLE_OPERATING":"Notes Payable - Operating",
    "LL_NOTES_PAYABLE_LAND":"Notes Payable - Land",
    "LL_PROPERTY_TAXES":"Property taxes",
    "LL_LONG_TERM_LEASE":"Long Term Lease",
    "LL_OTHER_LONG_TERM_LIABILITIES": "Other Long Term Liabilities",
    "LL_TOTAL_LONGTERM_LIABILITIES":"Total Long Term Liabilities",
    "TOTAL_LIABILITIES":"Total Liabilties",
    "E_COMMON_STOCK":"Common Stock",
    "E_DIVIDENDS_OR_DISTRIBUTIONS_PAID":"Dividends / Distributions Paid",
    "E_OWNERS_EQUITY_OR_RETAINED_EARNINGS":"Owners' Equity / Retained Earnings",
    "E_TREASURY_STOCK":"Treasury Stock",
    "TOTAL_EQUITY":"Total Equity",
    "TOTAL_LIABILITIES_EQUITY":"Total Liabilities and Equity",
}

column_mapping_IS = {

    "YEAR":" YEAR",
    "STATUS": "Status",
    "I_Agricultural_Program_Payment":   "Agricultural Program Payment",
    "I_Cooperative_Distributions":"Cooperative Distributions",
    "I_Crop_Insurance_Proceeds":"Crop Insurance Proceeds",
    "I_Crop_Sales":"Crop Sales",
    "I_Farm_Management":"Farm Management / Customer Hire",
    "I_Interest_Income":"Interest Income",
    "I_Other_Income":"Other Income",
    "I_Total_Income":"Total Income",
    "E_Advertising":"Advertising",
    "E_Chemical_and_Fertilizer":"Chemical and Fertilizer",
    "E_CAR_TRUCK_EXPENSE":"Car & Truck Expense",
    "E_Custom_Hire_Contract_Labo":"  Custom Hire & Contract Labo",
    "E_Depreciation_Expense":"Depreciation Expense",
    "E_Dues_Fees_Subscriptions":"   Dues, Fees, and Subscriptions",
    "E_Employee_Benefit_Programs":" Employee Benefit Programs",
    "E_Equipment_Lease":"   Equipment Lease",
    "E_Lease_Other":"Other Lease",
    "E_Feed_Medicine":"Feed & Medicine",
    "E_Freight":"Freight",
    "E_Gasoline_Fuel_Oil":"Gasoline, Fuel, and Oil",
    "E_Insurance":"Insurance",
    "E_Interest":"Interest",
    "E_Legal_Professional":"Legal and Professional",
    "E_Meals_Entertainment":"Meals and Entertainment",
    "E_Miscellaneous":"Miscellaneous",
    "E_Repairs_Maintenance":"Repairs and Maintenance",
    "E_Seeds_Plants_Purchased":"Seeds and Plants Purchased",
    "E_Supplies":"Supplies",
    "E_Taxes":"Taxes",
    "E_TRAVEL":"Travel",
    "E_Telephone_Utilities":"Telephone and Utilities",
    "E_VETERINARY_BREEDING_MEDICINE":"Veterinary Breeding Medicine",
    "E_Wages":"Wages",
    "E_OTHER_EXPENSE":"Other Expense",
    "E_PLUG_ANU_MISSING_EXPENSE":"Plug Anu Missing Expense",
    "E_Total_Expenses":"Total Expense",
    "Net_income":"Net Expense",
}

column_mapping_CF = {
    "YEAR":" YEAR",      
    "STATUS": "Status",
    "OPERATING_INCOME":"Operating Income ",
    "Net_income":"Net income",	
    "EBIDTA":"EBIDTA",	
    "OPERATING_MARGIN_PERCENT"	:"Operating Margin (%)",
    "Net_Profit_Margin_PERCENT"	:"Net Profit Margin (%)",
    "DSCR"	:"DSCR",
    "DEBT_PAYMENT_AND_INTEREST"	:"Debt Payment & Interest",
    "DEBT_TO_EBIDTA"	:"Debt to EBIDTA",
    "DEBT_TO_TOTAL_ASSETS"	:"Debt to Total Assets",
    "CURRENT_RATIO"	:"Current Ratio",
    "FUNDING_DEBT"	:"Funding Debt",
    "EFFECTIVE_INTEREST_RATE_PERCENT":"Effective Interest Rate (%)",
    "DEBT_OVER_EBIDTA":"Debt over EBIDTA",

}

def make_api_call(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        logging.info(f"API call successful: {response.json()}")
        return response
    except requests.exceptions.RequestException as e:
        logging.error(f"API call failed: {e}")
        raise HTTPException(status_code=500, detail="API call failed")

def map_and_transpose_data(data, column_mapping):
    mapped_data = data.rename(columns=column_mapping)
    # Select only the columns present in the mapping
    selected_columns = [col for col in mapped_data.columns if col in column_mapping.values()]
    transposed_data = mapped_data[selected_columns].transpose()
    return transposed_data




# Endpoint to get loan_ids from AWS API for Loan Application dropdown
@app.get("/loan_ids")
async def get_loan_ids_from_aws():
    aws_api_url = "https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Financials/Export_financials_data/export_loanID"
    response = requests.get(aws_api_url)
    loan_ids = response.json()
    return loan_ids

@app.get("/export-data/{loan_id}")
async def export_data(loan_id: str):
    try:
        # Make API requests to get data from AWS APIs using requests
        balance_sheet_url = f"https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Financials/Export_financials_data/export_balance_sheet?loan_id={loan_id}"
        income_statement_url = f"https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Financials/Export_financials_data/export_incomestatement?loan_id={loan_id}"
        calculated_field_url = f"https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Financials/Export_financials_data/export_calculated_fields?loan_id={loan_id}"

        balance_sheet_response = make_api_call(balance_sheet_url)
        income_statement_response = make_api_call(income_statement_url)
        calculated_field_response = make_api_call(calculated_field_url)

        # Assuming the API responses are in JSON format, you can access the data using .json()
        data_BS = balance_sheet_response.json()["data"]
        data_IS = income_statement_response.json()["data"]
        data_CF = calculated_field_response.json()["data"]

        # Apply column mappings and transpose the data
        transposed_data_BS = map_and_transpose_data(pd.DataFrame(data_BS), column_mapping_BS)
        transposed_data_IS = map_and_transpose_data(pd.DataFrame(data_IS), column_mapping_IS)
        transposed_data_CF = map_and_transpose_data(pd.DataFrame(data_CF), column_mapping_CF)

        TEMP_DIR = "temp"
        if not os.path.exists(TEMP_DIR):
            os.mkdir(TEMP_DIR)

        # Export transposed data to Excel file
        transposed_file_path = os.path.join(TEMP_DIR, f"{loan_id}_financial_statements.xlsx")
        with pd.ExcelWriter(transposed_file_path) as writer:
            transposed_data_BS.to_excel(writer, sheet_name="Balance_Sheet", index=True)
            transposed_data_IS.to_excel(writer, sheet_name="Income_Statement", index=True)
            transposed_data_CF.to_excel(writer, sheet_name="Calculated_Fields", index=True)

        # Process the Excel file after writing to remove top 3 rows and set 'YEAR' row as header
        with pd.ExcelFile(transposed_file_path) as xls:
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name)
              
                # Remove top 3 rows including header
                # df = df.iloc[3:]
                # Set 'YEAR' row as header
                df = df.reset_index(drop=True)
                df.columns = df.iloc[0].values
                df = df[1:]
                
                # Save the modified DataFrame back to the same sheet
                df.to_excel(writer, sheet_name=sheet_name, index=False)

        # Set the response headers
        headers = {
            "Content-Disposition": f"attachment; filename={loan_id}_financial_statements.xlsx",
            "Content-Type": "application/octet-stream",
        }

        return FileResponse(transposed_file_path, headers=headers)
    except Exception as e:
        logging.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
#===================================================================================================================================================================================================

S3_BUCKET_NAME = "schedules-template"

def generate_presigned_url(bucket_name, object_key, expiration=3600):
    s3 = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        aws_session_token=AWS_SESSION_TOKEN if AWS_SESSION_TOKEN else None
    )

    url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket_name, 'Key': object_key},
        ExpiresIn=expiration
    )

    return url

@app.get("/get_template_url")
def get_template_url():
    template_url = generate_presigned_url(S3_BUCKET_NAME, "Template.xlsx")
    return {"template_url": template_url}

#============================================================================================
def get_db_connection():
    connection = pymysql.connect(
        host='gofin-aurora-instance-1.ci0rkg2zgzsd.us-east-1.rds.amazonaws.com',
        user='praveend',
        password='Praveend@jn2',
        database='usda',
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection
#==========================================================================

# Function to fetch applicant details based on the applicant type (individual or business)
async def fetch_applicant_details(request: Request):
    user_id = request.session.get("userId")
    if not user_id:
        return JSONResponse(status_code=401, content="User is not logged in")

    # Fetch loan data from the database using the user's session data
    loan_id = request.session.get("selectedLoanId")
    if not loan_id:
        return JSONResponse(status_code=404, content={"error": "No loan data found for editing"})

    applicant_id = request.session.get("selectedApplicantId")
    if not applicant_id:
        return JSONResponse(status_code=404, content={"error": "No APPLICANT_ID found for editing"})

    try:
        # Establish a database connection
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Use callproc to execute the stored procedure
            cursor.callproc("EDIT_DISPLAY_APPLICANT_DETAILS", (loan_id, applicant_id))

            # Fetch all rows from the result set
            applicant_details = cursor.fetchall()

            if applicant_details:
                # Convert the fetched data to a list of dictionaries
                applicant_details_list = []
                for row in applicant_details:
                    applicant_details_dict = {
                        "applyingAs": row.get("APPLYING_AS"),
                        "typeOfApplicant": row.get("TYPE_OF_APPLICANT"),
                        "A_ID": row.get("A_ID"),
                        "relationWithPrimaryApplicant": row.get("RELATION_WITH_PRIMARY_APPLICANT"),
                        "PA_ID": row.get("PA_ID"),
                        "loanID": row.get("LOAN_ID"),
                        "firstName": row.get("FIRST_NAME"),
                        "middleName": row.get("MIDDLE_NAME"),
                        "lastName": row.get("LAST_NAME"),
                        "email": row.get("EMAIL"),
                        "telephone": row.get("TELEPHONE"),
                        "fax": row.get("FAX"),
                        "streetAddress": row.get("STREET_ADDRESS"),
                        "city": row.get("CITY"),
                        "state": row.get("STATE"),
                        "zip": row.get("ZIP"),
                        "county": row.get("COUNTY"),
                        "socialSecurity": row.get("SOCIAL_SEC"),
                        "dateOfBirth": row.get("D_O_B"),
                        "maritalStatus": row.get("MARITAL_STATUS"),
                        "yearBeginningFarming": row.get("YEAR_BEGIN_FARMING"),
                        "yearAtCurrentAddress": row.get("YEAR_AT_CURRENT_ADDRESS"),
                        "usCitizenOrPermanentAlien": row.get("US_CITIZEN_OR_PERMANENT_ALIEN"),
                        # Add other fields as needed for individual applicant details
                    }
                    applicant_details_list.append(applicant_details_dict)

                return JSONResponse(content=applicant_details_list)
            else:
                raise HTTPException(status_code=404, detail="Applicant details not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    finally:
        # Close the database connection
        connection.close()


# Function to fetch business entity details
async def fetch_business_entity_details(request: Request):
    user_id = request.session.get("userId")
    if not user_id:
        return JSONResponse(status_code=401, content="User is not logged in")

    # Fetch loan data from the database using the user's session data
    loan_id = request.session.get("selectedLoanId")
    if not loan_id:
        return JSONResponse(status_code=404, content={"error": "No loan data found for editing"})

    applicant_id = request.session.get("selectedApplicantId")
    if not applicant_id:
        return JSONResponse(status_code=404, content={"error": "No APPLICANT_ID found for editing"})

    try:
        # Establish a database connection
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Use callproc to execute the stored procedure
            cursor.callproc("EDIT_DISPLAY_APPLICANT_BUSINESS_ENTITY", (loan_id, applicant_id))

            # Fetch all rows from the result set
            business_entity_details = cursor.fetchall()

            if business_entity_details:
                # Convert the fetched data to a list of dictionaries
                business_entity_details_list = []
                for row in business_entity_details:
                    business_entity_details_dict = {
                        "applyingAs": row.get("APPLYING_AS"),
                        "typeOfApplicant": row.get("TYPE_OF_APPLICANT"),
                        "A_ID": row.get("A_ID"),
                        "relationWithPrimaryApplicant": row.get("RELATION_WITH_PRIMARY_APPLICANT"),
                        "PA_ID": row.get("PA_ID"),
                        "loanID": row.get("LOAN_ID"),
                        "businessName": row.get("BUSINESS_NAME"),
                        "email": row.get("EMAIL"),
                        "taxId": row.get("FEDERAL_TAX_ID"),
                        "telephone": row.get("TELEPHONE"),
                        "fax": row.get("FAX"),
                        "streetAddress": row.get("STREET_ADDRESS"),
                        "city": row.get("CITY"),
                        "state": row.get("STATE"),
                        "zip": row.get("ZIP"),
                        "county": row.get("COUNTY"),
                        "contactNameDetails": row.get("CONTACT_NAME_DETAILS"),
                        "businessDescription": row.get("DESCRIPTION_OF_BUSINESS_OR_CUSTOM_SERVICES"),
                        "principalOfficer": row.get("PRINCIPAL_OFFICER"),
                        "homeAddress": row.get("HOME_ADDRESS"),
                        "percentOwned": row.get("Percent_OWNED"),
                        "ownershipTitle": row.get("TITLE"),
                        # Add other fields as needed for business entity details
                    }
                    business_entity_details_list.append(business_entity_details_dict)

                return JSONResponse(content=business_entity_details_list)
            else:
                raise HTTPException(status_code=404, detail="Business entity details not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    finally:
        # Close the database connection
        connection.close()


# Function to fetch additional applicant information
async def fetch_additional_applicant_information(request: Request):
    user_id = request.session.get("userId")
    if not user_id:
        return JSONResponse(status_code=401, content="User is not logged in")

    # Fetch loan data from the database using the user's session data
    loan_id = request.session.get("selectedLoanId")
    if not loan_id:
        return JSONResponse(status_code=404, content={"error": "No loan data found for editing"})

    applicant_id = request.session.get("selectedApplicantId")
    if not applicant_id:
        return JSONResponse(status_code=404, content={"error": "No APPLICANT_ID found for editing"})

    try:
        # Establish a database connection
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Use callproc to execute the stored procedure
            cursor.callproc("EDIT_DISPLAY_ADDITIONAL_APPLICANT_INFORMATION", (loan_id, applicant_id))

            # Fetch all rows from the result set
            additional_applicant_info = cursor.fetchall()

            if additional_applicant_info:
                # Convert the fetched data to a list of dictionaries
                additional_applicant_info_list = []
                for row in additional_applicant_info:
                    additional_applicant_info_dict = {
                        "A_ID": row.get("A_ID"),
                        "loanID": row.get("LOAN_ID"),
                        "additionalComments": row.get("ADDITIONAL_COMMENTS"),
                        "grossFarmIncome": row.get("GROSS_FARM_INCOME"),
                        "netFarmIncome": row.get("NET_FARM_INCOME"),
                        "netNonFarmIncome": row.get("NET_NON_FARM_INCOME"),
                        "sourceOfNonFarmIncomeD1": row.get("SOURCE_OF_NON_FARM_INCOME_D1"),
                        "sourceOfNonFarmIncomeA1": row.get("SOURCE_OF_NON_FARM_INCOME_A1"),
                        "sourceOfNonFarmIncomeD2": row.get("SOURCE_OF_NON_FARM_INCOME_D2"),
                        "sourceOfNonFarmIncomeA2": row.get("SOURCE_OF_NON_FARM_INCOME_A2"),
                        "sourceOfNonFarmIncomeD3": row.get("SOURCE_OF_NON_FARM_INCOME_D3"),
                        "sourceOfNonFarmIncomeA3": row.get("SOURCE_OF_NON_FARM_INCOME_A3"),
                        "sourceOfNonFarmIncomeD4": row.get("SOURCE_OF_NON_FARM_INCOME_D4"),
                        "sourceOfNonFarmIncomeA4": row.get("SOURCE_OF_NON_FARM_INCOME_A4"),
                        "sourceOfNonFarmIncomeD5": row.get("SOURCE_OF_NON_FARM_INCOME_D5"),
                        "sourceOfNonFarmIncomeA5": row.get("SOURCE_OF_NON_FARM_INCOME_A5"),
                        "totalAssets": row.get("TOTAL_ASSETS"),
                        "totalLiabilities": row.get("TOTAL_LIABILITIES"),
                        # Add other fields as needed for additional applicant information
                    }
                    additional_applicant_info_list.append(additional_applicant_info_dict)

                return JSONResponse(content=additional_applicant_info_list)
            else:
                raise HTTPException(status_code=404, detail="Additional applicant information not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    finally:
        # Close the database connection
        connection.close()








@app.post("/store_selected_borrowing_id")
async def store_selected_borrowing_id(request: Request, borrowing_id: int):
    # Store the selected BORROWING_ID in the session
    request.session["selectedBorrowingId"] = borrowing_id
    return {"message": "Selected BORROWING_ID stored in session"}
#==========================================================================

@app.get("/fetchLoan")
async def fetch_loan_data(request: Request):
    user_id = request.session.get("userId")
    if not user_id:
        return JSONResponse(status_code=401, content="User is not logged in")

    # Fetch loan data from the database using the user's session data
    loan_id = request.session.get("selectedLoanId")
    if not loan_id:
        return JSONResponse(status_code=404, content={"error": "No loan data found for editing"})
    
    borrowing_id = request.session.get("selectedBorrowingId")

    if not borrowing_id:
        return JSONResponse(status_code=404, content={"error": "No BORROWING_ID found for editing"})

    try:
        # Establish a database connection
        aws_api_url = f"https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Loan_Application_Form/Loans/Fetch_Loan_Data_Edit?loan_id={loan_id}&borrowing_id={borrowing_id}"
        response = requests.get(aws_api_url)
 
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the JSON response
            json_data = response.json()

            # Check if 'Result' key exists in the response
            loan_data = json_data.get('Result')
            print(loan_data)
            if loan_data:
                # Convert the fetched data to a list of dictionaries
                loan_data_list = []
                for row in loan_data:

                    loan_data_dict = {
                        "amount_requested": row.get("AMOUNT_REQUESTED"),
                        "projected_loan_to_value": row.get("PROJECTED_LOAN_TO_VALUE"),
                        "requested_close_date": row.get("REQUESTED_CLOSE_DATE"),
                        "payment_frequency": row.get("PAYMENT_FREQUENCY"),
                        "loan_purpose": row.get("LOAN_PURPOSE"),
                        "loan_purpose_other": row.get("LOAN_PURPOSE_OTHER"),
                        "source_of_funds_desc_1": row.get("SOURCE_OF_FUNDS_DESC_1"),
                        "source_of_funds_amount_1": row.get("SOURCE_OF_FUNDS_AMMOUNT_1"),
                        "use_of_funds_desc_1": row.get("USE_OF_FUNDS_DESC_1"),
                        "use_of_funds_amount_1": row.get("USE_OF_FUNDS_AMMOUNT_1"),
                        "source_of_funds_desc_2": row.get("SOURCE_OF_FUNDS_DESC_2"),
                        "source_of_funds_amount_2": row.get("SOURCE_OF_FUNDS_AMMOUNT_2"),
                        "use_of_funds_desc_2": row.get("USE_OF_FUNDS_DESC_2"),
                        "use_of_funds_amount_2": row.get("USE_OF_FUNDS_AMMOUNT_2"),
                        "source_of_funds_desc_3": row.get("SOURCE_OF_FUNDS_DESC_3"),
                        "source_of_funds_amount_3": row.get("SOURCE_OF_FUNDS_AMMOUNT_3"),
                        "use_of_funds_desc_3": row.get("USE_OF_FUNDS_DESC_3"),
                        "use_of_funds_amount_3": row.get("USE_OF_FUNDS_AMMOUNT_3"),
                        "source_of_funds_desc_4": row.get("SOURCE_OF_FUNDS_DESC_4"),
                        "source_of_funds_amount_4": row.get("SOURCE_OF_FUNDS_AMMOUNT_4"),
                        "use_of_funds_desc_4": row.get("USE_OF_FUNDS_DESC_4"),
                        "use_of_funds_amount_4": row.get("USE_OF_FUNDS_AMMOUNT_4"),
                        "loan_product": row.get("LOAN_PRODUCT"),
                        "requested_year_amortized": row.get("REQUESTED_YEAR_AMORTIZED")
                    }
                    loan_data_list.append(loan_data_dict)
                    # print(loan_data_list)


                return JSONResponse(content=loan_data_list)
            else:
                raise HTTPException(status_code=404, detail="Loan data not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")




@app.post("/updateLoan")
async def update_loan(request: Request):

    user_id = request.session.get("userId")
    if not user_id:
        return JSONResponse(status_code=401, content="User is not logged in")

    # Fetch loan data from the database using the user's session data
    loan_id = request.session.get("selectedLoanId")
    if not loan_id:
        return JSONResponse(status_code=404, content={"error": "No loan data found for editing"})

    borrowing_id = request.session.get("selectedBorrowingId")
    if not borrowing_id:
        return JSONResponse(status_code=404, content={"error": "No BORROWING_ID found for editing"})

    try:
        form_data = await request.json()
        form_data['ID'] = borrowing_id
        form_data['L_ID'] = loan_id
        form_data['EST_AMOUNT'] = None
        form_data['L_DATE'] = current_datetime

        connection = get_db_connection()
        cursor = connection.cursor()

        # Your stored procedure parameters
        
        ID = form_data.get('ID')
        L_ID = form_data.get('L_ID')
        A = form_data.get('A_REQ')
        B = form_data.get('EST_AMOUNT')
        C = form_data.get('L_V')
        D = form_data.get('REQ_DATE')
        E = form_data.get('PAYMENT')
        F = form_data.get('L_PURPOSE')
        G = form_data.get('L_PURPOSE_O')
        H = form_data.get('S_D_1')
        I = form_data.get('S_A_1')
        J = form_data.get('U_D_1')
        K = form_data.get('U_A_1')
        L = form_data.get('S_D_2')
        M = form_data.get('S_A_2')
        N = form_data.get('U_D_2')
        O = form_data.get('U_A_2')
        P = form_data.get('S_D_3')
        Q = form_data.get('S_A_3')
        R = form_data.get('U_D_3')
        S = form_data.get('U_A_3')
        T = form_data.get('S_D_4')
        U = form_data.get('S_A_4')
        V = form_data.get('U_D_4')
        W = form_data.get('U_A_4')
        Z = form_data.get('L_PRODUCT')
        X = form_data.get('REQ_YR_AMORT')
        UPDATED_DATE = form_data.get('L_DATE')

        aws_api_url = (
            "https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Loan_Application_Form/Loans/Update_data"
        )
 
        # Prepare the request body
        request_body = {
            "L_ID" : L_ID,
            "ID" : ID,
            "A" : A,
            "B" : B,
            "C" : C,
            "D" : D,
            "E" : E,
            "F" : F,
            "G" : G,
            "H" : H,
            "I" : I,
            "J" : J,
            "K" : K,
            "L" : L,
            "M" : M,
            "N" : N,
            "O" : O,
            "P" : P,
            "Q" : Q,
            "R" : R,
            "S" : S,
            "T" : T,
            "U" : U,
            "V" : V,
            "W" : W,
            "Z" : Z,
            "X" : X,
            "UPDATED_DATE" : UPDATED_DATE
        }
 
        response = requests.post(aws_api_url, json=request_body)
   
        if response.status_code == 200:
            # print("Loan Information form data successfully Updated in the database")
            return {"message": "Loan Information form data successfully Updated in the database"}
        else:
            
            return {"error": f"HTTP Error: {response.status_code}"}
 
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}

@app.get("/fetchCollateral")
async def fetch_collateral_data(request: Request):
    user_id = request.session.get("userId")
    if not user_id:
        return JSONResponse(status_code=401, content="User is not logged in")

    # Fetch loan data from the database using the user's session data
    loan_id = request.session.get("selectedLoanId")
    if not loan_id:
        return JSONResponse(status_code=404, content={"error": "No loan data found for editing"})

    try:
        # Establish a database connection
        aws_api_url = f"https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Loan_Application_Form/Collaterals/Fetch_Collateral_Data_Edit?loan_id={loan_id}"
        response = requests.get(aws_api_url)
 
        if response.status_code == 200:
            # Parse the JSON response
            json_data = response.json()

            # Check if 'Result' key exists in the response
            collateral_data = json_data.get('Result')

            if collateral_data:
                # Convert the fetched data to a list of dictionaries
                collateral_data_list = []
                for row in collateral_data:
                    collateral_data_dict = {
                        "propertyState": row.get("STATE_OF_PROPERTY_LOCATION"),
                        "propertyCounty": row.get("COUNTY_OF_PROPERTY_LOCATION"),
                        "section": row.get("SECTION"),
                        "township": row.get("TOWNSHIP"),
                        "range": row.get("RANGE"),
                        "abriviatedlegaldescription": row.get("ABBRIVIATED_LEGAL_DESCRIPTION"),
                        "landValue": row.get("ESTIMATED_VALUE_LAND"),
                        "residenceValue": row.get("ESTIMATED_VALUE_RESIDENCE"),
                        "improvementsValue": row.get("ESTIMATED_VALUE_ALL_OTHER_IMPROVEMENTS"),
                        "plantingsValue": row.get("ESTIMATED_VALUE_PERMANENT_PLANTINGS"),
                        "totalValue": row.get("ESTIMATED_VALUE_TOTAL_VALUE"),
                        "propertyLeases": "yes" if row.get("LEASES_OR_RENTAL_AGREEMENTS_ON_PROPERTY")=="yes" else "no",
                        "remainingTerm": "yes" if row.get("LEASES_OR_RENTAL_AGREEMENTS_REMAINING_FOR_3YRS_MORE")=="yes" else "no",
                        "purchaseAgreements": "yes" if row.get("AGREEMENT_FOR_PROPERTY_INCLUDE_PURCHASE_OPTION/RIGHT_OTHER")=="yes" else "no",
                        "manureEasements": "yes" if row.get("L&E_MANURE_EASEMENTS")=="on" else "no",
                        "windLeases": "yes" if row.get("L&E_WIND_LEASES,EASEMENTS_OR_AGREEMENTS")=="on" else "no",
                        "cellTower": "yes" if row.get("L&E_CELL_TOWER")=="on" else "no",
                        "oilMineralGasLeases": "yes" if row.get("L&E_OIL/MINERAL_GAS_LEASES")=="on" else "no",
                        "otherLeases": "yes" if row.get("L&E_OTHER") =="on" else "no",
                        "otherLeasesDescription": row.get("L&E_OTHER_DESC"),
                        "ownership": row.get("OWNS_COLLATERAL"),
                        "cashRent": row.get("ESTIMATED_CASH_RENT/ACRE($)"),
                        "realEstateTaxes": row.get("ESTIMATED_REAL_ESTATE_TAXES/ACRE($)"),
                        "pastureIrrigatedAcres": row.get("PASTURE_IRRIGATED_ACRES"),
                        "pastureIrrigatedValuePerAcre": row.get("PASTURE_IRRIGATED_VALUE/ACRES"),
                        "pastureNonIrrigatedAcres": row.get("PASTURE_NONIRRIGATED_ACRES"),
                        "pastureNonirrigatedValuePerAcre": row.get("PASTURE_NONIRRIGATED_VALUE/ACRES"),
                        "crpIrrigatedAcres": row.get("CRP_IRRIGATED_ACRES"),
                        "crpIrrigatedValuePerAcre": row.get("CRP_IRRIGATED_VALUE/ACRES"),
                        "crpNonIrrigatedAcres": row.get("CRP_NONIRRIGATED_ACRES"),
                        "crpNonirrigatedValuePerAcre": row.get("CRP_NONIRRIGATED_VALUE/ACRES"),
                        "woodedIrrigatedAcres": row.get("WOODED_IRRIGATED_ACRES"),
                        "woodedIrrigatedValuePerAcre": row.get("WOODED_IRRIGATED_VALUE/ACRES"),
                        "woodedNonIrrigatedAcres": row.get("WOODED_NONIRRIGATED_ACRES"),
                        "woodedNonirrigatedValuePerAcre": row.get("WOODED_NONIRRIGATED_VALUE/ACRES"),
                        "permanentPlantingIrrigatedAcres": row.get("PERMANENT_PLANTING_IRRIGATED_ACRES"),
                        "permanentPlantingIrrigatedValuePerAcre": row.get("PERMANENT_PLANTING_IRRIGATED_VALUE/ACRES"),
                        "permanentPlantingNonIrrigatedAcres": row.get("PERMANENT_PLANTING_NONIRRIGATED_ACRES"),
                        "permanentPlantingNonirrigatedValuePerAcre": row.get("PERMANENT_PLANTING_NONIRRIGATED_VALUE/ACRES"),
                        "timberlandIrrigatedAcres": row.get("TIMBERLAND_IRRIGATED_ACRES"),
                        "timberlandIrrigatedValuePerAcre": row.get("TIMBERLAND_IRRIGATED_VALUE/ACRES"),
                        "timberlandNonIrrigatedAcres": row.get("TIMBERLAND_NONIRRIGATED_ACRES"),
                        "timberlandNonirrigatedValuePerAcre": row.get("TIMBERLAND_NONIRRIGATED_VALUE/ACRES"),
                        "otherIrrigatedAcres": row.get("OTHER_IRRIGATED_ACRES"),
                        "otherIrrigatedValuePerAcre": row.get("OTHER_IRRIGATED_VALUE/ACRES"),
                        "otherNonIrrigatedAcres": row.get("OTHER_NONIRRIGATED_ACRES"),
                        "otherNonirrigatedValuePerAcre": row.get("OTHER_NONIRRIGATED_VALUE/ACRES"),
                        "totalIrrigatedAcres": row.get("TOTAL_IRRIGATED_ACRES"),
                        "totalNonIrrigatedAcres": row.get("TOTAL_NONIRRIGATED_ACRES"),
                        "totalAcres": row.get("TOTAL_ACRES"),
                        "improvements":"yes" if row.get("IMPROVEMENTS_ON_COLLATERAL")=="yes" else "no",
                        "permanentplantings": row.get("PERMANENT_PLANTING_ON_COLLATERAL"),
                        "improvements":"yes" if row.get("IMPROVEMENTS_ON_COLLATERAL")=="yes" else "no",
                        "irepayment": "yes" if row.get("I_REPRESENT_SIGNIFICANT_PORTION_OF_REPAYMENT_INCOME")=="yes" else "no",                       
                        "pprepayment": "yes" if row.get("P_REPRESENT_SIGNIFICANT_PORTION_OF_REPAYMENT_INCOME")=="yes" else "no",
                        "sixmonthwork": "yes" if row.get("IMPROVEMENT_REPAIRS_LAST_6_MONTHS")=="yes" else "no",
                        "residence": "yes" if row.get("RESIDENCE_ON_COLLATERAL")=="yes" else "no",
                        # Add more fields as needed
                        "description": row.get("IMPROVEMENTS_PERMANENT_PLANTING_DESCRIPTION"),
                        "waterRights": "yes" if row.get("WATER_IRRIGATION_WELL_RIGHTS")=="yes" else "no",
                        "waterRightsDescription": row.get("WATER_DESCRIBE"),
                        "environmentalHazard": "yes" if row.get("ENVIRONMENTAL_HAZARD_KNOW_SUSPECTED")=="yes" else "no",
                        "environmentalHazardDescription": row.get("ENVIRONMENT_DESCRIBE")
                    }
                    collateral_data_list.append(collateral_data_dict)



                return JSONResponse(content=collateral_data_list)
            else:
                raise HTTPException(status_code=404, detail="Loan data not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@app.post("/updateCollateral")
async def update_loan(request: Request):

    user_id = request.session.get("userId")
    if not user_id:
        return JSONResponse(status_code=401, content="User is not logged in")

    # Fetch loan data from the database using the user's session data
    loan_id = request.session.get("selectedLoanId")
    if not loan_id:
        return JSONResponse(status_code=404, content={"error": "No loan data found for editing"})


    try:
        form_data = await request.json()

        form_data['L_ID'] = loan_id
        form_data['L_DATE'] = current_datetime

        connection = get_db_connection()
        cursor = connection.cursor()

        # Your stored procedure parameters

        loan_id = form_data.get('L_ID')
        PS = form_data.get('SPL')
        PC = form_data.get('CPL')
        SEC = form_data.get('SEC')
        TWN = form_data.get('TOWN')
        RNG = form_data.get('RAN')
        ALD = form_data.get('ALD')
        LV = form_data.get('EVL')
        RV = form_data.get('EVR')
        IV = form_data.get('EVAOI')
        PV = form_data.get('EVPP')
        TV = form_data.get('EVTV')
        PL = form_data.get('LRAP')
        RT = form_data.get('LRAR')
        PA = form_data.get('APIPO')
        ME = form_data.get('LEME')
        WL = form_data.get('LEWL')
        CT = form_data.get('LECT')
        OMGL = form_data.get('LEOM')
        OL = form_data.get('LEO')
        OLD = form_data.get('LEOD')
        OWN = form_data.get('OC')
        CR = form_data.get('ECRA')
        RET = form_data.get('ERET')
        PIA = form_data.get('PIA')
        PIVPA = form_data.get('PIV')
        PNA = form_data.get('PNA')
        PNVPA = form_data.get('PNVA')
        CIA = form_data.get('CIA')
        CIVPA = form_data.get('CIVA')
        CNA = form_data.get('CNIA')
        CNVPA = form_data.get('CNIVA')
        WIA = form_data.get('WIA')
        WIVPA = form_data.get('WIVA')
        WNA = form_data.get('WNIA')
        WNVPA = form_data.get('WNIVA')
        PPIA = form_data.get('PLIA')
        PIV = form_data.get('PPIV')
        PPNA = form_data.get('PLNA')
        PNV = form_data.get('PPNVA')
        TLIA = form_data.get('TIA')
        TIVPA = form_data.get('TIVA')
        TLNA = form_data.get('TNIA')
        TNVPA = form_data.get('TNIVA')
        OIA = form_data.get('OIA')
        OIVPA = form_data.get('OIVA')
        ONA = form_data.get('ONIA')
        ONVPA = form_data.get('ONIVA')
        TIA = form_data.get('TOIA')
        TNA = form_data.get('TONIA')
        TA = form_data.get('TA')
        IMP = form_data.get('IOC')
        PP = form_data.get('IRSPRI')
        IR = form_data.get('PPOC')
        PPR = form_data.get('PRSIP')
        SMW = form_data.get('IRLM')
        RES = form_data.get('ROC')
        DESC = form_data.get('IPPD')
        WR = form_data.get('WIWR')
        WRD = form_data.get('WD')
        EH = form_data.get('EHKS')
        EHD = form_data.get('ED')
        Z = form_data.get('L_DATE')


        aws_api_url = (
            "https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Loan_Application_Form/Collaterals/update_data"
        )

        # Prepare the request body
        request_body = {
        "loan_id":loan_id,
        "PS" : PS,
        "PC" : PC,
        "SEC" : SEC,
        "TWN" : TWN,
        "RNG" : RNG,
        "ALD" : ALD,
        "LV" : LV,
        "RV" : RV,
        "IV" : IV,
        "PV" : PV,
        "TV" : TV,
        "PL" : PL,
        "RT" : RT,
        "PA" : PA,
        "ME" : ME,
        "WL" : WL,
        "CT" : CT,
        "OMGL" : OMGL,
        "OL" : OL,
        "OLD" : OLD,
        "OWN" : OWN,
        "CR" : CR,
        "RET" : RET,  
        "PIA" : PIA,
        "PIVPA" : PIVPA,
        "PNA" : PNA,
        "PNVPA" : PNVPA,
        "CIA" : CIA,
        "CIVPA" : CIVPA,
        "CNA" : CNA,
        "CNVPA" : CNVPA,
        "WIA" : WIA,
        "WIVPA" : WIVPA,
        "WNA" : WNA,
        "WNVPA" : WNVPA,
        "PPIA" : PPIA,
        "PIV" : PIV,
        "PPNA" : PPNA,
        "PNV" : PNV,
        "TLIA" : TLIA,
        "TIVPA" : TIVPA,
        "TLNA" : TLNA,
        "TNVPA" : TNVPA,
        "OIA" : OIA,
        "OIVPA" : OIVPA,
        "ONA" : ONA,
        "ONVPA" : ONVPA,
        "TIA" : TIA,
        "TNA" : TNA,
        "TA" : TA,
        "IMP" : IMP,
        "PP" : PP,
        "IR" : IR,
        "PPR" : PPR,
        "SMW" : SMW,
        "RES" : RES,
        "DESC" : DESC,
        "WR" : WR,
        "WRD" : WRD,
        "EH" : EH,
        "EHD" : EHD,
        "Z" : Z
        }

        response = requests.post(aws_api_url, json=request_body)
    
        if response.status_code == 200:
            print("Collateral Information form data successfully stored in the database")
            return {"message": "Collateral Information form data successfully stored in the database"}
        else:
            
            return {"error": f"HTTP Error: {response.status_code}"}

    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
#==============================================================================
        
@app.get("/fetchOtherinfo")
async def fetch_loan_data(request: Request):
    user_id = request.session.get("userId")
    if not user_id:
        return JSONResponse(status_code=401, content="User is not logged in")

    # Fetch loan data from the database using the user's session data
    loan_id = request.session.get("selectedLoanId")
    if not loan_id:
        return JSONResponse(status_code=404, content={"error": "No loan data found for editing"})


    try:
        aws_api_url = f"https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Loan_Application_Form/Other_Info/preview_OtherInfo?loan_id={loan_id}"
        response = requests.get(aws_api_url)            
    
        # Fetch all rows from the result set
        other_info = response.json()['Result']
        if other_info:
            # Convert the fetched data to a list of dictionaries
            other_info_list = []
            for row in other_info:

                other_info_dict = {
                    "judgments":"yes" if row.get("UNJUSTIFIED_JUDGEMENTS")=="yes" else "no",
                    "bankruptcy":"yes" if row.get("DECLARED_BANKRUPT")=="yes" else "no",
                    "lawsuits": "yes" if row.get("DEFENDANT_IN_LAWSUIT_OR_PENDING")=="yes" else "no",
                    "pastDue": "yes" if row.get("ANY_ACCOUNTS_PAST_DUE")=="yes" else "no",
                    "foreclosure":"yes" if row.get("PROPERTY_FORECLOSED_OR_TRANSFERED")=="yes" else "no",
                    "existingClient": row.get("EXISTING_CLIENT_OF_ORIGINATOR"),
                    "totalAcresOwned": row.get("TOTAL_ACRES_OWNED"),
                    "totalAcresRented": row.get("TOTAL_ACRES_RENTED"),
                    "assetsPledged":"yes" if row.get("ASSETS_PLEDGED_AS_SECURITY")=="yes" else "no",
                    "contingentLiabilities":"yes" if row.get("CONTINGENT_LIABILITIES")=="yes" else "no",
                    "alimonyChildSupport":"yes" if row.get("OBLIGATED_TO_PAY")=="yes" else "no",
                    "details": row.get("DESCRIPTION"),
                    "interestInCompanies":"yes" if row.get("GREATER_INTEREST_IN_OTHER_COMPANY")=="yes" else "no",
                    "residenceOnCollateral":"yes" if row.get("RESIDENCE_ON_THE_COLLATERAL")=="yes" else "no",

                }
                other_info_list.append(other_info_dict)
                print(other_info_list)

            return JSONResponse(content=other_info_list)
        else:
            raise HTTPException(status_code=404, detail="Data not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.post("/update_otherInfo")
async def update_otherInfo(request: Request):
    user_id = request.session.get("userId")
    if not user_id:
        return JSONResponse(status_code=401, content="User is not logged in")

    # Fetch loan data from the database using the user's session data
    loan_id = request.session.get("selectedLoanId")
    if not loan_id:
        return JSONResponse(status_code=404, content={"error": "No loan data found for editing"})
    try:
        # Parse the form data
        form_data = await request.json()

        # Use the form data to call the stored procedure for business entity applicants
        with get_db_connection() as conn:
            with conn.cursor() as cursor: 
                LOAN_ID=loan_id
                D = form_data.get("judgments")
                E = form_data.get("bankruptcy")
                F = form_data.get("lawsuits")
                G = form_data.get("pastDue")
                H = form_data.get("foreclosure")
                I = form_data.get("existingClient")
                J = form_data.get("totalAcresOwned")
                K = form_data.get("totalAcresRented")
                L = form_data.get("assetsPledged")
                M = form_data.get("contingentLiabilities")
                N = form_data.get("obligatedToPay")
                O = form_data.get("details")
                P = form_data.get("interestInCompanies")
                Q = form_data.get("residenceOnCollateral") 
                Z = current_datetime

        aws_api_url = (
            "https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Loan_Application_Form/Other_Info/Update_Data"
        )

        # Prepare the request body
        request_body = {
            "C": LOAN_ID,
            "D": D,
            "E": E,
            "F": F,
            "G": G,
            "H": H,
            "I": I,
            "J": J,
            "K": K,
            "L": L,
            "M": M,
            "N": N,
            "O": O,
            "P": P,
            "Q": Q,
            "Z": Z
        }

        response = requests.post(aws_api_url, json=request_body)
    
        if response.status_code == 200:
            print("OTHER INFO data successfully updated in the database")
            return {"message": "OTHER INFO data successfully updated in the database"}
        else:
            
            return {"error": f"HTTP Error: {response.status_code}"}

    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
otp_storage = {}

@app.get("/CAdmin_forgot_password", response_class=HTMLResponse)
async def forgot_password_form(request: Request):
    try:
        return templates.TemplateResponse("CAdmin_forget_password.html", {"request": request})
    except Exception as e:
        print(f"Error in forgot_password_form: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
def check_username_exists(username: str):
    try:
        print("Username", username)
        aws_api_url = f"https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Company/Company_Admin_Login?userName={username}"
        response = requests.get(aws_api_url)
       
        if response.status_code != 200:
            print("User Not Found")
            raise HTTPException(status_code=401, detail="User Not Found")
 
        user_data = response.json()
        print(f"user_data: {user_data}")

        EMAIL= user_data.get('EMAIL')
        print(f"EMAIL: {EMAIL}")
        return EMAIL
    except Exception as e:
        print(f"Error checking username existence: {e}")
        return None

@app.post("/send_otp")
async def send_otp(request: Request):
    # Get the username from the query parameters
    print("In Send OTP")
    username = request.query_params.get('username', '')
    print("Username", username)

    # Check if username exists in the database
    try:
        email = check_username_exists(username)
        if email:
            # Generate OTP
            generated_otp = str(random.randint(100000, 999999))
            print(f"Generated OTP: {generated_otp}")
            otp_storage[username] = generated_otp

            # Send OTP via email
            send_otp_email(email, generated_otp)

            # Redirect to the page where the user enters OTP and resets the password
            request.session['otp'] = generated_otp
            request.session['username'] = username

            return {"message": "OTP sent successfully"}
        else:
            return {"error": "Username not found in the database"}
    except Exception as e:
        print(f"Error in forgot_password_submit: {e}")
        return {"error": "An error occurred"}

def send_otp_email(email: str, otp: str):
    try:
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        smtp_user = "pkd17789@gmail.com"
        smtp_password = "trhk qgfy hwyw jpze"

        subject = "Password Reset OTP"
        body = f"Your OTP for password reset is: {otp}"
        sender_email = "pkd17789@gmail.com"

        message = f"Subject: {subject}\n\n{body}"

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(sender_email, email, message)
    except Exception as e:
        print(f"Error sending OTP email: {e}")
    
@app.get("/verify_otp", response_class=HTMLResponse)
async def verify_otp_form(request: Request):
    try:
        return templates.TemplateResponse("CAdmin_Forget_password_OTP.html", {"request": request})
    except Exception as e:
        print(f"Error in verify_otp_form: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@app.post("/verify_otp")
async def verify_otp(request: Request):
    # Retrieve stored OTP and email
    print("In verify OTP")
    try:
        # Retrieve stored OTP and email
        Username = request.session.get('username')
        print("Username: ",Username)

        # Check if email is stored
        if not Username:
            raise HTTPException(status_code=400, detail="UserName not found in session")

        # Retrieve stored OTP from the otp_storage dictionary
        otp = request.query_params.get('otp', '')
        stored_otp = otp_storage.get(Username)
        print("OTP: ",stored_otp)

        # Check if stored OTP exists and matches the entered OTP
        if stored_otp and otp == stored_otp:
            # Clear the stored OTP from session and otp_storage after successful verification (for demo purpose)
            del otp_storage[Username]
            del request.session['otp']
 

            return {"message": "OTP verified successfully"}
        else:
            return {"error": "Invalid OTP"}
    except Exception as e:
        print(f"Error in verify_otp: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    
@app.get("/CAdmin_set_new_password", response_class=HTMLResponse)
async def password_reset_form(request: Request):
    try:
        return templates.TemplateResponse("CAdmin_set_new_password.html", {"request": request})
    except Exception as e:
        print(f"Error in Password Reset: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/CAdmin_set_new_password")
async def set_password(
    request: Request
):
    try:
        # Retrieve parameters from the URL
        securityQuestion = request.query_params.get("securityQuestion")
        print("SQ",securityQuestion)
        securityAnswer = request.query_params.get("answer")
        print("SA",securityAnswer)
        newPassword = request.query_params.get("newPassword")
        print("NP",newPassword)
        confirmPassword = request.query_params.get("confirmPassword")
        print("CP",confirmPassword)
    # Retrieve stored security question and answer from the database
        print("In Set Password")
        username = request.session.get('username')
        print("Username",username)
            # Retrieve security question and answer from the database
        aws_api_url = f"https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Company/Company_Admin_Login?userName={username}"
        response = requests.get(aws_api_url)
       
        if response.status_code != 200:
            print("User Not Found")
            raise HTTPException(status_code=401, detail="User Not Found")
 
        user_data = response.json()
        print(f"user_data: {user_data}")
        if securityQuestion == user_data.get('SECURITY_QUES') and securityAnswer == user_data.get('SECURITY_ANS'):
            # Check if the new password matches the confirmation
            if newPassword == confirmPassword:
                # Update the password in the database
                Role = user_data.get('ROLE')
                Flag = user_data.get('FLAG')
                salt = bcrypt.gensalt()
                print("Salt", salt)
                hashed_password = bcrypt.hashpw(newPassword.encode('utf-8'), salt)
                print("Hashed password", hashed_password)
                salt_base64 = base64.b64encode(salt).decode('utf-8')
                print("salt_vase64", salt_base64)
                hashed_password_base64 = base64.b64encode(hashed_password).decode('utf-8')
                print("hashed_password_base64", hashed_password_base64)  # Use a secure hashing method
                aws_api_url = f"https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Company/CAdmin_Reset_Password"
            
                request_body = {
                    "username" : username,
                    "securityQuestion" : securityQuestion,
                    "securityAnswer" : securityAnswer,
                    "Role" : Role,
                    "Flag" : Flag,
                    "hashed_password" : hashed_password_base64,
                    "salt" : salt_base64,
                    "L_Date" : current_datetime
                }            
                response = requests.post(aws_api_url, json=request_body)
                        
                if response.status_code == 200:
                    print(f"{response.text}")
                    return {"message": f"{response.text}"}
                else:
                 
                 return {"error": f"HTTP Error: {response.status_code}", "message": f"HTTP Error: {response.text}"}

            else:
                raise HTTPException(status_code=400, detail="New password and confirmation do not match")
        else:
                raise HTTPException(status_code=400, detail="Invalid security question or answer")
    except pymysql.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

#=============================================================================================




@app.get("/fetch_company_profile", response_class=JSONResponse)
async def get_existing_loans(request: Request):
    user_id = request.session.get("userId")
    if not user_id:
        return JSONResponse(status_code=401, content="User is not logged in")
    
    userName = request.session.get("userName")
 
    try:
        ID = user_id  # Hardcoded value for testing
        aws_api_url = f"https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Company/Fetch_Company_Profile?ID={ID}"
        response = requests.get(aws_api_url)

        if response.status_code == 200:
            data = response.json()
            print('profdata', data)
            return data
            
        else:
            error_message = f"Failed to fetch data. Status code: {response.status_code}"
            return JSONResponse(status_code=500, content={"error": error_message})

    except Exception as e:
        error_message = f"An error occurred while fetching data: {str(e)}"
        return JSONResponse(status_code=500, content={"error": error_message})
 
 
#Company employee profile page
 
@app.get("/fetch_employee_profile", response_class=JSONResponse)
async def get_existing_loans(request: Request):
    user_id = request.session.get("empId")
    if not user_id:
        return JSONResponse(status_code=401, content="User is not logged in")
 
    try:
        ID = user_id  # Hardcoded value for testing
        aws_api_url = f"https://oj8mqaxze0.execute-api.us-east-1.amazonaws.com/Loan_Application_APIs/Company/Fetch_Company_Employee_Profile?ID={ID}"
        response = requests.get(aws_api_url)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            error_message = f"Failed to fetch data. Status code: {response.status_code}"
            return JSONResponse(status_code=500, content={"error": error_message})

    except Exception as e:
        error_message = f"An error occurred while fetching data: {str(e)}"
        return JSONResponse(status_code=500, content={"error": error_message})
#=============================================================================================


# Function to fetch applicant details based on the applicant type (individual or business)
@app.get("/fetchIndividualApplicant")
async def fetch_applicant_details(request: Request):
    user_id = request.session.get("empId")
    if not user_id:
        return JSONResponse(status_code=401, content="User is not logged in")

    # Fetch loan data from the database using the user's session data
    loan_id = request.session.get("selectedLoanId")
    if not loan_id:
        return JSONResponse(status_code=404, content={"error": "No loan data found for editing"})

    applicant_id = request.session.get("selectedApplicantId")
    if not applicant_id:
        return JSONResponse(status_code=404, content={"error": "No APPLICANT_ID found for editing"})

    try:
        # Establish a database connection
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Use callproc to execute the stored procedure
            cursor.callproc("EDIT_DISPLAY_APPLICANT_DETAILS", (loan_id, applicant_id))

            # Fetch all rows from the result set
            applicant_details = cursor.fetchall()

            if applicant_details:
                # Convert the fetched data to a list of dictionaries
                applicant_details_list = []
                for row in applicant_details:
                    applicant_details_dict = {
                        "applyingAs": row.get("APPLYING_AS"),
                        "typeOfApplicant": row.get("TYPE_OF_APPLICANT"),
                        "A_ID": row.get("A_ID"),
                        "relationWithPrimaryApplicant": row.get("RELATION_WITH_PRIMARY_APPLICANT"),
                        "PA_ID": row.get("PA_ID"),
                        "loanID": row.get("LOAN_ID"),
                        "firstName": row.get("FIRST_NAME"),
                        "middleName": row.get("MIDDLE_NAME"),
                        "lastName": row.get("LAST_NAME"),
                        "email": row.get("EMAIL"),
                        "telephone": row.get("TELEPHONE"),
                        "fax": row.get("FAX"),
                        "streetAddress": row.get("STREET_ADDRESS"),
                        "city": row.get("CITY"),
                        "state": row.get("STATE"),
                        "zip": row.get("ZIP"),
                        "county": row.get("COUNTY"),
                        "socialSecurity": row.get("SOCIAL_SEC"),
                        "dateOfBirth": row.get("D_O_B"),
                        "maritalStatus": row.get("MARITAL_STATUS"),
                        "yearBeginningFarming": row.get("YEAR_BEGIN_FARMING"),
                        "yearAtCurrentAddress": row.get("YEAR_AT_CURRENT_ADDRESS"),
                        "usCitizenOrPermanentAlien": row.get("US_CITIZEN_OR_PERMANENT_ALIEN"),
                        # Add other fields as needed for individual applicant details
                    }
                    applicant_details_list.append(applicant_details_dict)

                return JSONResponse(content=applicant_details_list)
            else:
                raise HTTPException(status_code=404, detail="Applicant details not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    finally:
        # Close the database connection
        connection.close()


# Function to fetch business entity details
@app.get("/fetchBusinessApplicant")
async def fetch_business_entity_details(request: Request):
    user_id = request.session.get("userId")
    if not user_id:
        return JSONResponse(status_code=401, content="User is not logged in")

    # Fetch loan data from the database using the user's session data
    loan_id = request.session.get("selectedLoanId")
    if not loan_id:
        return JSONResponse(status_code=404, content={"error": "No loan data found for editing"})

    applicant_id = request.session.get("selectedApplicantId")
    if not applicant_id:
        return JSONResponse(status_code=404, content={"error": "No APPLICANT_ID found for editing"})

    try:
        # Establish a database connection
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Use callproc to execute the stored procedure
            cursor.callproc("EDIT_DISPLAY_APPLICANT_BUSINESS_ENTITY", (loan_id, applicant_id))

            # Fetch all rows from the result set
            business_entity_details = cursor.fetchall()

            if business_entity_details:
                # Convert the fetched data to a list of dictionaries
                business_entity_details_list = []
                for row in business_entity_details:
                    business_entity_details_dict = {
                        "applyingAs": row.get("APPLYING_AS"),
                        "typeOfApplicant": row.get("TYPE_OF_APPLICANT"),
                        "A_ID": row.get("A_ID"),
                        "relationWithPrimaryApplicant": row.get("RELATION_WITH_PRIMARY_APPLICANT"),
                        "PA_ID": row.get("PA_ID"),
                        "loanID": row.get("LOAN_ID"),
                        "businessName": row.get("BUSINESS_NAME"),
                        "email": row.get("EMAIL"),
                        "taxId": row.get("FEDERAL_TAX_ID"),
                        "telephone": row.get("TELEPHONE"),
                        "fax": row.get("FAX"),
                        "streetAddress": row.get("STREET_ADDRESS"),
                        "city": row.get("CITY"),
                        "state": row.get("STATE"),
                        "zip": row.get("ZIP"),
                        "county": row.get("COUNTY"),
                        "contactNameDetails": row.get("CONTACT_NAME_DETAILS"),
                        "businessDescription": row.get("DESCRIPTION_OF_BUSINESS_OR_CUSTOM_SERVICES"),
                        "principalOfficer": row.get("PRINCIPAL_OFFICER"),
                        "homeAddress": row.get("HOME_ADDRESS"),
                        "percentOwned": row.get("Percent_OWNED"),
                        "ownershipTitle": row.get("TITLE"),
                        # Add other fields as needed for business entity details
                    }
                    business_entity_details_list.append(business_entity_details_dict)

                return JSONResponse(content=business_entity_details_list)
            else:
                raise HTTPException(status_code=404, detail="Business entity details not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    finally:
        # Close the database connection
        connection.close()


# Function to fetch additional applicant information
@app.get("/fetchAdditionalApplicantInfo")
async def fetch_additional_applicant_information(request: Request):
    user_id = request.session.get("userId")
    if not user_id:
        return JSONResponse(status_code=401, content="User is not logged in")

    # Fetch loan data from the database using the user's session data
    loan_id = request.session.get("selectedLoanId")
    if not loan_id:
        return JSONResponse(status_code=404, content={"error": "No loan data found for editing"})

    applicant_id = request.session.get("selectedApplicantId")
    if not applicant_id:
        return JSONResponse(status_code=404, content={"error": "No APPLICANT_ID found for editing"})

    try:
        # Establish a database connection
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Use callproc to execute the stored procedure
            cursor.callproc("EDIT_DISPLAY_ADDITIONAL_APPLICANT_INFORMATION", (loan_id, applicant_id))

            # Fetch all rows from the result set
            additional_applicant_info = cursor.fetchall()

            if additional_applicant_info:
                # Convert the fetched data to a list of dictionaries
                additional_applicant_info_list = []
                for row in additional_applicant_info:
                    additional_applicant_info_dict = {
                        "A_ID": row.get("A_ID"),
                        "loanID": row.get("LOAN_ID"),
                        "additionalComments": row.get("ADDITIONAL_COMMENTS"),
                        "grossFarmIncome": row.get("GROSS_FARM_INCOME"),
                        "netFarmIncome": row.get("NET_FARM_INCOME"),
                        "netNonFarmIncome": row.get("NET_NON_FARM_INCOME"),
                        "sourceOfNonFarmIncomeD1": row.get("SOURCE_OF_NON_FARM_INCOME_D1"),
                        "sourceOfNonFarmIncomeA1": row.get("SOURCE_OF_NON_FARM_INCOME_A1"),
                        "sourceOfNonFarmIncomeD2": row.get("SOURCE_OF_NON_FARM_INCOME_D2"),
                        "sourceOfNonFarmIncomeA2": row.get("SOURCE_OF_NON_FARM_INCOME_A2"),
                        "sourceOfNonFarmIncomeD3": row.get("SOURCE_OF_NON_FARM_INCOME_D3"),
                        "sourceOfNonFarmIncomeA3": row.get("SOURCE_OF_NON_FARM_INCOME_A3"),
                        "sourceOfNonFarmIncomeD4": row.get("SOURCE_OF_NON_FARM_INCOME_D4"),
                        "sourceOfNonFarmIncomeA4": row.get("SOURCE_OF_NON_FARM_INCOME_A4"),
                        "sourceOfNonFarmIncomeD5": row.get("SOURCE_OF_NON_FARM_INCOME_D5"),
                        "sourceOfNonFarmIncomeA5": row.get("SOURCE_OF_NON_FARM_INCOME_A5"),
                        "totalAssets": row.get("TOTAL_ASSETS"),
                        "totalLiabilities": row.get("TOTAL_LIABILITIES"),
                        # Add other fields as needed for additional applicant information
                    }
                    additional_applicant_info_list.append(additional_applicant_info_dict)

                return JSONResponse(content=additional_applicant_info_list)
            else:
                raise HTTPException(status_code=404, detail="Additional applicant information not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    finally:
        # Close the database connection
        connection.close()


#=====================================================================================================================

@app.post("/remove_company")
async def remove_company(request: Request):
    try:
        data = await request.json()
        admin_id = data.get("adminId")

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.callproc('DELETE_COMPANY_ADMIN', (admin_id,))
            conn.commit()

        return JSONResponse(content={"message": "Company removed successfully"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"An error occurred: {str(e)}"})
    

@app.post("/remove_borrower")
async def remove_borrower(request: Request):
    try:
        data = await request.json()
        a_id = data.get("aId")
        applicant_type = data.get("applicantType")  # Add this line to get applicantType from the request data

        with get_db_connection() as conn:
            if applicant_type == 'individual':
                cursor = conn.cursor()
                cursor.callproc('DELETE_APPLICANT_DETAILS', (a_id,))
            elif applicant_type == 'business':
                cursor = conn.cursor()
                cursor.callproc('DELETE_APPLICANT_BUSINESS_ENTITY', (a_id,))
            else:
                return JSONResponse(status_code=400, content={"error": "Invalid applicantType"})
            
            conn.commit()

        return JSONResponse(content={"message": "Borrower removed successfully"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"An error occurred: {str(e)}"})
    

@app.post("/remove_loan_info")
async def remove_loan_info(request: Request):
    try:
        data = await request.json()
        id = data.get("borrowing_id")

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.callproc('DELETE_LOAN_INFORMATION', (id,))
            conn.commit()

        return JSONResponse(content={"message": "Loan info removed successfully"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"An error occurred: {str(e)}"})
    

@app.post("/remove_collateral_info")
async def remove_collateral_info(request: Request):
    loan_id = request.session.get("selectedLoanId")
    if not loan_id:
        return JSONResponse(status_code=404, content={"error": "No loan data found for editing"})

    try:
        id=loan_id
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.callproc('DELETE_COLLATERAL_INFORMATION', (id,))
            conn.commit()

        return JSONResponse(content={"message": "Collateral removed successfully"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"An error occurred: {str(e)}"})
    

@app.post("/update_loan_status")
async def update_loan_status(request: Request):
    loan_id = request.session.get("selectedLoanId")
    if not loan_id:
        return JSONResponse(status_code=404, content={"error": "No loan data found for editing"})
    try:

        status = 'Sent to Investor'

        # Update the status using a stored procedure or direct SQL query
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.callproc("STATUS_UPDATE_FOR_INVESTORS", (status, loan_id))
            conn.commit()

        return JSONResponse(content={"message": "Status updated successfully"}, status_code=200)
    except Exception as e:
        return HTTPException(detail=str(e), status_code=500)


#==============================================================================================
# Routes to render Web pages
@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("landingpage.html", {"request": request})

@app.get("/admin.html", response_class=HTMLResponse)
async def admin_page(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

@app.get("/cadmin.html", response_class=HTMLResponse)
async def cadmin_page(request: Request):
    return templates.TemplateResponse("cadmin.html", {"request": request})

@app.get("/cemployee.html", response_class=HTMLResponse)
async def cemployee_page(request: Request):
    return templates.TemplateResponse("cemployee.html", {"request": request})    

@app.get("/adminDashboard.html", response_class=HTMLResponse)
async def admin_page(request: Request):
    return templates.TemplateResponse("adminDashboard.html", {"request": request})

@app.get("/compDashboard.html", response_class=HTMLResponse)
async def compDashboard_page(request: Request):
    return templates.TemplateResponse("compDashboard.html", {"request": request})

@app.get("/empDashboard.html", response_class=HTMLResponse)
async def empDashboard_page(request: Request):
    return templates.TemplateResponse("empDashboard.html", {"request": request})

@app.get("/application.html", response_class=HTMLResponse)
async def application_page(request: Request):
    return templates.TemplateResponse("application.html", {"request": request})

@app.get("/investorLogin.html", response_class=HTMLResponse)
async def application_page(request: Request):
    return templates.TemplateResponse("investorLogin.html", {"request": request})

@app.get("/investorDashboard.html", response_class=HTMLResponse)
async def application_page(request: Request):
    return templates.TemplateResponse("investorDashboard.html", {"request": request})    

@app.get("/analytics.html", response_class=HTMLResponse)
async def analytics_page(request: Request):
    return templates.TemplateResponse("analytics.html", {"request": request})

@app.get("/landingpage.html", response_class=HTMLResponse)
async def landing_page(request: Request):
    return templates.TemplateResponse("landingpage.html", {"request": request})

@app.get("/addnewBorrower.html", response_class=HTMLResponse)
async def addNewBorrower_page(request: Request):
    return templates.TemplateResponse("addnewBorrower.html", {"request": request})

@app.get("/addnewCollateral.html", response_class=HTMLResponse)
async def addNewCollateral_page(request: Request):
    return templates.TemplateResponse("addnewCollateral.html", {"request": request})

@app.get("/addNewLoan.html", response_class=HTMLResponse)
async def addNewLoan_page(request: Request):
    return templates.TemplateResponse("addNewLoan.html", {"request": request})


@app.get("/otherInfo.html", response_class=HTMLResponse)
async def otherInfo_page(request: Request):
    return templates.TemplateResponse("otherInfo.html", {"request": request})

@app.get("/Prog2.html", response_class=HTMLResponse)
async def Prog2_page(request: Request):
    return templates.TemplateResponse("Prog2.html", {"request": request})
@app.get("/index.html")
async def rindex_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/resetPass.html", response_class=HTMLResponse)
async def resetpass_page(request: Request):
    return templates.TemplateResponse("resetPass.html", {"request": request})

@app.get("/editBorrower.html", response_class=HTMLResponse)
async def editBorrower_page(request: Request):
    return templates.TemplateResponse("editBorrower.html", {"request": request})

@app.get("/editLoan.html", response_class=HTMLResponse)
async def editLoan_page(request: Request):
    return templates.TemplateResponse("editLoan.html", {"request": request})

@app.get("/editCollateral.html", response_class=HTMLResponse)
async def editCollateral_page(request: Request):
    return templates.TemplateResponse("editCollateral.html", {"request": request})

@app.get("/editOtherinfo.html", response_class=HTMLResponse)
async def editOtherinfo_page(request: Request):
    return templates.TemplateResponse("editOtherinfo.html", {"request": request})

@app.get("/preview.html", response_class=HTMLResponse)
async def preview_page(request: Request):
    return templates.TemplateResponse("preview.html", {"request": request})

@app.post("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    request.session.clear()
    return templates.TemplateResponse("landingpage.html", {"request": request})

@app.get("/setPassEmp.html", response_class=HTMLResponse)
async def setPassEmp(request: Request):
    return templates.TemplateResponse("setPassEmp.html", {"request": request})

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", port=8000)