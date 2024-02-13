// document.addEventListener('DOMContentLoaded', function () {
//     // Detect changes in the radio buttons to show/hide relevant form sections
//     const individualRadio = document.getElementById('individualRadio');
//     const businessEntityRadio = document.getElementById('businessEntityRadio');
//     const individualForm = document.getElementById('individualForm');
//     const businessEntityForm = document.getElementById('businessEntityForm');
//     const loanIDField = document.getElementById('loanIDField');
//     const loanIDFieldBusiness = document.getElementById('loanIDFieldBusiness');
//     const relationshipField = document.getElementById('relationshipField');
//     const relationshipFieldBusiness = document.getElementById('relationshipFieldBusiness');
//     const additionalInfoIndividual = document.getElementById('additionalInfoIndividual');
//     const additionalInfoBusiness = document.getElementById('additionalInfoBusiness');

//     individualRadio.addEventListener('change', function () {
//         individualForm.style.display = 'block';
//         businessEntityForm.style.display = 'none';
//         loanIDField.style.display = 'block';
//         loanIDFieldBusiness.style.display = 'none';
//         relationshipField.style.display = 'block';
//         relationshipFieldBusiness.style.display = 'none';
//         additionalInfoIndividual.style.display = 'block';
//         additionalInfoBusiness.style.display = 'none';
//     });

//     businessEntityRadio.addEventListener('change', function () {
//         businessEntityForm.style.display = 'block';
//         individualForm.style.display = 'none';
//         loanIDFieldBusiness.style.display = 'block';
//         loanIDField.style.display = 'none';
//         relationshipFieldBusiness.style.display = 'block';
//         relationshipField.style.display = 'none';
//         additionalInfoBusiness.style.display = 'block';
//         additionalInfoIndividual.style.display = 'none';
//     });

//     // Function to update the owned percentage slider value
//     window.updateOwnedPercentage = function (value) {
//         document.getElementById('ownedPercentageValue').textContent = value;
//     };

//     // Function to close the form popup
//     window.closeForm = function () {
//         document.getElementById('borrowerPopupOverlay').style.display = 'none';
//     };

//     // Form submission handling
//     const applyingForm = document.getElementById('applyingForm');
//     const individualSubmitButton = document.getElementById('individualSubmitButton');
//     const businessEntitySubmitButton = document.getElementById('businessEntitySubmitButton');

//     applyingForm.addEventListener('submit', function (event) {
//         event.preventDefault();
//         const formData = new FormData(applyingForm);

//         // Determine whether to submit individual or business entity form
//         const isIndividual = individualRadio.checked;
//         const submitUrl = isIndividual ? '/submit_individual_borrower' : '/submit_business_entity_borrower';

//         // Send the form data to the backend
//         fetch(submitUrl, {
//             method: 'POST',
//             body: formData,
//         })
//         .then(response => response.json())
//         .then(data => {
//             // Handle the response from the backend, e.g., show success message
//             console.log(data);
//             // You can customize this part based on your application's needs
//         })
//         .catch(error => {
//             console.error('Error submitting form:', error);
//             // Handle errors, e.g., show error message to the user
//         });
//     });
// });



