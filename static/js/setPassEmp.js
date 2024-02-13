document.getElementById('resetPasswordForm').addEventListener('submit', function (event) {
    event.preventDefault(); // Prevent the default form submission

    var form = event.target;
    var formData = new FormData(form);

    fetch('/set_password_emp', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.text(); // Handle HTML content
    })
    .then(data => {
        // Check for success message in HTML response
        if (data.includes('Password updated successfully')) {
            // Show success alert
            alert('Password set successfully!');
            
            // Redirect to the login page
            window.location.href = '/cemployee.html';
        } else {
            // Display the HTML content as an error message
            document.getElementById('reset-error-message').innerHTML = data;
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});
