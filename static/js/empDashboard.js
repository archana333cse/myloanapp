// Sidebar toggle
const sidebarToggle = document.querySelector("#sidebar-toggle")
sidebarToggle.addEventListener("click", function () {
  document.querySelector("#sidebar").classList.toggle("collapsed");
});

// theme toggle

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

//=====================toggle registeration form===========================

// Get the elements
const addNewLink = document.querySelector('.sidebar-link[data-bs-target="#addNew"]');
const addNewApplicationForm = document.getElementById('addNewApplicationForm');

// Add click event listener to the "Add New Company" link
addNewLink.addEventListener('click', function (event) {
  // Prevent the default link behavior
  event.preventDefault();

  // Hide specific elements
  document.getElementById('hideElement1').style.display = 'none';
  document.getElementById('hideElement2').style.display = 'none';
  document.getElementById('hideElement3').style.display = 'none';
  document.getElementById('resetPasswordForm').style.display = 'none';
  document.getElementById('showExistingApplication').style.display='none';
  document.getElementById('profileSection').style.display='none';

  // Show the registration form
  addNewApplicationForm.style.display = 'block';
});



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
  document.getElementById('hideElement3').style.display = 'none';
  document.getElementById('addNewApplicationForm').style.display = 'none';
  document.getElementById('resetPasswordForm').style.display = 'none';
  document.getElementById('showExistingApplication').style.display='none';
  document.getElementById('showAnalytics').style.display='none';
  document.getElementById('showUtilities').style.display='none';

  // Show the profile section
  profileSection.style.display = 'block';

  
  
  // Call the function to update profile details (you need to implement this function)
  fetchEmployeeProfile();
});

// Function to fetch company profile data from the backend
async function fetchEmployeeProfile() {
  try {
      const response = await fetch('/fetch_employee_profile');
      const result = await response.json();

      // Check for errors in the response
      if (response.status === 200) {
        const data = result.Result;
          if (data && data.length > 0) {
              // Assuming you have a single result for a specific loan ID
              const companyProfile = data[0];

              // Update the HTML elements with the fetched data
              document.getElementById('empId').innerText = companyProfile.E_ID;
              document.getElementById('compId').innerText = companyProfile.COMP_ID;
              document.getElementById('userName').innerText = companyProfile.USERNAME;
              document.getElementById('empName').innerText = companyProfile.NAME;
              document.getElementById('empEmail').innerText = companyProfile.EMAIL;
              document.getElementById('empContact').innerText = companyProfile.CONTACT;

              // You can add more elements based on your data structure
          } else {
              console.error('No data found for editing.');
          }
      } else if (response.status === 401) {
          console.error('User is not logged in.');
      } else if (response.status === 404) {
          console.error('No loan data found for editing.');
      } else {
          console.error('An error occurred while fetching data.');
      }
  } catch (error) {
      console.error('Error fetching company profile data:', error);
  }
}

// Call the function to fetch company profile data
fetchEmployeeProfile();




//============================show existing element===============================

// Get the elements
const existingLink = document.querySelector('.sidebar-link[data-bs-target="#existingApplication"]');
const showExistingApplication = document.getElementById('showExistingApplication');

// Add click event listener to the "Existing Application" link
existingLink.addEventListener('click', function (event) {
    // Prevent the default link behavior
    event.preventDefault();

    // Hide specific elements
    document.getElementById('hideElement1').style.display = 'none';
    document.getElementById('hideElement2').style.display = 'none';
    document.getElementById('hideElement3').style.display = 'block';
    document.getElementById('addNewApplicationForm').style.display = 'none';
    document.getElementById('resetPasswordForm').style.display = 'none';
    document.getElementById('profileSection').style.display='none';

    // Show the "Existing Application" section
    showExistingApplication.style.display = 'block';

    // Fetch and update the existing applications table
    fetchExistingApplication();
});
//======================================================

// Get the elements
const analyticLink = document.querySelector('.sidebar-link[data-bs-target="#analytics"]');
const showAnalytics = document.getElementById('showAnalytics');

// Add click event listener to the "Existing Application" link
analyticLink.addEventListener('click', function (event) {
    // Prevent the default link behavior
    event.preventDefault();

    // Hide specific elements
    document.getElementById('hideElement1').style.display = 'none';
    document.getElementById('hideElement2').style.display = 'none';
    document.getElementById('hideElement3').style.display = 'none';
    document.getElementById('addNewApplicationForm').style.display = 'none';
    document.getElementById('resetPasswordForm').style.display = 'none';
    document.getElementById('showExistingApplication').style.display='none';
    document.getElementById('profileSection').style.display='none';
    // Show the "Existing Application" section
    showAnalytics.style.display = 'block';

});

