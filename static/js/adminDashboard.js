


// Sidebar toggle
const sidebarToggle = document.querySelector("#sidebar-toggle");
sidebarToggle.addEventListener("click", () => {
  document.querySelector("#sidebar").classList.toggle("collapsed");
});

// Theme toggle
document.querySelector(".theme-toggle").addEventListener("click", () => {
  toggleLocalStorage();
  toggleRootClass();
});

function toggleRootClass() {
  const current = document.documentElement.getAttribute("data-bs-theme");
  const inverted = current === "dark" ? "light" : "dark";
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

// Add New Company link
const addNewLink = document.querySelector('.sidebar-link[data-bs-target="#addNew"]');
const addNewCompanyForm = document.getElementById('addNewCompanyForm');

addNewLink.addEventListener('click', (event) => {
  event.preventDefault();
  hideElements(['hideElement1', 'hideElement2', 'showExistingCompany', 'resetPasswordForm','profileSection']);
  addNewCompanyForm.style.display = 'block';
});


//=================================================


// Profile link
const profileLink = document.querySelector('.navbar-nav .dropdown-item:first-child');
const profileSection = document.getElementById('profileSection');
const profileContent = document.getElementById('profileContent');

profileLink.addEventListener('click', async (event) => {
    event.preventDefault();
    hideElements(['hideElement1', 'hideElement2', 'showExistingCompany', 'resetPasswordForm', 'addNewCompanyForm']);
    profileSection.style.display = 'block';

    // Fetch user details from the server (replace '/get_user_profile' with your actual endpoint)
    try {
        const response = await fetch('/get_user_profile');
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const userData = await response.json();

        // Update profile content with fetched user details
        updateProfileContent(userData);
    } catch (error) {
        console.error('Error fetching user profile data:', error);
    }
});

function updateProfileContent(userData) {
    const profileName = document.getElementById('profileName');
    const profileEmail = document.getElementById('profileEmail');
    const profileID = document.getElementById('profileID');
    const profilecontact=document.getElementById('profileContact');

    profileName.innerText = userData.name;
    profileEmail.innerText = userData.email;
    profileID.innerText = userData.id;
    profileContact.innerText=userData.contact;
}

//===============================================




// Reset Password link
const resetPassLink = document.querySelector('.sidebar-link[data-bs-target="#resetPass"]');
const resetPassForm = document.getElementById('resetPasswordForm');

resetPassLink.addEventListener('click', (event) => {
  event.preventDefault();
  hideElements(['hideElement1', 'hideElement2', 'showExistingCompany', 'addNewCompanyForm' ,'profileSection']);
  resetPassForm.style.display = 'block';
});

// Existing Company link
const existingCompanyLink = document.querySelector('.sidebar-link[data-bs-target="#existingCompany"]');
const showExistingCompany = document.getElementById('showExistingCompany');

existingCompanyLink.addEventListener('click', (event) => {
  event.preventDefault();
  hideElements(['hideElement1', 'hideElement2', 'resetPasswordForm', 'addNewCompanyForm','profileSection']);
  
  showExistingCompany.style.display = 'block';
});


// Hide elements by IDs
function hideElements(idsArray) {
  idsArray.forEach((id) => {
    const element = document.getElementById(id);
    if (element) { 
      element.style.display = 'none';
    }
  });
}

// Reset Password form submission
const resetPasswordForm = document.getElementById('resetpasswordform');

resetPasswordForm.addEventListener('submit', async (event) => {
  event.preventDefault();

  const newPassword = document.getElementById('password').value;
  const confirmPassword = document.getElementById('cPassword').value;

  if (!newPassword || !confirmPassword) {
    alert('Please enter and confirm the new password.');
    return;
  }

  if (newPassword !== confirmPassword) {
    alert('Passwords do not match. Please try again.');
    return;
  }

  try {
    // Assuming '/reset_password' is the endpoint for password reset
    const response = await fetch('/admin_reset_password', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ newPassword }), // Send the new password to the server
    });

    if (response.ok) {
      alert('Password updated successfully.');
      // Optionally, close the reset password form or redirect to another page
      // resetPasswordForm.reset(); // Reset form fields
      // Additional logic after successful password reset
    } else {
      alert('Failed to update password. Please try again later.');
      // Handle error scenarios if needed
    }
  } catch (error) {
    console.error('Error:', error);
    alert('An error occurred. Please try again later.');
  }
});

// Fetch and display existing companies
window.addEventListener('load', () => {
  fetchExistingCompanies();
});

// Function to fetch existing companies
async function fetchExistingCompanies() {
  try {
    const response = await fetch('/get_existing_companies');
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    const data = await response.json();

    // Populate the table with fetched data
    renderExistingCompanies(data.data);
    
  } catch (error) {
    console.error('Error fetching existing companies data:', error);
  }
}

