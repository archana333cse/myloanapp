document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('ForgotPasswordForm');

    if (form) {
        form.addEventListener('submit', function (event) {
            event.preventDefault();

            // Get the username entered by the user
            const username = document.getElementById('username').value;
            console.log(username);

            // Make a POST request to the server to send OTP
            fetch(`/send_otp?username=${encodeURIComponent(username)}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
            })
                .then(response => response.json())
                .then(data => {
                    // Display success or error message to the user
                    alert(data.message || data.error);

                    // Redirect to a new page if OTP sent successfully
                    if (!data.error) {
                        console.log("Redirecting to /verify_otp");
                        window.location.href = '/verify_otp';
                    }
                })
                .catch(error => console.error('Error:', error));
        });
    } else {
        console.error('Form with ID "ForgotPasswordForm" not found');
    }
});


document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('VerifyOTPForm');

    if (form) {
        form.addEventListener('submit', function (event) {
            event.preventDefault();

            // Get the OTP entered by the user
            const otp = document.getElementById('otp').value;
            console.log(otp);

            // Make a POST request to the server to verify OTP
            fetch(`/verify_otp?otp=${encodeURIComponent(otp)}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
            })
                .then(response => response.json())
                .then(data => {
                    // Display success or error message to the user
                    alert(data.message || data.error);

                    // Redirect to a new page if OTP verified successfully
                    if (!data.error) {
                        console.log("Redirecting to CAdmin_set_new_password");
                        window.location.href = '/CAdmin_set_new_password';
                    }
                })
                .catch(error => console.error('Error:', error));
        });
    } else {
        console.error('Form with ID "VerifyOTPForm" not found');
    }
});


document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('resetPasswordForm');

    if (form) {
        form.addEventListener('submit', function (event) {
            event.preventDefault();

            // Get form data
            const securityQuestion = document.getElementById('securityQuestion').value;
            const answer = document.getElementById('answer').value;
            const newPassword = document.getElementById('newPassword').value;
            const confirmPassword = document.getElementById('confirmPassword').value;

            // Make a POST request to the server to reset the password
            fetch(`/CAdmin_set_new_password?securityQuestion=${securityQuestion}&answer=${answer}&newPassword=${newPassword}&confirmPassword=${confirmPassword}`,{
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
            })
            .then(response => {
                if (!response.ok) {
                    
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })    
            .then(data => {
                // Display success message to the user
                if (data.message) {
                    alert(data.message);
            
                    // Redirect to a new page if password reset successfully
                    if (!data.error) {
                        console.log("Redirecting to compDashboard.html");
                        window.location.href = 'compDashboard.html';  
                    }
                } else if (data.error) {
                    // Display error message received from the server
                    alert(`Error: ${data.error}`);
                } else {
                    // Handle unexpected response from the server
                    alert('An unexpected response was received from the server.');
                }
            })
            .catch(error => console.error('Error:', error));
            alert('An error occurred while resetting the password. Please try again.');
        });
    } else {
        console.error('Form with ID "resetPasswordForm" not found');
    }
});