//====================================================================

//======================reset password form==========================
const addNewLink1 = document.querySelector('.sidebar-link[data-bs-target="#resetPass"]');
const resetPassForm = document.getElementById('resetPasswordForm');
addNewLink1.addEventListener('click', function (event) {
  event.preventDefault();
  // Hide specific elements
  document.getElementById('hideElement1').style.display = 'none';
  document.getElementById('hideElement2').style.display = 'none';
  document.getElementById('hideElement3').style.display = 'none';
  document.getElementById('addNewApplicationForm').style.display = 'none';
  document.getElementById('showExistingApplication').style.display='none';
  document.getElementById('profileSection').style.display='none';

  // Show the registration form
  resetPassForm.style.display = 'block';

});

resetPassForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const oldPassword = document.getElementById('oldPassword').value;
  const newPassword = document.getElementById('npassword').value;
  const confirmPassword = document.getElementById('cPassword').value;

  if (!oldPassword || !newPassword || !confirmPassword || newPassword !== confirmPassword) {
    alert('Please enter and confirm a matching password.');
    return;
  }
  if (oldPassword === newPassword) {
    alert('old password and new password can not be same!');
  }

  try {
    const response = await fetch('/cemp_reset_password', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ oldPassword, newPassword, cPassword: confirmPassword }),
    });

    if (response.ok) {
      alert('Password updated successfully.');
      //resetPasswordForm.style.display = 'none';
    } else {
      const responseData = await response.json();
      alert(responseData.error || 'Failed to update password. Please try again later.');
    }
  } catch (error) {
    console.error('Error:', error);
    alert('An error occurred. Please try again later.');
  }
});

// ------------------------------------------------------------------------------------------------ 
// Existing application

async function fetchExistingApplication() {
  try {
    const response = await fetch('/get_existing_applications');
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    const data = await response.json();
    console.log('Received data:', data);

    // Get a reference to the table body element
    const tableBody = document.getElementById('table-body');

    // Clear the existing table rows
    tableBody.innerHTML = '';

    // Loop through the fetched data and create table rows
    data.data.forEach(row => {
      const newRow = document.createElement('tr');
      newRow.innerHTML = `
        <td>${row.LOAN_ID}</td>
        <td>${row.APPLICATION_NAME}</td>
        <td>${row.AMOUNT_REQUESTED}</td>
        <td>${row.STATUS}</td>
        <td>
          <button class="edit-button" onclick="handleEdit(${row.LOAN_ID})">Edit</button>
        </td>
      `;
      tableBody.appendChild(newRow);
    });
  } catch (error) {
    console.error('Error fetching data:', error);
  }
}

async function handleEdit(loanId) {
  try {
    const response = await fetch('/store_loan_id', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ loan_id: loanId }),
    });

    if (!response.ok) {
      throw new Error('Failed to store loan ID');
    }

    // Optionally, handle success or perform other actions after storing the ID
    window.location.href = '/application.html'; // Redirect to another page after storing ID
  } catch (error) {
    console.error('Error storing loan ID:', error);
    // Handle the error, show an alert, or perform other actions
  }
}

// Call fetchExistingApplication() when the page loads to populate the table
window.addEventListener('load', () => {
  fetchExistingApplication();
});




//===============================================================


// --------------------------------------------------------


// ===================================start application==============================================
document.addEventListener('DOMContentLoaded', function () {
  const applicationForm = document.getElementById('applicationForm');

  applicationForm.addEventListener('submit', async function (event) {
    event.preventDefault();

    // Retrieve form data
    const formData = new FormData(applicationForm);
    const borrowerName = formData.get('borrowerName');
    const amountRequested = formData.get('amountRequested');
    const CompId = formData.get('CompId');

    // Validate form data (add your own validation as needed)
    if (!borrowerName || !amountRequested || !CompId) {
      alert('Please fill in all the required fields.');
      return;
    }

    // Prepare JSON data
    const jsonData = {
      borrowerName,
      amountRequested,
      CompId,
    };

    try {
      // Send the form data to the server
      const response = await fetch('/start_application', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(jsonData),
      });

      if (response.ok) {
        const responseData = await response.json();
        alert('Application data submitted successfully');
        console.log('Response from backend:', responseData);

        // Optionally, you can reset the form after successful submission
        applicationForm.reset();
        // Redirect to application.html after successful submission
        window.location.href = '/application.html';

        // Fetch and update the existing applications table
        fetchExistingApplication();
      } else {
        alert('Failed to submit application data');
      }
    } catch (error) {
      console.error('Error:', error); 
      alert('An error occurred while submitting the form');
    }
  });
});







