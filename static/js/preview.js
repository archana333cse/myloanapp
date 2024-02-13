document.addEventListener('DOMContentLoaded', () => {
    // Fetch individual borrower data
    fetch('/individual_preview_data')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(individualData => {
            if (Object.keys(individualData).length !== 0) {
                displayBorrowerData('Individual Borrower Data', individualData);
            }
        })
        .catch(error => console.error('Error fetching individual borrower data:', error));

    // Fetch business borrower data
    fetch('/business_preview_data')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(businessData => {
            if (Object.keys(businessData).length !== 0) {
                displayBorrowerData('Business Borrower Data', businessData);
            }
        })
        .catch(error => console.error('Error fetching business borrower data:', error));

    function displayBorrowerData(title, data) {
        const borrowerInfo = document.getElementById('borrowerInfo');

        // Check if there is data available
        if (Object.keys(data).length !== 0) {
            const titleElement = document.createElement('h2');
            titleElement.textContent = title;
            borrowerInfo.appendChild(titleElement);

            // Display borrower information
            for (const aId in data) {
                const borrowerSection = document.createElement('div');
                borrowerSection.className = 'borrower-section';

                const header = document.createElement('h3');
                header.textContent = `A_ID: ${aId}`;
                borrowerSection.appendChild(header);

                const borrowerData = data[aId];
                borrowerData.forEach(entry => {
                    const form = document.createElement('form');

                    for (const key in entry) {
                        const label = document.createElement('label');
                        label.textContent = key.replace(/_/g, ' ');
                        const input = document.createElement('input');
                        input.type = 'text';
                        input.id = key;
                        input.name = key;
                        input.value = entry[key] || '';

                        form.appendChild(label);
                        form.appendChild(input);
                    }

                    borrowerSection.appendChild(form);
                });

                borrowerInfo.appendChild(borrowerSection);
            }
        }
    }
});



//=====================================================================================================================
document.addEventListener('DOMContentLoaded', () => {
    // Fetch loan preview data from the API
    fetch(`/loan_preview_data`) // Assuming the backend already includes the loan ID in the response
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const loanInfo = document.getElementById('loanInfo');
            loanInfo.innerHTML = '';

            // Assuming the backend response includes the loan ID
            const loanId = data.loanId; // Adjust this line based on the actual structure of your backend response

            if (Object.keys(data).length === 0) {
                const p = document.createElement('p');
                p.textContent = 'No loan information available';
                loanInfo.appendChild(p);
            } else {
                // Loop through each borrowing ID and its associated loan entries
                for (const borrowingId in data) {
                    const loanEntries = data[borrowingId];
                    const borrowingSection = document.createElement('div');
                    borrowingSection.className = 'borrowing-section';

                    const borrowingHeader = document.createElement('h3');
                    borrowingHeader.textContent = `Borrowing ID: ${borrowingId}`;
                    borrowingSection.appendChild(borrowingHeader);

                    loanEntries.forEach(loan_entry => {
                        // Create form and populate fields
                        const form = document.createElement('form');

                        // Create labels and input fields for each loan detail
                        const loanFields = Object.keys(loan_entry);

                        loanFields.forEach(fieldName => {
                            const label = document.createElement('label');
                            label.textContent = fieldName.replace(/_/g, ' '); // Replace underscores with spaces
                            const input = document.createElement('input');
                            input.type = 'text';
                            input.id = fieldName;
                            input.name = fieldName;
                            input.value = loan_entry[fieldName] || ''; // Display the loan data or empty string if not available

                            form.appendChild(label);
                            form.appendChild(input);
                        });

                        borrowingSection.appendChild(form);
                    });

                    loanInfo.appendChild(borrowingSection);
                }
            }
        })
        .catch(error => console.error('Error fetching loan preview data:', error));
});



//=====================================================================================================================

