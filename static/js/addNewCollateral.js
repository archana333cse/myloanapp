document.addEventListener('DOMContentLoaded', function () {

    

    var collateralForm = document.getElementById('collateralForm');

    // Function to validate the form
    // Function to validate the form
    function validateForm() {
        // Validate required fields
        var requiredFields = document.querySelectorAll('[required]');
        var isValid = true;

        requiredFields.forEach(function (field) {
            if (!field.value.trim()) {
                alert('Please fill in all required fields.');
                isValid = false;
            }
        });

        // Validate descriptions for specific "yes" options
        var radioOptionsWithDescription = [
            { option: 'waterRights', description: 'waterRightsDescription' },
            { option: 'environmentalHazard', description: 'environmentalHazardDescription' }
        ];

        radioOptionsWithDescription.forEach(function (option) {
            var radio = document.querySelector('input[name="' + option.option + '"]:checked');
            var descriptionField = document.querySelector('textarea[name="' + option.description + '"]');

            if (radio && radio.value === 'yes' && (!descriptionField || !descriptionField.value.trim())) {
                // "Yes" option is selected, but description is empty
                alert('Please fill the description for the "' + option.option + '" option.');
                isValid = false;
            }
        });

        return isValid;
    }

    // Function to build the details string
    function buildDetailsString() {
        var formElements = collateralForm.elements;
        var detailsObject = {};

        for (var i = 0; i < formElements.length; i++) {
            var element = formElements[i];
            if (element.type !== 'button' && element.name) {
                detailsObject[element.name] = element.value;
            }
        }

        return JSON.stringify(detailsObject);
    }

    // Function to calculate total value
    function updateTotalValue() {
        let totalValue = 0;
        const table = document.getElementById('appraisedValueTable');
        const inputs = table.querySelectorAll('input[name$="Value"]');

        inputs.forEach(input => {
            if (!isNaN(parseFloat(input.value))) {
                const value = parseFloat(input.value);
                totalValue += value;
            }
        });

        const totalValueElement = document.getElementById('totalValue');
        totalValueElement.textContent = totalValue.toFixed(2);
    }

    const updateTotalAcres = () => {
        let totalIrrigatedAcres = 0;
        let totalNonIrrigatedAcres = 0;
    
        const rows = document.querySelectorAll('#acresTable tbody tr:not(#totalRow)');
    
        rows.forEach(row => {
            const irrigatedInput = row.querySelector('input[name$="IrrigatedAcres"]');
            const nonIrrigatedInput = row.querySelector('input[name$="NonIrrigatedAcres"]');
    
            if (irrigatedInput && !isNaN(parseFloat(irrigatedInput.value))) {
                totalIrrigatedAcres += parseFloat(irrigatedInput.value);
            }
    
            if (nonIrrigatedInput && !isNaN(parseFloat(nonIrrigatedInput.value))) {
                totalNonIrrigatedAcres += parseFloat(nonIrrigatedInput.value);
            }
        });
    
        document.getElementById('totalIrrigatedAcres').textContent = totalIrrigatedAcres.toFixed(2);
        document.getElementById('totalNonIrrigatedAcres').textContent = totalNonIrrigatedAcres.toFixed(2);
    };
    
    

    // Submit form
    collateralForm.addEventListener('submit', function (event) {
        event.preventDefault();

        var isValid = validateForm();

        if (isValid) {
            var details = buildDetailsString();

            // Send form data to backend using fetch
            fetch('/submit_collateral', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: details // Sending form data as JSON
            })
            .then(response => {
                if (response.ok) {
                    return response.json(); // If expecting JSON response from backend
                } else {
                    throw new Error('Failed to submit form');
                }
            })
            .then(data => {
                // Handle success response from backend
                console.log('Form submitted successfully:', data);
                alert('Form submitted successfully!');
                collateralForm.reset();
            })
            .catch(error => {
                // Handle error
                console.error('Form submission error:', error);
                alert('Form submission failed. Please try again.');
            });
        }
    });

    // Listen for input changes to update total value
    const inputElements = document.querySelectorAll('#appraisedValueTable input[type="number"]');
    inputElements.forEach(inputElement => {
        inputElement.addEventListener('input', updateTotalValue);
    });

    // Listen for input changes to update total acres for irrigated and non-irrigated
    const acreInputs = document.querySelectorAll('input[name$="Acres"]');
    acreInputs.forEach(input => {
        input.addEventListener('input', updateTotalAcres);
    });

    // Initial value calculation
    updateTotalValue();
});

//========close form====================
function closeForm() {
  
   window.location.href = '/application.html#tab3';
   //showTab('tab3');
  }
  
