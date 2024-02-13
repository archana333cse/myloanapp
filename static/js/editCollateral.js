

async function fetchAndDisplayCollateralData() {
    try {
        const response = await fetch('/fetchCollateral', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (response.ok) {
            const collateralDataArray = await response.json();

            if (collateralDataArray.length > 0) {
                const collateralData = collateralDataArray[0];
                console.log("Received collateral data", collateralData);

                // Iterate through keys in collateralData
                Object.keys(collateralData).forEach((key) => {
                    const elements = document.getElementsByName(key);

                    if (elements.length > 0) {
                        elements.forEach((element) => {
                            // Check if the value is not null or undefined before updating
                            if (collateralData[key] !== null && collateralData[key] !== undefined) {
                                // Special handling for checkboxes
                                if (element.type === 'checkbox') {
                                  // Use the boolean value directly for comparison
                                  element.checked = collateralData[key];
                              } else if (element.type === 'radio') {
                                  element.checked = element.value === collateralData[key];
                              } else {
                                  element.value = collateralData[key];
                              }
                            }
                        });
                    }
                });
            } else {
                console.error('Error: Empty collateral data array');
            }
        } else {
            console.error('Error fetching collateral data:', response.status, response.statusText);
            console.log(response);
        }
    } catch (error) {
        console.error('An error occurred while fetching collateral data:', error.message);
    }
}

// Call the function to fetch and display collateral data when the page loads
window.onload = fetchAndDisplayCollateralData;


//------------------------------------------------------------------------------------------------------------------



document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('updateCollateralForm');
    const submitButton = document.getElementById('submitButton'); // Assuming you have a button with ID 'submitButton'

    function calculateAndUpdateTotalValue() {
      // Get the input fields for Land, Residence, All Other Improvements, and Permanent Plantings
      const landValue = parseFloat(document.querySelector('input[name="landValue"]').value) || 0;
      const residenceValue = parseFloat(document.querySelector('input[name="residenceValue"]').value) || 0;
      const improvementsValue = parseFloat(document.querySelector('input[name="improvementsValue"]').value) || 0;
      const plantingsValue = parseFloat(document.querySelector('input[name="plantingsValue"]').value) || 0;
  
      // Calculate the total value
      const totalValue = landValue + residenceValue + improvementsValue + plantingsValue;
  
      // Update the total value in the readonly input field
      const totalValueField = document.getElementById('totalValue');
      if (totalValueField) {
        totalValueField.value = totalValue.toFixed(2);
      }
    }
  
    // Add event listeners to input fields for real-time calculation
    const inputFields = document.querySelectorAll('input[name^="value"]');
    inputFields.forEach((inputField) => {
      inputField.addEventListener('input', calculateAndUpdateTotalValue);
    });
  
    form.addEventListener('submit', function (event) {
      event.preventDefault();
  
      // Collect form data
      const formData = {
        SPL: document.querySelector('input[name="propertyState"]').value,
        CPL: document.querySelector('input[name="propertyCounty"]').value,
        SEC: document.querySelector('input[name="section"]').value,
        TOWN: document.querySelector('input[name="township"]').value,
        RAN: document.querySelector('input[name="range"]').value,
        ALD: document.querySelector('input[name="abriviatedlegaldescription"]').value,
        EVL: document.querySelector('input[name="landValue"]').value,
        EVR: document.querySelector('input[name="residenceValue"]').value,
        EVAOI: document.querySelector('input[name="improvementsValue"]').value,
        EVPP: document.querySelector('input[name="plantingsValue"]').value,
        EVTV: document.querySelector('input[name="totalValue"]').value,
        LRAP: document.querySelector('input[name="propertyLeases"]:checked').value,
        LRAR: document.querySelector('input[name="remainingTerm"]:checked').value,
        APIPO: document.querySelector('input[name="purchaseAgreements"]:checked').value,
        LEME: document.querySelector('input[name="manureEasements"]').checked,
        LEWL: document.querySelector('input[name="windLeases"]').checked,
        LECT: document.querySelector('input[name="cellTower"]').checked,
        LEOM: document.querySelector('input[name="oilMineralGasLeases"]').checked,
        LEO: document.querySelector('input[name="otherLeases"]').checked,
        LEOD: document.querySelector('input[name="otherLeasesDescription"]').value,
        OC: document.querySelector('input[name="ownership"]').value,
        ECRA: document.querySelector('input[name="cashRent"]').value,
        ERET: document.querySelector('input[name="realEstateTaxes"]').value,
        PIA: document.querySelector('input[name="pastureIrrigatedAcres"]').value,
        PIV: document.querySelector('input[name="pastureIrrigatedValuePerAcre"]').value,
        PNA: document.querySelector('input[name="pastureNonIrrigatedAcres"]').value,
        PNVA: document.querySelector('input[name="pastureNonirrigatedValuePerAcre"]').value,
        CIA: document.querySelector('input[name="crpIrrigatedAcres"]').value,
        CIVA: document.querySelector('input[name="crpIrrigatedValuePerAcre"]').value,
        CNIA: document.querySelector('input[name="crpNonIrrigatedAcres"]').value,
        CNIVA: document.querySelector('input[name="crpNonirrigatedValuePerAcre"]').value,
        WIA: document.querySelector('input[name="woodedIrrigatedAcres"]').value,
        WIVA: document.querySelector('input[name="woodedIrrigatedValuePerAcre"]').value,
        WNIA: document.querySelector('input[name="woodedNonIrrigatedAcres"]').value,
        WNIVA: document.querySelector('input[name="woodedNonirrigatedValuePerAcre"]').value,
        PLIA: document.querySelector('input[name="plantingsIrrigatedAcres"]').value,
        PPIV: document.querySelector('input[name="plantingsIrrigatedValuePerAcre"]').value,
        PLNA: document.querySelector('input[name="plantingsNonIrrigatedAcres"]').value,
        PPNVA: document.querySelector('input[name="plantingsNonirrigatedValuePerAcre"]').value,
        TIA: document.querySelector('input[name="timberlandIrrigatedAcres"]').value,
        TIVA: document.querySelector('input[name="timberlandIrrigatedValuePerAcre"]').value,
        TNIA: document.querySelector('input[name="timberlandNonIrrigatedAcres"]').value,
        TNIVA: document.querySelector('input[name="timberlandNonirrigatedValuePerAcre"]').value,
        OIA: document.querySelector('input[name="othersIrrigatedAcres"]').value,
        OIVA: document.querySelector('input[name="othersIrrigatedValuePerAcre"]').value,
        ONIA: document.querySelector('input[name="othersNonIrrigatedAcres"]').value,
        ONIVA: document.querySelector('input[name="othersNonirrigatedValuePerAcre"]').value,
        TOIA: document.querySelector('input[id="totalIrrigatedAcres"]').value,
        TONIA: document.querySelector('input[id="totalNonIrrigatedAcres"]').value,
        TA: document.querySelector('input[name="totalacres"]').value,
        IOC: document.querySelector('input[name="improvements"]:checked').value,
        IRSPRI: document.querySelector('input[name="permanentplantings"]:checked').value,
        PPOC: document.querySelector('input[name="irepayment"]:checked').value,
        PRSIP: document.querySelector('input[name="pprepayment"]:checked').value,
        IRLM: document.querySelector('input[name="sixmonthwork"]:checked').value,
        ROC: document.querySelector('input[name="residence"]:checked').value,
        IPPD: document.querySelector('textarea[name="description"]').value,
        WIWR: document.querySelector('input[name="waterRights"]:checked').value,
        WD: document.querySelector('textarea[name="waterRightsDescription"]').value,
        EHKS: document.querySelector('input[name="environmentalHazard"]:checked').value,
        ED: document.querySelector('textarea[name="environmentalHazardDescription"]').value,
    };
    
      // Send data to backend using fetch API
      fetch('/updateCollateral', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })
        .then(response => response.json())
        .then(data => {
          console.log(data);
          if (data.success) {
            alert('Data updated successfully!');
          } else {
            alert('Data update failed. Please check the form and try again.');
          }
          console.log(data);
          
        })
        .catch(error => {
          console.error('Error:', error);
        });
    });
  
    // Add click event listener to the submit button
    submitButton.addEventListener('click', function (event) {
      // Trigger the form submission when the button is clicked
      form.dispatchEvent(new Event('submit'));
    });
  });