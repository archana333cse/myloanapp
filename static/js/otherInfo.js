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
  
    const form = document.getElementById('otherInfoForm');
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
            form.reset();
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
    
    window.location.href = '/application.html#tab1';
  }
  