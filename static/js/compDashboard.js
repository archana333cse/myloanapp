// Function to toggle sidebar
document.querySelector("#sidebar-toggle").addEventListener("click", function () {
  document.querySelector("#sidebar").classList.toggle("collapsed");
});

// Function to toggle theme
document.querySelector(".theme-toggle").addEventListener("click", () => {
  toggleLocalStorage();
  toggleRootClass();
});

function toggleRootClass() {
  const current = document.documentElement.getAttribute("data-bs-theme");
  const inverted = current == "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-bs-theme", inverted);
}

function toggleLocalStorage() {
  if (isLight()) {
    localStorage.removeItem("light");
  } else {
    localStorage.setItem("light", "set");
  }
}

function isLight() {
  return localStorage.getItem("light");
}

if (isLight()) {
  toggleRootClass();
}

//======================profilel section============================

// Add click event listener to the "Profile" link in the dropdown menu
const profileLink = document.querySelector('.navbar-nav .dropdown-item:first-child');
const profileSection = document.getElementById('profileSection');

profileLink.addEventListener('click', function (event) {
  // Prevent the default link behavior
  event.preventDefault();

  // Hide specific elements
  document.getElementById('hideElement1').style.display = 'none';
  document.getElementById('hideElement2').style.display = 'none';
  //document.getElementById('hideElement3').style.display = 'none';
  document.getElementById('addNewEmployeeForm').style.display = 'none';
  
  document.getElementById('resetPasswordForm').style.display = 'none';
  

  // Show the profile section
  profileSection.style.display = 'block';

 
  
  // Call the function to update profile details (you need to implement this function)
  fetchCompanyProfile();
});


// Function to fetch company profile data from the backend
async function fetchCompanyProfile() {
  try {
    const response = await fetch('/fetch_company_profile');
    const result = await response.json();

    // Check for errors in the response
    if (response.status === 200) {
      const data = result.Result; // Use 'Result' key
      if (data && data.length > 0) {
        // Assuming you have a single result for a specific user ID
        const companyProfile = data[0];

        // Update the HTML elements with the fetched data
        document.getElementById('ID').innerText = companyProfile.ADMIN_ID;
        document.getElementById('userName').innerText = companyProfile.USERNAME;
        document.getElementById('Name').innerText = companyProfile.COMPANY_NAME;
        document.getElementById('role').innerText = companyProfile.ROLE;
        document.getElementById('Email').innerText = companyProfile.EMAIL;
        document.getElementById('Contact').innerText = companyProfile.CONTACT;

        // You can add more elements based on your data structure
      } else {
        console.error('No data found for editing.');
      }
    } else if (response.status === 401) {
      console.error('User is not logged in.');
    } else if (response.status === 404) {
      console.error('No data found for editing.');
    } else {
      console.error('An error occurred while fetching data.');
    }
  } catch (error) {
    console.error('Error fetching company profile data:', error);
  }
}








// Toggle employee registration form
const addNewLink = document.querySelector('.sidebar-link[data-bs-target="#addNew"]');
const addNewEmployeeForm = document.getElementById('addNewEmployeeForm');

addNewLink.addEventListener('click', function (event) {
  event.preventDefault();
  document.getElementById('hideElement1').style.display = 'none';
  document.getElementById('hideElement2').style.display = 'none';
 // document.getElementById('hideElement3').style.display = 'none';
  document.getElementById('resetPasswordForm').style.display = 'none';
  document.getElementById('profileSection').style.display='none';
  document.getElementById('showExistingEmployee').style.display='none';

  addNewEmployeeForm.style.display = 'block';
});

// Toggle  existing employee 
const existingLink = document.querySelector('.sidebar-link[data-bs-target="#existingEmployee"]');
const showExistingEmployee = document.getElementById('showExistingEmployee'); 

existingLink.addEventListener('click', function (event) {
  event.preventDefault();
  document.getElementById('hideElement1').style.display = 'none';
  document.getElementById('hideElement2').style.display = 'none';
  document.getElementById('addNewEmployeeForm').style.display = 'none';
  document.getElementById('resetPasswordForm').style.display = 'none';
  document.getElementById('profileSection').style.display='none';
  showExistingEmployee.style.display = 'block';
});


// Reset Password form
const resetPasswordForm = document.getElementById('resetPasswordForm');
const resetpasswordform=document.getElementById('resetpasswordform');

document.querySelector('.sidebar-link[data-bs-target="#resetPass"]').addEventListener('click', function (event) {
  event.preventDefault();
  document.getElementById('hideElement1').style.display = 'none';
  document.getElementById('hideElement2').style.display = 'none';
  //document.getElementById('hideElement3').style.display = 'none';
  document.getElementById('addNewEmployeeForm').style.display = 'none';
  document.getElementById('profileSection').style.display='none';
  document.getElementById('showExistingEmployee').style.display='none';

  resetPasswordForm.style.display = 'block';
});

resetPasswordForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const oldPassword = document.getElementById('oldPassword').value;
  const newPassword = document.getElementById('npassword').value;
  const confirmPassword = document.getElementById('cPassword').value;

  if (!oldPassword || !newPassword || !confirmPassword || newPassword !== confirmPassword) {
    alert('Please enter and confirm a matching password.');
    return;
  }
  if(oldPassword===newPassword){
    alert('old password and new password can not be same!');
  }

  try {
    const response = await fetch('/cadmin_reset_password', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ oldPassword, newPassword, cPassword: confirmPassword }),
    });

    if (response.ok) {
      alert('Password updated successfully.');
      //resetpasswordform.reset(); // Reset the password form
      //resetPasswordForm.style.display = 'block';
     
    } else {
      const responseData = await response.json();
      alert(responseData.error || 'Failed to update password. Please try again later.');

     
    }
   
  } catch (error) {
    console.error('Error:', error);
    alert('An error occurred. Please try again later.');
  }
});

// Fetch existing employees
async function fetchExistingEmployees() {
  try {
    const response = await fetch('/get_existing_employees');
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    const data = await response.json();
    const tableBody = document.getElementById('existing-emp-tablebody');
    tableBody.innerHTML = '';

    data.data.forEach(row => {
      const newRow = document.createElement('tr');
      newRow.innerHTML = `
        <td>${row.E_ID}</td>
        <td>${row.NAME}</td>
        <td>${row.EMAIL}</td>
        <td>${row.CONTACT}</td>
        <td>
          <button class="remove-button" disabled>Remove</button>
          <button class="visit-button" disabled>Visit</button>
        </td>
      `;
      tableBody.appendChild(newRow);
    });
  } catch (error) {
    console.error('Error fetching existing employees data:', error);
  }
}

window.addEventListener('load', fetchExistingEmployees);


// Function to handle employee registration form submission
document.addEventListener('DOMContentLoaded', () => {
  const signUpForm = document.getElementById('employeeRegistrationForm');
  const errorMessage = document.getElementById('error-message');

  signUpForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const formData = new FormData(signUpForm);
    const formDataObject = {};
    formData.forEach((value, key) => {
      formDataObject[key] = value;
    });

    try {
      const response = await fetch('/register_company_employee', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formDataObject),
      });

      if (response.ok) {
        const responseData = await response.json();
        if ('error' in responseData) {
          errorMessage.innerText = responseData.error;
        } else {
          const message = responseData.message;
          const userid = responseData.userid;
          const empEmail = formDataObject.empEmail || ''; // Check if empEmail exists, if not, set an empty string
          alert(`${message}\nUser ID: ${userid}\nPassword: ${empEmail.split('@')[0]}`);
          //location.reload();
    signUpForm.reset();

        }
      } else {
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
          const errorResponse = await response.json();
          errorMessage.innerText = errorResponse.error;
        } else {
          errorMessage.innerHTML = await response.text();
        }
      }
    } catch (error) {
      errorMessage.innerText = 'An error occurred while processing your request.';
      console.error('Error:', error);
    }
  });
});

//toggle for selected dashboard elements

document.addEventListener("DOMContentLoaded", function() {
  // Get references to the dashboard elements
  const dashboardElement = document.getElementById("dashboardElement");
  const existingElement=document.getElementById('existingElement');
  const resetPasswordElement = document.getElementById("resetPasswordElement");
  const addEmployeeElement = document.getElementById("addEmployeeElement");
  const logoutElement=document.getElementById("logoutElement");
  const profileElement=document.getElementById('profileElement');
  
  // Add the "selected" class to the Dashboard element by default
  dashboardElement.classList.add("selected");


  // Add click event listeners to toggle the "selected" class
  dashboardElement.addEventListener("click", function() {
    dashboardElement.classList.toggle("selected");
    profileElement.classList.remove('selected');
    existingElement.classList.remove('selected');
    resetPasswordElement.classList.remove("selected");
    addEmployeeElement.classList.remove("selected");
    logoutElement.classList.remove("selected");
  });

  resetPasswordElement.addEventListener("click", function() {
    resetPasswordElement.classList.toggle("selected");
    profileElement.classList.remove('selected');
    existingElement.classList.remove('selected');
    dashboardElement.classList.remove("selected");
    addEmployeeElement.classList.remove("selected");
    logoutElement.classList.remove("selected");
  });

  addEmployeeElement.addEventListener("click", function() {
    addEmployeeElement.classList.toggle("selected");
    profileElement.classList.remove('selected');
    existingElement.classList.remove('selected');
    dashboardElement.classList.remove("selected");
    resetPasswordElement.classList.remove("selected");
    logoutElement.classList.remove("selected");
  });
  logoutElement.addEventListener("click", function() {
    logoutElement.classList.toggle("selected");
    profileElement.classList.remove('selected');
    existingElement.classList.remove('selected');
    dashboardElement.classList.remove("selected");
    resetPasswordElement.classList.remove("selected");
    addEmployeeElement.classList.remove("selected");
  });
  existingElement.addEventListener("click", function() {
    existingElement.classList.toggle("selected");
    profileElement.classList.remove('selected');
    logoutElement.classList.remove('selected');
    dashboardElement.classList.remove("selected");
    resetPasswordElement.classList.remove("selected");
    addEmployeeElement.classList.remove("selected");
  });

  profileElement.addEventListener("click", function() {
    profileElement.classList.toggle("selected");
    existingElement.classList.remove('selected');
    logoutElement.classList.remove('selected');
    dashboardElement.classList.remove("selected");
    resetPasswordElement.classList.remove("selected");
    addEmployeeElement.classList.remove("selected");
  });


});

