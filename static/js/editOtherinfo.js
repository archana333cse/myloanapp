async function fetchAndDisplayOtherinfoData() {
    try {
        const response = await fetch('/fetchOtherinfo', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (response.ok) {
            const otherInfoArray = await response.json();

            if (otherInfoArray.length > 0) {
                const otherInfoData = otherInfoArray[0];
                console.log("Received other info data", otherInfoData);

                // Update radio buttons and input fields based on the fetched data
                const existingClientRadioYes = document.getElementById('yesRadio');
                const existingClientRadioNo = document.getElementById('noRadio');
                const existingClientYearInput = document.getElementById('yearInput');

                if (otherInfoData.existingClient === 'no') {
                    existingClientRadioNo.checked = true;
                    existingClientRadioYes.checked = false;
                    existingClientYearInput.value = '';  // Clear the year input if 'No' is selected
                } else {
                    existingClientRadioYes.checked = true;
                    existingClientRadioNo.checked = false;
                    existingClientYearInput.value = otherInfoData.existingClient;  // Set the year value
                }

                // Iterate through other keys in otherInfoData to update other form fields
                Object.keys(otherInfoData).forEach((key) => {
                    if (key !== 'existingClient') {
                        const elements = document.getElementsByName(key);

                        if (elements.length > 0) {
                            elements.forEach((element) => {
                                // Check if the value is not null or undefined before updating
                                if (otherInfoData[key] !== null && otherInfoData[key] !== undefined) {
                                    // Special handling for checkboxes
                                    if (element.type === 'checkbox') {
                                        element.checked = otherInfoData[key].toLowerCase() === 'yes';
                                    } else if (element.type === 'radio') {
                                        element.checked = element.value === otherInfoData[key];
                                    } else {
                                        element.value = otherInfoData[key];
                                    }
                                }
                            });
                        }
                    }
                });
            } else {
                console.error('Error: Empty other info data array');
            }
        } else {
            console.error('Error fetching other info data:', response.status, response.statusText);
            console.log(response);
        }
    } catch (error) {
        console.error('An error occurred while fetching other info data:', error.message);
    }
}

// Call the function to fetch and display other info data when the page loads
window.onload = fetchAndDisplayOtherinfoData;

//======================================================================================


document.addEventListener('DOMContentLoaded', () => {
    const yesRadio = document.getElementById('yesRadio');
    const yearInput = document.getElementById('yearInput');
  
    yesRadio.addEventListener('change', function() {
      if (this.checked) {
        const year = prompt('Enter Year Begin:');
        if (year !== null && year !== "") {
          yesRadio.value = year;
          yearInput.value = year;
        } else {
          yesRadio.checked = false;
        }
      }
    });
  
    const form = document.getElementById('editOtherInfoForm');
    const detailsTextarea = document.getElementById('details');
    const radioButtonsYes = document.querySelectorAll('input[type=radio][value="yes"]');
    
    function isAnyYesSelected() {
      for (let i = 0; i < radioButtonsYes.length; i++) {
        if (radioButtonsYes[i].checked) {
          return true;
        }
      }
      return false;
    }
  
    form.addEventListener('submit', function(event) {
      event.preventDefault();
    
      if (isAnyYesSelected() && detailsTextarea.value.trim() === '') {
        alert('Please fill in the details field for "Yes" responses.');
      } else {
        const formData = new FormData(form);
        const serializedForm = {};
        formData.forEach((value, key) => {
          serializedForm[key] = value;
        });
    
        fetch('/update_otherInfo', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(serializedForm)
        })
        .then(response => {
          if (response.ok) {
            alert('Form submitted and stored successfully!');
            window.location.href = 'application.html#tab4';

            detailsTextarea.required = false; // Remove the required attribute
          } else {
            alert('Error submitting the form. Please try again.');
          }
        })
        .catch(error => {
          console.error('Error:', error);
        });
      }
    });
  });

  //==================================
function closeForm() {
    //showTab('tab1');
    
    window.location.href = '/application.html#tab4';
  }