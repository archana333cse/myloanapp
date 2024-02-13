document.addEventListener('DOMContentLoaded', () => {
    const signInForm = document.getElementById('signInForm');
    const errorMessage = document.getElementById('signin-error-message');
    errorMessage.style.display = 'block';
  
    signInForm.addEventListener('submit', async (event) => {
        event.preventDefault();
  
        const formData = new FormData(signInForm);
        const formDataObject = {};
        formData.forEach((value, key) => {
            formDataObject[key] = value;
        });
  
        try {
            const response = await fetch('/cadmin_login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formDataObject),
            });
  
            if (response.ok) {
                const responseData = await response.json();
                const redirectURL = responseData.redirect; // Get the redirect URL from the response data
  
                if (redirectURL === '/resetPass.html') { // Check the URL for reset password
                    window.location.href = redirectURL;
                } else {
                    window.location.href = '/compDashboard.html'; // Default redirection
                }
            } else {
                const errorResponse = await response.text();
                errorMessage.textContent = errorResponse;
            }
        } catch (error) {
            console.error('Error:', error);
        }
    });
});