document.addEventListener('DOMContentLoaded', () => {
    fetch('/collateral_info')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const collateralInfo = document.getElementById('collateralInfo');
            collateralInfo.innerHTML = '';

            if (Object.keys(data).length === 0) {
                const p = document.createElement('p');
                p.textContent = 'No collateral information available';
                collateralInfo.appendChild(p);
            } else {
                for (const aId in data) {
                    const collateralEntries = data[aId];
                    const aIdSection = document.createElement('div');
                    aIdSection.className = 'collateral-section';

                    const aIdHeader = document.createElement('h3');
                    aIdHeader.textContent = `A_ID: ${aId}`;
                    aIdSection.appendChild(aIdHeader);

                    collateralEntries.forEach(collateralEntry => {
                        const form = document.createElement('form');

                        const collateralFields = Object.keys(collateralEntry);

                        collateralFields.forEach(fieldName => {
                            const label = document.createElement('label');
                            label.textContent = fieldName.replace(/_/g, ' ');
                            const input = document.createElement('input');
                            input.type = 'text';
                            input.id = fieldName;
                            input.name = fieldName;
                            input.value = collateralEntry[fieldName] || '';

                            form.appendChild(label);
                            form.appendChild(input);
                        });

                        aIdSection.appendChild(form);
                    });

                    collateralInfo.appendChild(aIdSection);
                }
            }
        })
        .catch(error => console.error('Error fetching collateral information:', error));
});


//=====================================================================================================================

document.addEventListener('DOMContentLoaded', () => {
    fetch('/other_info')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const otherInfo = document.getElementById('otherInfo');
            otherInfo.innerHTML = '';

            if (Object.keys(data).length === 0) {
                const p = document.createElement('p');
                p.textContent = 'No other information available';
                otherInfo.appendChild(p);
            } else {
                const categorizedData = categorizeByAID(data);

                for (const aId in categorizedData) {
                    const aIdSection = document.createElement('div');
                    aIdSection.className = 'other-section';

                    const aIdHeader = document.createElement('h3');
                    aIdHeader.textContent = `A_ID: ${aId}`;
                    aIdSection.appendChild(aIdHeader);

                    categorizedData[aId].forEach(otherEntry => {
                        const form = document.createElement('form');

                        for (const fieldName in otherEntry) {
                            const label = document.createElement('label');
                            label.textContent = fieldName.replace(/_/g, ' ');

                            const input = document.createElement('input');
                            input.type = 'text';
                            input.id = fieldName;
                            input.name = fieldName;
                            input.value = otherEntry[fieldName] || '';

                            form.appendChild(label);
                            form.appendChild(input);
                        }

                        aIdSection.appendChild(form);
                    });

                    otherInfo.appendChild(aIdSection);
                }
            }
        })
        .catch(error => console.error('Error fetching other information:', error));
});

function categorizeByAID(data) {
    const categorizedData = {};

    data.forEach(entry => {
        const aId = entry['A_ID'];
        if (!categorizedData[aId]) {
            categorizedData[aId] = [];
        }
        categorizedData[aId].push(entry);
    });

    return categorizedData;
}




//=====================================================================================================================

async function fetchDocuments() {
    try {
      const response = await fetch('/document_upload');
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const data = await response.json();
  
      const tableBody = document.getElementById('doctablebody');
      tableBody.innerHTML = '';
  
      // Loop through the fetched data and create table rows
      data.forEach(doc => {
        const newRow = document.createElement('tr');
        newRow.innerHTML = `
          <td>${doc.A_ID}</td>
          <td>${doc.LOAN_ID}</td>         
          <td>${doc.FILE_CATEGORY}</td>
          <td>${doc.FILE_DESC}</td>
          <td>${doc.DOC_NAME}</td>
          <td>${doc.FILE_DATE_AS_OF}</td>
        `;
        tableBody.appendChild(newRow);
      });
    } catch (error) {
      console.error('Error fetching document upload data:', error);
    }
  }
  
  // Call fetchDocumentUpload() when the page loads to populate the table
  window.addEventListener('load', fetchDocuments);
  


  async function sendToInvestor() {
    try {
        const response = await fetch('/update_loan_status', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({}),
        });

        if (response.ok) {
            // Status updated successfully
            alert('Application sent to Investor successfully!');
            // Perform any additional actions or navigate to a different page if needed
        } else {
            // Handle the error if the request was not successful
            console.error('Failed to update status:', response.statusText);
        }
    } catch (error) {
        // Handle any network or unexpected errors
        console.error('Error updating status:', error);
    }
}




//=====================================================================================================================
async function generatePDF() {
    const element = document.getElementById('preview-content'); // Element to be converted to PDF
    const opt = {
      margin:       10,
      filename:     'preview.pdf',
      image:        { type: 'jpeg', quality: 0.98 },
      html2canvas:  { scale: 2 },
      jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
    };
  
    // Generate PDF from the element
    html2pdf().from(element).set(opt).save(); // This will trigger the download of the generated PDF
  }
  
