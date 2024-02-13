const signUpButton = document.getElementById('signUp');
const signInButton = document.getElementById('signIn');
const container = document.getElementById('container');

signUpButton.addEventListener('click', () => {
	container.classList.add("right-panel-active");
});

signInButton.addEventListener('click', () => {
	container.classList.remove("right-panel-active");
});

// Add an event listener to the "Sign In" button
function navigateToHome() {   
    window.location.href = 'home.html';
}



//---------------------------------------------------------------------------------

document.addEventListener('DOMContentLoaded', () => {
	const signUpForm = document.getElementById('signUpForm');
	const errorMessage = document.getElementById('error-message'); // Add a div for error messages in your HTML
	errorMessage.style.display = 'block';
	// Add a submit event listener to the form
	signUpForm.addEventListener('submit', async (event) => {
	  event.preventDefault(); // Prevent the default form submission
  
	  // Get form data as a FormData object
	  const formData = new FormData(signUpForm);
  
	  // Convert FormData to JSON
	  const formDataObject = {};
	  formData.forEach((value, key) => {
		formDataObject[key] = value;
	  });
  
	  try {
		// Send the data to the backend using fetch or another AJAX method
		const response = await fetch('/signup', {
		  method: 'POST',
		  headers: {
			'Content-Type': 'application/json', // Set the content type to JSON
		  },
		  body: JSON.stringify(formDataObject), // Convert data to JSON and send
		});
  
		if (response.ok) {
		  // Handle success, extract the generated user ID and password
		  const { message, userid } = await response.json();
		  const email = formDataObject.email; // Get the email from the form
  
		  // Generate the password (assuming email is in the form of "username@domain")
		  const password = email.split('@')[0]; // Extract the username part
  
		  // Create the success message
		  const successMessage = `${message}\nUser ID: ${userid}\nPassword: ${password}\n(Note: Password is only for once, remember to change the password after login.)`;
		  alert(successMessage);
		  signUpForm.reset(); // Reset the form
		  errorMessage.textContent = ''; // Clear any previous error message
		} else {
			// Handle errors based on content type
			const contentType = response.headers.get('content-type');
			console.log('Content-Type:', contentType); // Debugging
			if (contentType && contentType.includes('application/json')) {
			  // JSON response
			  const errorResponse = await response.json();
			  console.log('Error Response:', errorResponse.error); // Debugging
			  errorMessage.innerText = errorResponse.error; // Display the error message on the frontend
			} else {
			  // HTML response (display it as-is)
			  errorMessage.innerHTML = await response.text(); // Display HTML error message
			}
		}
	  } catch (error) {
		// Handle network errors or other exceptions
		console.error('Error:', error);
		
	  }
	});
  });
  
//   -----------------------------------------------------------------------------------------------------------------

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
		const response = await fetch('/signin', {
		  method: 'POST',
		  headers: {
			'Content-Type': 'application/json', // Set the content type to JSON
		  },
		  body: JSON.stringify(formDataObject), // Convert data to JSON and send
		});
		console.log("Response status:", response.status);
		if (response.ok) {
		  // Redirect to home.html on successful login
		  window.location.href = '/home.html';
  
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
  
  
  