// Add an event listener to the reset password form
const resetPasswordForm = document.getElementById('resetpasswordform');
resetPasswordForm.addEventListener('submit', async (event) => {
  event.preventDefault();

  const newPassword = document.getElementById('password').value;
  const confirmPassword = document.getElementById('cPassword').value;

  // Validate that newPassword and confirmPassword are not empty
  if (!newPassword || !confirmPassword) {
    alert('Please enter a password and confirm it.');
    return;
  }

  // Validate that newPassword matches confirmPassword
  if (newPassword !== confirmPassword) {
    alert('Passwords do not match. Please try again.');
    return;
  }

  // Send the newPassword to the FastAPI route for resetting the password
  try {
    const response = await fetch('/reset_password', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ newPassword }), // Don't include user_id here
    });

    if (response.ok) {
      alert('Password updated successfully.');
      closeResetPasswordPopup();
    } else {
      alert('Failed to update password. Please try again later.');
    }
  } catch (error) {
    console.error('Error:', error);
    alert('An error occurred. Please try again later.');
  }
});

//toggle for selected dashboard elements

document.addEventListener("DOMContentLoaded", function () {
  // Get references to the dashboard elements
  const dashboardElement = document.getElementById("dashboardElement");
  const profileElement=document.getElementById('profileElement');
  const analyticsElement = document.getElementById("analyticsElement");
  //const utilitiesElement = document.getElementById("utilitiesElement");
  const existingElement=document.getElementById("existingElement");
  const resetPasswordElement = document.getElementById("resetPasswordElement");
  const addEmployeeElement = document.getElementById("addEmployeeElement");
  const logoutElement = document.getElementById("logoutElement");

  // Add the "selected" class to the Dashboard element by default
  dashboardElement.classList.add("selected");


  // Add click event listeners to toggle the "selected" class
  dashboardElement.addEventListener("click", function () {
    dashboardElement.classList.toggle("selected");
    profileElement.classList.remove('selected');
    analyticsElement.classList.remove("selected");
    //utilitiesElement.classList.remove("selected");
    existingElement.classList.remove("selected");
    resetPasswordElement.classList.remove("selected");
    addEmployeeElement.classList.remove("selected");
    logoutElement.classList.remove("selected");
  });

  resetPasswordElement.addEventListener("click", function () {
    resetPasswordElement.classList.toggle("selected");
    profileElement.classList.remove('selected');
    analyticsElement.classList.remove("selected");
    //utilitiesElement.classList.remove("selected");
    existingElement.classList.remove("selected");
    dashboardElement.classList.remove("selected");
    addEmployeeElement.classList.remove("selected");
    logoutElement.classList.remove("selected");
  });

  addEmployeeElement.addEventListener("click", function () {
    addEmployeeElement.classList.toggle("selected");
    profileElement.classList.remove('selected');
    analyticsElement.classList.remove("selected");
    //utilitiesElement.classList.remove("selected");
    existingElement.classList.remove("selected");
    dashboardElement.classList.remove("selected");
    resetPasswordElement.classList.remove("selected");
    logoutElement.classList.remove("selected");
  });
  logoutElement.addEventListener("click", function () {
    logoutElement.classList.toggle("selected");
    profileElement.classList.remove('selected');
    analyticsElement.classList.remove("selected");
    //utilitiesElement.classList.remove("selected");
    existingElement.classList.remove("selected");
    dashboardElement.classList.remove("selected");
    resetPasswordElement.classList.remove("selected");
    addEmployeeElement.classList.remove("selected");
  });
  analyticsElement.addEventListener("click", function () {
    analyticsElement.classList.toggle("selected");
    profileElement.classList.remove('selected');
    logoutElement.classList.remove("selected");
    //utilitiesElement.classList.remove("selected");
    existingElement.classList.remove("selected");
    dashboardElement.classList.remove("selected");
    resetPasswordElement.classList.remove("selected");
    addEmployeeElement.classList.remove("selected");
  });
 
  existingElement.addEventListener("click", function () {
    existingElement.classList.toggle("selected");
    profileElement.classList.remove('selected');
    //utilitiesElement.classList.remove("selected");
    analyticsElement.classList.remove("selected");
    logoutElement.classList.remove("selected");
    dashboardElement.classList.remove("selected");
    resetPasswordElement.classList.remove("selected");
    addEmployeeElement.classList.remove("selected");
  });

  profileElement.addEventListener("click", function () {
    profileElement.classList.toggle("selected");
    existingElement.classList.remove('selected');
    //utilitiesElement.classList.remove("selected");
    analyticsElement.classList.remove("selected");
    logoutElement.classList.remove("selected");
    dashboardElement.classList.remove("selected");
    resetPasswordElement.classList.remove("selected");
    addEmployeeElement.classList.remove("selected");
  });
});