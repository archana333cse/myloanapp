

       
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
// Profile link
const profilePassLink = document.querySelector('.navbar-nav .dropdown-item:first-child');
const profileSection = document.getElementById('profileSection');

profilePassLink.addEventListener('click', (event) => {
    event.preventDefault();
    hideElements(['hideElement1', 'hideElement2','showAnalytics','showUtility','resetPasswordForm']);
    profileSection.style.display = 'block';


    // Call the function to update profile details 
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





// Reset Password link
const resetPassLink = document.querySelector('.sidebar-link[data-bs-target="#resetPass"]');
const resetPassForm = document.getElementById('resetPasswordForm');

resetPassLink.addEventListener('click', (event) => {
    event.preventDefault();
    hideElements(['hideElement1', 'hideElement2','showAnalytics','showUtility','profileSection']);
    resetPassForm.style.display = 'block';
});

// Analytics link
const analyticsLink = document.querySelector('.sidebar-link[data-bs-target="#analytics"]');
const showAnalytics = document.getElementById('showAnalytics');

analyticsLink.addEventListener('click', (event) => {
    event.preventDefault();
    hideElements(['hideElement1', 'hideElement2','resetPasswordForm','showUtility','profileSection']);
    showAnalytics.style.display = 'block';
});

// utility link
const utilityLink = document.querySelector('.sidebar-link[data-bs-target="#utilities"]');
const showUtility = document.getElementById('showUtility');

utilityLink.addEventListener('click', (event) => {
    event.preventDefault();
    hideElements(['hideElement1', 'hideElement2','resetPasswordForm','showAnalytics','profileSection']);
    showUtility.style.display = 'block';
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



//toggle for selected dashboard elements

document.addEventListener("DOMContentLoaded", function () {
    // Get references to the dashboard elements
    const dashboardElement = document.getElementById("dashboardElement");
    const analyticsElement=document.getElementById("analyticsElement");
    const resetPasswordElement = document.getElementById("resetPasswordElement");
    const utilityElement=document.getElementById("utilityElement");
    const logoutElement = document.getElementById("logoutElement");
    const profileElement=document.getElementById('profileElement');


    // Add the "selected" class to the Dashboard element by default
    dashboardElement.classList.add("selected");


    // Add click event listeners to toggle the "selected" class 
    dashboardElement.addEventListener("click", function () {
        dashboardElement.classList.toggle("selected");
        analyticsElement.classList.remove("selected");
        resetPasswordElement.classList.remove("selected");
        utilityElement.classList.remove("selected");
        logoutElement.classList.remove("selected");
        profileElement.classList.remove("selected");

    });

    resetPasswordElement.addEventListener("click", function () {
        resetPasswordElement.classList.toggle("selected");
        analyticsElement.classList.remove("selected");
        dashboardElement.classList.remove("selected");
        utilityElement.classList.remove("selected");
        logoutElement.classList.remove("selected");
        profileElement.classList.remove("selected");
    });


    logoutElement.addEventListener("click", function () {
        logoutElement.classList.toggle("selected");
        analyticsElement.classList.remove("selected");
        dashboardElement.classList.remove("selected");
        resetPasswordElement.classList.remove("selected");
        utilityElement.classList.remove("selected");
        profileElement.classList.remove("selected");
    });
    analyticsElement.addEventListener("click", function () {
        analyticsElement.classList.toggle("selected");
        logoutElement.classList.remove("selected");
        dashboardElement.classList.remove("selected");
        resetPasswordElement.classList.remove("selected");
        utilityElement.classList.remove("selected");
        profileElement.classList.remove("selected");
    });
    utilityElement.addEventListener("click", function () {
        utilityElement.classList.toggle("selected");
        logoutElement.classList.remove("selected");
        dashboardElement.classList.remove("selected");
        resetPasswordElement.classList.remove("selected");
        analyticsElement.classList.remove("selected");
        profileElement.classList.remove("selected");
    });
    profileElement.addEventListener("click", function () {
        profileElement.classList.toggle("selected");
        logoutElement.classList.remove("selected");
        dashboardElement.classList.remove("selected");
        resetPasswordElement.classList.remove("selected");
        analyticsElement.classList.remove("selected");
        utilityElement.classList.remove("selected");
    });


});