document.addEventListener('DOMContentLoaded', function () {
    // Initial setup based on the applyingAs radio button
    const applyingAsRadio = document.getElementById('individualRadio');
    const individualForm = document.getElementById('individualForm');
    const businessEntityForm = document.getElementById('businessEntityForm');
    const additionalInfoIndividual = document.getElementById('additionalInfoIndividual');
    const additionalInfoBusiness = document.getElementById('additionalInfoBusiness');
  
    // Event listener for the applyingAs radio button change
    applyingAsRadio.addEventListener('change', function () {
      if (applyingAsRadio.checked) {
        if (applyingAsRadio.value === 'individual') {
          showForm(individualForm);
          hideForm(businessEntityForm);
          showForm(additionalInfoIndividual);
          hideForm(additionalInfoBusiness);
        } else {
          hideForm(individualForm);
          showForm(businessEntityForm);
          hideForm(additionalInfoIndividual);
          hideForm(additionalInfoBusiness);
        }
      }
    });
  
    // Fetch data from the backend and populate the form
    fetchDataAndPopulateForm();
  });
  
  // Function to fetch data from the backend and populate the form
  function fetchDataAndPopulateForm() {
    // Replace 'your_api_endpoints' with the actual endpoints for fetching data
    fetch('/fetchIndividualApplicant') // Example for individual applicant data
      .then(response => response.json())
      .then(data => {
        if (data.length > 0) {
          populateIndividualForm(data[0]); // Assuming you get one record for individual
          showForm(additionalInfoIndividual);
          populateAdditionalInfoIndividual(data[0]);
        }
      })
      .catch(error => console.error('Error fetching individual applicant data:', error));
  
    fetch('/fetchBusinessApplicant') // Example for business entity data
      .then(response => response.json())
      .then(data => {
        if (data.length > 0) {
          populateBusinessEntityForm(data[0]); // Assuming you get one record for business entity
          showForm(additionalInfoBusiness);
          populateAdditionalInfoBusiness(data[0]);
        }
      })
      .catch(error => console.error('Error fetching business entity data:', error));
  }
  
  function populateIndividualForm(data) {
    // Populate individual form fields based on the data
    document.getElementById('individualRadio').checked = true; // Select the individual radio button

    // Populate common fields
    document.getElementById('applicantIs').value = data.typeOfApplicant;
    document.getElementById('relationshipWithPrimary').value = data.relationWithPrimaryApplicant;
    document.getElementById('loanID').value = data.loanID;
    document.getElementById('firstName').value = data.firstName;
    document.getElementById('middleName').value = data.middleName;
    document.getElementById('lastName').value = data.lastName;
    document.getElementById('email').value = data.email;
    document.getElementById('telephone').value = data.telephone;
    document.getElementById('fax').value = data.fax;
    document.getElementById('streetAddress').value = data.streetAddress;
    document.getElementById('city').value = data.city;
    document.getElementById('state').value = data.state;
    document.getElementById('zipCode').value = data.zip;
    document.getElementById('county').value = data.county;
    document.getElementById('citizenship').value = data.usCitizenOrPermanentAlien;
    document.getElementById('dateOfBirth').value = data.dateOfBirth;
    document.getElementById('socialSecurity').value = data.socialSecurity;
    document.querySelector('input[name="maritalStatus"][value="' + data.maritalStatus + '"]').checked = true;
    document.getElementById('yearBeginningFarming').value = data.yearBeginningFarming;
    document.getElementById('yearAtCurrentAddress').value = data.yearAtCurrentAddress;



    // Show/hide fields based on the applicant type
    if (data.typeOfApplicant === 'primaryApplicant') {
        document.getElementById('relationshipField').style.display = 'none';
        document.getElementById('loanIDField').style.display = 'none';
    } else {
        document.getElementById('relationshipField').style.display = 'block';
        document.getElementById('loanIDField').style.display = 'block';
    }

    // Show additional information section
    document.getElementById('additionalInfoIndividual').style.display = 'block';
}

  
function populateBusinessEntityForm(data) {
  // Populate business entity form fields based on the data
  document.getElementById('businessEntityRadio').checked = true; // Select the business entity radio button

  // Populate common fields
  document.getElementById('applicantIs').value = data.typeOfApplicant;
  document.getElementById('relationshipWithPrimary').value = data.relationWithPrimaryApplicant;
  document.getElementById('loanID').value = data.loanID;
  document.getElementById('businessName').value = data.businessName;
  document.getElementById('email').value = data.email;
  document.getElementById('taxId').value = data.taxId;
  document.getElementById('businessTelephone').value = data.telephone;
  document.getElementById('fax').value = data.fax;
  document.getElementById('streetAddress').value = data.streetAddress;
  document.getElementById('city').value = data.city;
  document.getElementById('state').value = data.state;
  document.getElementById('zipCode').value = data.zip;
  document.getElementById('county').value = data.county;
  document.getElementById('contactNameDetails').value = data.contactNameDetails;
  document.getElementById('businessDescription').value = data.businessDescription;
  document.getElementById('businessType').value = data.businessType;
  document.getElementById('principalOfficer').value = data.principalOfficer;
  document.getElementById('homeAddress').value = data.homeAddress;
  document.getElementById('ownedPercentageSlider').value = data.percentOwned;
  document.getElementById('ownershipTitle').value = data.ownershipTitle;
  document.getElementById('ownedPercentageValue').innerText = data.percentOwned;

  // Show/hide fields based on the applicant type
  if (data.typeOfApplicant === 'primaryApplicant') {
      document.getElementById('relationshipFieldBusiness').style.display = 'none';
      document.getElementById('loanIDFieldBusiness').style.display = 'none';
  } else {
      document.getElementById('relationshipFieldBusiness').style.display = 'block';
      document.getElementById('loanIDFieldBusiness').style.display = 'block';
  }

  // Show additional information section
  document.getElementById('additionalInfoBusiness').style.display = 'block';
}

  // Function to populate additional information for business entity
  function populateAdditionalInfoIndividual(data) {
    // Populate additional information fields
    document.getElementById('additionalComments').value = data.additionalComments;
    document.getElementById('grossFarmIncome').value = data.grossFarmIncome;
    document.getElementById('netFarmIncome').value = data.netFarmIncome;
    document.getElementById('netNonFarmIncome').value = data.netNonFarmIncome;
    document.getElementById('source1').value = data.source1;
    document.getElementById('income1').value = data.income1;
    document.getElementById('source2').value = data.source2;
    document.getElementById('income2').value = data.income2;
    document.getElementById('source3').value = data.source3;
    document.getElementById('income3').value = data.income3;
    document.getElementById('source4').value = data.source4;
    document.getElementById('income4').value = data.income4;

    // ... Add similar lines for other additional information fields

    document.getElementById('totalAssets').value = data.totalAssets;
    document.getElementById('totalLiabilities').value = data.totalLiabilities;
  }

  // Function to populate additional information for business entity
  function populateAdditionalInfoBusiness(data) {
    // Populate additional information fields
    document.getElementById('additionalComments').value = data.additionalComments;
    document.getElementById('grossFarmIncome').value = data.grossFarmIncome;
    document.getElementById('netFarmIncome').value = data.netFarmIncome;
    document.getElementById('netNonFarmIncome').value = data.netNonFarmIncome;
    document.getElementById('source1').value = data.source1;
    document.getElementById('income1').value = data.income1;
    document.getElementById('source2').value = data.source2;
    document.getElementById('income2').value = data.income2;
    document.getElementById('source3').value = data.source3;
    document.getElementById('income3').value = data.income3;
    document.getElementById('source4').value = data.source4;
    document.getElementById('income4').value = data.income4;

    // ... Add similar lines for other additional information fields

    document.getElementById('totalAssets').value = data.totalAssets;
    document.getElementById('totalLiabilities').value = data.totalLiabilities;
  }
  
  // Function to show a form
  function showForm(form) {
    form.style.display = 'block';
  }
  
  // Function to hide a form
  function hideForm(form) {
    form.style.display = 'none';
  }
  