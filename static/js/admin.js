
document.addEventListener('DOMContentLoaded', () => {
	const signInForm = document.getElementById('signInForm');
	const errorMessage = document.getElementById('signin-error-message'); // Add a div for error messages in your HTML
	// const resetPasswordForm = document.getElementById('resetPasswordModal');
	errorMessage.style.display = 'block';
  
	signInForm.addEventListener('submit', async (event) => {
	  event.preventDefault(); // Prevent the default form submission
  
	  // Get form data as a FormData object
	  const formData = new FormData(signInForm);
  
	  // Convert FormData to JSON
	  const formDataObject = {};
	  formData.forEach((value, key) => {
		formDataObject[key] = value;
	  });
  
	  try {
		// Send the data to the backend using fetch or another AJAX method
		const response = await fetch('/admin_login', {
		  method: 'POST',
		  headers: {
			'Content-Type': 'application/json', // Set the content type to JSON
		  },
		  body: JSON.stringify(formDataObject), // Convert data to JSON and send
		});
		console.log("Response status:", response.status);
		if (response.ok) {
		  // Redirect to home.html on successful login
		  window.location.href = '/adminDashboard.html';
  
		  // Show the reset password modal
		//   resetPasswordForm.style.display = "block";
		  console.log(resetPasswordForm, 'responded')
		} else {
		  const errorResponse = await response.text(); // Get the error message as text
		  errorMessage.textContent = errorResponse; // Display the error message on the frontend
		}
	  } catch (error) {
		// Handle network errors or other exceptions
		console.error('Error:', error);
	  }
	});
  });
  