// Function to render existing companies
function renderExistingCompanies(companies) {
  const tableBody = document.getElementById('existing-comp-tablebody');

  tableBody.innerHTML = '';

  companies.forEach((company) => {
    const newRow = document.createElement('tr');
    newRow.innerHTML = `
      <td>${company.ADMIN_ID}</td>
      <td>${company.ROLE}</td>
      <td>${company.COMPANY_NAME}</td>
      <td>${company.EMAIL}</td>
      <td>${company.CONTACT}</td>
      <td>
        <button class="remove-button" data-admin-id="${company.ADMIN_ID}">Remove</button>
      </td>
    `;
    tableBody.appendChild(newRow);

    // Add event listener to the "Remove" button
    const removeButton = newRow.querySelector('.remove-button');
    removeButton.addEventListener('click', () => removeCompany(company.ADMIN_ID, newRow));
  });
}

// Function to remove a company
async function removeCompany(adminId, rowElement) {
  try {
    const response = await fetch('/remove_company', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ adminId }),
    });

    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    // Remove the row from the table after successful removal
    rowElement.remove();
  } catch (error) {
    console.error('Error removing company:', error);
  }
}

// Call fetchExistingCompanies to initialize the table
fetchExistingCompanies();


// Registration of new company
const signUpForm = document.getElementById('companyRegistrationForm');
const errorMessage = document.getElementById('error-message');

signUpForm.addEventListener('submit', async (event) => {
  event.preventDefault();

  const formData = new FormData(signUpForm);
  const formDataObject = {};

  formData.forEach((value, key) => {
    formDataObject[key] = value;
  });

  
  try {
    const response = await fetch('/register_company', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formDataObject),
    });

    if (response.ok) {
      const responseData = await response.json();
      handleSuccessfulRegistration(responseData);
    } else {
      // Handle error scenarios
    }
  } catch (error) {
    errorMessage.innerText = 'An error occurred while processing your request.';
    console.error('Error:', error);
  }
});
function handleSuccessfulRegistration(data) {
  const successMessageContainer = document.getElementById('success-message');
  const errorMessageContainer = document.getElementById('error-message1');

  if ('error' in data) {
    errorMessageContainer.innerText = data.error;
    successMessageContainer.style.display = 'none';  // Hide success message container
    alert("There are some error registering company")
  } else {
    const successMessage = `Successfully Registered\n${data.message}\nUser ID: ${data.userid}\nPassword: ${data.companyEmail ? data.companyEmail.split('@')[0] : ''}`;
    alert(successMessage);
    //const successMessage = `${data.message}\nUser ID: ${data.userid}\nPassword: ${data.companyEmail.split('@')[0]}`;
    successMessageContainer.innerText = successMessage;
    successMessageContainer.style.display = 'block';  // Display success message container
    errorMessageContainer.innerText = '';  // Clear any previous error messages

    // Optionally, you can reset the form or perform other actions here
    signUpForm.reset();
  }
}



//toggle for selected dashboard elements

document.addEventListener("DOMContentLoaded", function() {
  // Get references to the dashboard elements
  const profileElement=document.getElementById("profileElement");
  const dashboardElement = document.getElementById("dashboardElement");
  const existingElement=document.getElementById("existingElement");
  const resetPasswordElement = document.getElementById("resetPasswordElement");
  const addEmployeeElement = document.getElementById("addEmployeeElement");
  const logoutElement=document.getElementById("logoutElement");
 
  
  // Add the "selected" class to the Dashboard element by default
  dashboardElement.classList.add("selected");


  // Add click event listeners to toggle the "selected" class 
  dashboardElement.addEventListener("click", function() {
    dashboardElement.classList.toggle("selected");
    profileElement.classList.remove("selected");
    existingElement.classList.remove("selected");
    resetPasswordElement.classList.remove("selected");
    addEmployeeElement.classList.remove("selected");
    logoutElement.classList.remove("selected");
    
  });

  resetPasswordElement.addEventListener("click", function() {
    resetPasswordElement.classList.toggle("selected");
    profileElement.classList.remove("selected");
    existingElement.classList.remove("selected");
    dashboardElement.classList.remove("selected");
    addEmployeeElement.classList.remove("selected");
    logoutElement.classList.remove("selected");
   
  });

  addEmployeeElement.addEventListener("click", function() {
    addEmployeeElement.classList.toggle("selected");
    profileElement.classList.remove("selected");
    existingElement.classList.remove("selected");
    dashboardElement.classList.remove("selected");
    resetPasswordElement.classList.remove("selected");
    logoutElement.classList.remove("selected");
   
  });
  logoutElement.addEventListener("click", function() {
    logoutElement.classList.toggle("selected");
    profileElement.classList.remove("selected");
    existingElement.classList.remove("selected");
    dashboardElement.classList.remove("selected");
    resetPasswordElement.classList.remove("selected");
    addEmployeeElement.classList.remove("selected");
   
  });
  existingElement.addEventListener("click", function() {
    existingElement.classList.toggle("selected");
    profileElement.classList.remove("selected");
    logoutElement.classList.remove("selected");
    dashboardElement.classList.remove("selected");
    resetPasswordElement.classList.remove("selected");
    addEmployeeElement.classList.remove("selected");
   
  });

  profileElement.addEventListener("click", function() {
    profileElement.classList.toggle("selected");
    existingElement.classList.remove("selected");
    logoutElement.classList.remove("selected");
    dashboardElement.classList.remove("selected");
    resetPasswordElement.classList.remove("selected");
    addEmployeeElement.classList.remove("selected");
   
  });
 
});




