// Function to fetch and display loan data
async function fetchAndDisplayLoanData() {
    try {
        // Fetch loan data from the backend
        const response = await fetch('/fetchLoan', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        // Check if the request was successful
        if (response.ok) {
            // Parse the response as JSON
            const loanDataArray = await response.json();

            // Check if the array contains any data
            if (loanDataArray.length > 0) {
                // Access the first object inside the array
                const loanData = loanDataArray[0];

                // Log the received data for debugging
                console.log("Received data", loanData);

                // Populate the form with the received data
                document.getElementById('amount_requested').value = loanData.amount_requested !== null ? loanData.amount_requested : '';
                document.getElementById('projected_loan_to_value').value = loanData.projected_loan_to_value !== null ? loanData.projected_loan_to_value : '';
                document.getElementById('requested_close_date').value = loanData.requested_close_date || '';

                // Check the payment frequency radio button
                const paymentFrequencyRadio = document.querySelector(`input[name="payment_frequency"][value="${loanData.payment_frequency}"]`);
                if (paymentFrequencyRadio) {
                    paymentFrequencyRadio.checked = true;
                }

                // Check the loan purpose radio button
                const loanPurposeRadio = document.querySelector(`input[name="loan_purpose"][value="${loanData.loan_purpose}"]`);
                if (loanPurposeRadio) {
                    loanPurposeRadio.checked = true;
                }

                // If the loan purpose is "Other", populate the "Specify other purpose" field
                if (loanData.loan_purpose === 'other') {
                    document.getElementById('loan_purpose_other').value = loanData.loan_purpose_other || '';
                }

                // Populate Use of Funds table dynamically
                for (let i = 1; i <= 4; i++) {
                    const sourceOfFundsAmount = loanData[`source_of_funds_amount_${i}`] !== null ? loanData[`source_of_funds_amount_${i}`] : '';
                    const sourceOfFundsDescription = loanData[`source_of_funds_desc_${i}`] || '';
                    const useOfFundsAmount = loanData[`use_of_funds_amount_${i}`] !== null ? loanData[`use_of_funds_amount_${i}`] : '';
                    const useOfFundsDescription = loanData[`use_of_funds_desc_${i}`] || '';

                    document.getElementById(`source_of_funds_amount_${i}`).value = sourceOfFundsAmount;
                    document.getElementById(`source_of_funds_desc_${i}`).value = sourceOfFundsDescription;
                    document.getElementById(`use_of_funds_amount_${i}`).value = useOfFundsAmount;
                    document.getElementById(`use_of_funds_desc_${i}`).value = useOfFundsDescription;
                }

                // Populate the rest of the form fields
                document.getElementById('loanProduct').value = loanData.loan_product || '';

                // Check the requested years amortized radio button
                const yearsAmortizedRadio = document.querySelector(`input[name="yearsAmortized"][value="${loanData.requested_year_amortized}"]`);
                if (yearsAmortizedRadio) {
                    yearsAmortizedRadio.checked = true;
                }
            } else {
                console.error('Error: Empty loan data array');
            }
        } else {
            // Handle errors if the request was not successful
            console.error('Error fetching loan data:', response.status, response.statusText);
            // Log the actual response to get more details
            console.log(response);
        }
    } catch (error) {
        console.error('An error occurred while fetching loan data:', error.message);
    }
}

// Call the function to fetch and display loan data when the page loads
window.onload = fetchAndDisplayLoanData;

// Function to close the form (you may need to implement this based on your requirements)
function closeForm() {
    // Implement the close form functionality as needed
}


document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('loanEditForm');
    const submitButton = document.getElementById('submitButton'); // Assuming you have a button with ID 'submitButton'
  
    form.addEventListener('submit', function (event) {
      event.preventDefault();
  
      // Collect form data
      const formData = {
        A_REQ: document.getElementById('amount_requested').value,
        L_V: document.getElementById('projected_loan_to_value').value,
        REQ_DATE: document.getElementById('requested_close_date').value,
        PAYMENT: document.querySelector('input[name="payment_frequency"]:checked').value,
        L_PURPOSE: document.querySelector('input[name="loan_purpose"]:checked').value,
        L_PURPOSE_O: document.getElementById('loan_purpose_other').value,
        S_D_1: document.getElementById('source_of_funds_desc_1').value,
        S_A_1: document.getElementById('source_of_funds_amount_1').value,
        U_D_1: document.getElementById('use_of_funds_desc_1').value,
        U_A_1: document.getElementById('use_of_funds_amount_1').value,
        S_D_2: document.getElementById('source_of_funds_desc_2').value,
        S_A_2: document.getElementById('source_of_funds_amount_2').value,
        U_D_2: document.getElementById('use_of_funds_desc_2').value,
        U_A_2: document.getElementById('use_of_funds_amount_2').value,
        S_D_3: document.getElementById('source_of_funds_desc_3').value,
        S_A_3: document.getElementById('source_of_funds_amount_3').value,
        U_D_3: document.getElementById('use_of_funds_desc_3').value,
        U_A_3: document.getElementById('use_of_funds_amount_3').value,
        S_D_4: document.getElementById('source_of_funds_desc_4').value,
        S_A_4: document.getElementById('source_of_funds_amount_4').value,
        U_D_4: document.getElementById('use_of_funds_desc_4').value,
        U_A_4: document.getElementById('use_of_funds_amount_4').value,
        L_PRODUCT: document.getElementById('loanProduct').value,
        REQ_YR_AMORT: document.querySelector('input[name="yearsAmortized"]:checked').value,
      };
  
      // Send data to backend using fetch API
      fetch('/updateLoan', {
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
  