
function closeForm() {
  
    window.location.href = "application.html";
  }
  
  
  
  // Function to submit individual borrower data
  async function submitIndividualBorrower(formData) {
    try {
      const response = await fetch('/submit_individual_borrower', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
  
      const data = await response.json();
      if (response.ok) {
        console.log('Data successfully submitted:', data);
        // Handle success: maybe show a success message or redirect the user
      } else {
        console.error('Error submitting data:', data.error);
        // Handle error: show an error message to the user
      }
    } catch (error) {
      console.error('An error occurred while submitting:', error);
      // Handle other errors: network issues, etc.
    }
  }
  
  // Function to submit business entity borrower data
  async function submitBusinessEntityBorrower(formData) {
    try {
      const response = await fetch('/submit_business_entity_borrower', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
  
      const data = await response.json();
      if (response.ok) {
        console.log('Data successfully submitted:', data);
        // Handle success: maybe show a success message or redirect the user
      } else {
        console.error('Error submitting data:', data.error);
        // Handle error: show an error message to the user
      }
    } catch (error) {
      console.error('An error occurred while submitting:', error);
      // Handle other errors: network issues, etc.
    }
  }
  
  document.addEventListener('DOMContentLoaded', function () {
    var individualRadio = document.getElementById('individualRadio');
    var businessEntityRadio = document.getElementById('businessEntityRadio');
  
    var individualForm = document.getElementById('individualForm');
    var businessEntityForm = document.getElementById('businessEntityForm');
  
    var relationshipField = document.getElementById('relationshipField');
    var loanIDField = document.getElementById('loanIDField');
  
    var relationshipFieldBusiness = document.getElementById('relationshipFieldBusiness');
    var loanIDFieldBusiness = document.getElementById('loanIDFieldBusiness');
  
    var additionalInfoIndividual = document.getElementById('additionalInfoIndividual');
    var additionalInfoBusiness = document.getElementById('additionalInfoBusiness');
  
    // Function to show or hide elements based on radio button selection
    function toggleFields() {
      if (individualRadio.checked) {
        individualForm.style.display = 'block';
        businessEntityForm.style.display = 'none';
  
        if (document.querySelector('input[name="applicantIs"]:checked')) {
          var selectedApplicantType = document.querySelector('input[name="applicantIs"]:checked').value;
          if (selectedApplicantType === 'primaryApplicant') {
            relationshipField.style.display = 'none';
            loanIDField.style.display = 'none';
            additionalInfoIndividual.style.display = 'block';
          } else {
            relationshipField.style.display = 'block';
            loanIDField.style.display = 'block';
            additionalInfoIndividual.style.display = 'none';
          }
        }
      } else if (businessEntityRadio.checked) {
        businessEntityForm.style.display = 'block';
        individualForm.style.display = 'none';
  
        if (document.querySelector('input[name="applicantIs"]:checked')) {
          var selectedApplicantTypeBusiness = document.querySelector('input[name="applicantIs"]:checked').value;
          if (selectedApplicantTypeBusiness === 'primaryApplicant') {
            relationshipFieldBusiness.style.display = 'none';
            loanIDFieldBusiness.style.display = 'none';
            additionalInfoBusiness.style.display = 'block';
          } else {
            relationshipFieldBusiness.style.display = 'block';
            loanIDFieldBusiness.style.display = 'block';
            additionalInfoBusiness.style.display = 'none';
          }
        }
      }
    }
  
  
    
    
    // Initial setup based on the default selected radio button
    toggleFields();
  
    // Add change event listeners to radio buttons
    individualRadio.addEventListener('change', toggleFields);
    businessEntityRadio.addEventListener('change', toggleFields);
  
    // Add change event listener to "applicantIs" radio buttons in the individual form
    var applicantIsRadioIndividual = document.querySelectorAll('#individualForm input[name="applicantIs"]');
    applicantIsRadioIndividual.forEach(function (radio) {
      radio.addEventListener('change', toggleFields);
    });
  
    // Add change event listener to "applicantIs" radio buttons in the business entity form
    var applicantIsRadioBusiness = document.querySelectorAll('#businessEntityForm input[name="applicantIs"]');
    applicantIsRadioBusiness.forEach(function (radio) {
      radio.addEventListener('change', toggleFields);
    });
  
    // Function to update the owned percentage value
    function updateOwnedPercentage(value) {
      const ownedPercentageValue = document.getElementById('ownedPercentageValue');
      ownedPercentageValue.textContent = value;
    }
  
    // Add input event listener to the ownedPercentageSlider
    ownedPercentageSlider.addEventListener('input', function () {
      updateOwnedPercentage(this.value);
    });
  
  
    function validateForm(currentForm) {
      var requiredFields = currentForm.querySelectorAll('[required]');
      console.log('Required Fields:', requiredFields);
    
      for (var i = 0; i < requiredFields.length; i++) {
        if (!requiredFields[i].value.trim()) {
          console.log('Field not filled:', requiredFields[i]);
          alert('Form submission unsuccessful. Please fill in all required fields.');
          return false;
        }
      }
      return true;
    }
    
  
    // Function to handle custom form submission
    async function submitForm(event) {
      // Prevent the default form submission behavior
      event.preventDefault();
  
      var currentForm;
      var endpointFunction;
  
      if (individualRadio.checked) {
        currentForm = individualForm;
        endpointFunction = submitIndividualBorrower;
      } else if (businessEntityRadio.checked) {
        currentForm = businessEntityForm;
        endpointFunction = submitBusinessEntityBorrower;
      }
  
      // Validate the form fields
      if (validateForm(currentForm)) {
        // Log the form data
        var formData = {};
        var formFields = currentForm.querySelectorAll('input, select, textarea');
        formFields.forEach(function (field) {
          formData[field.name] = field.value;
        });
  
        // Submit the form data to the appropriate endpoint function
        try {
          await endpointFunction(formData);
          //console.log('Form Data:', formData);
  
  
          alert('Form submitted successfully!');
          //currentForm.reset()
          currentForm.reset();
          
          
         // window.location.href = "application.html";
        } catch (error) {
          // Handle submission errors
          console.log('Form Data:', formData);
  
          console.error('Error submitting form:', error);
          alert('Form submission unsuccessful. Please try again.');
        }
      }
    }
  
    // Add submit event listener to the individual form
    individualForm.addEventListener('submit', submitForm);
  
    // Add submit event listener to the business entity form
    businessEntityForm.addEventListener('submit', submitForm);
  });
  