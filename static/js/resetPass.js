document.getElementById('resetPasswordForm').addEventListener('submit', function (event) {
    event.preventDefault(); // Prevent the default form submission
  
    var form = event.target;
    var formData = new FormData(form);
  
    fetch('/set_password', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Show success alert
            alert('Password set successfully!');
            
            // Redirect to the login page
            window.location.href = '/cadmin.html';
        } else {
            document.getElementById('reset-error-message').innerHTML = data.message;
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
  });
  
