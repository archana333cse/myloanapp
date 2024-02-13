// Function to submit the form when the submit icon is clicked
function submitForm() {
    document.getElementById('companyRegistrationForm').submit();
}


document.addEventListener('DOMContentLoaded', function () {
    const slides = document.querySelectorAll('.slide');
    let currentSlide = 0;

    function scrollToSlide(slideIndex) {
        slides[slideIndex].scrollIntoView({ behavior: 'smooth' });
    }

    scrollToSlide(currentSlide);

    document.addEventListener('keydown', function (e) {
        if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
            currentSlide = e.key === 'ArrowDown' ? currentSlide + 1 : currentSlide - 1;
            currentSlide = Math.max(0, Math.min(slides.length - 1, currentSlide));
            scrollToSlide(currentSlide);
        }
    });
});


// -----------------------------------------------------
// LogOut
function admin_logout() {
    fetch('/admin_logout', {
        method: 'GET'
    }).then(() => {
        // Always redirect to the landing page
        window.location.href = '/landingpage.html';
    });
}
// ------------------------------------------------------

document.addEventListener('DOMContentLoaded', () => {
    const signUpForm = document.getElementById('companyRegistrationForm');
    const errorMessage = document.getElementById('error-message');

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
            // Send the data to the backend using fetch
            const response = await fetch('/register_company', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json', // Set the content type to JSON
                },
                body: JSON.stringify(formDataObject), // Convert data to JSON and send
            });

            if (response.ok) {
                // Handle success, extract the response data
                const responseData = await response.json();


                if ('error' in responseData) {
                    errorMessage.innerText = responseData.error;
                } else {
                    // If there's no 'error', the response is successful
                    const message = responseData.message;
                    const userid = responseData.userid;

                    // Show a success message with the user ID and password
                    const successMessage = `${message}\nUser ID: ${userid}\nPassword: ${formDataObject.companyEmail.split('@')[0]}`;
                    alert(successMessage);

                    // Handle the success response as needed
                }
				window.location.href = '/cregistration.html';
            } else {
                // Handle errors based on content type
                const contentType = response.headers.get('content-type');

                if (contentType && contentType.includes('application/json')) {
                    // JSON response with an error message
                    const errorResponse = await response.json();
                    errorMessage.innerText = errorResponse.error;
                } else {
                    // HTML response (display it as-is)
                    errorMessage.innerHTML = await response.text();
                }
            }
        } catch (error) {
            // Handle network errors or other exceptions
            errorMessage.innerText = 'An error occurred while processing your request.';
            console.error('Error:', error);
        }
    });
});

// ----------------------------------------------------------------------------------------------------
// existing company

async function fetchExistingCompanies() {
	try {
	  const response = await fetch('/get_existing_companies');
	  if (!response.ok) {
		throw new Error('Network response was not ok');
	  }
	  const data = await response.json();
  
	  // Get a reference to the table body element
	  const tableBody = document.getElementById('existing-comp-tablebody');
  
	  // Clear the existing table rows
	  tableBody.innerHTML = '';
  
	  // Loop through the fetched data and create table rows
	  data.data.forEach(row => {
		const newRow = document.createElement('tr');
		newRow.innerHTML = `
		  <td>${row.ADMIN_ID}</td>
		  <td>${row.COMPANY_NAME}</td>
		  <td>${row.EMAIL}</td>
		  <td>${row.CONTACT}</td>
		  <td>
			<button class="remove-button" disabled>Remove</button>
		  </td>
		`;
		tableBody.appendChild(newRow);
	  });
	} catch (error) {
	  console.error('Error fetching existing borrowers data:', error);
	}
  }
  // Call fetchExistingLoans() when the page loads to populate the table
  window.addEventListener('load', fetchExistingCompanies);
