 
  // function navigateToApplication() {
  //   // Replace "application.html" with the correct file path if necessary
  //   window.location.href = 'application.html';
  // }


  
//===========================================


  // Function to show the loader
  function showLoader() {
    document.getElementById('loader-container').style.display = 'flex';
  }
  
  // Function to hide the loader
  function hideLoader() {
    document.getElementById('loader-container').style.display = 'none';
  }
  //=====================================================================

  console.log("addNewLoan.js loaded");
  function navigateToAnalytics() {   
    window.location.href = 'analytics.html';
  }

  function downloadTemplate() {
    fetch('/get_template_url')
      .then(response => response.json())
      .then(data => {
        window.open(data.template_url, '_blank');
      })
      .catch(error => {
        console.error('Error:', error);
      });
  }

// // ====================================================================================


    // JavaScript code to handle tab switching
    function showTab(tabId ) {
      //console.log("showTab called for tabId: ", tabId);
      const tabHeaders = document.querySelectorAll(".tab-header");
     // const container = document.getElementById(containerId);
      for (const header of tabHeaders) {
        header.classList.remove("active");
      }

      const tabContents = document.querySelectorAll(".tab-panel");
      for (const tab of tabContents) {
        tab.style.display = "none";
      }

      document.querySelector(`[data-tab-id="${tabId}"]`).classList.add("active");

      const selectedTab = document.getElementById(tabId);
      selectedTab.style.display = "block";

      const selectedTabHeading = selectedTab.querySelector("h2").innerText;
      document.getElementById("selected-tab-heading").innerText = selectedTabHeading;
    }

    // Set the default tab to be displayed when the page loads
    document.addEventListener("DOMContentLoaded", function () {
      showTab("tab1"); // Change "tab1" to the default tab you want to display initially
    });



// ----------------------------------------------------------------------------------------------------
// existing BORROWER'S TAB

async function fetchExistingBorrower() {
  try {
    const response = await fetch('/get_existing_borrowers');
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    const data = await response.json();

    // Get a reference to the table body element
    const tableBody = document.getElementById('borrowerTableBody');

    // Clear the existing table rows
    tableBody.innerHTML = '';

    // Loop through the fetched data and create table rows
    data.data.forEach(row => {
      const newRow = document.createElement('tr');
      newRow.innerHTML = `
        <td>${row.A_ID}</td>
        <td>${row.APPLYING_AS}</td>
        <td>${row.TYPE_OF_APPLICANT}</td>
        <td>${row.BORROWER_NAME}</td>
        <td>
          <button class="edit-button" onclick="editBorrower(${row.A_ID}, '${row.TYPE_OF_APPLICANT}')">Edit</button>
          <button class="remove-button" onclick="removeBorrower(${row.A_ID}, '${row.TYPE_OF_APPLICANT}')">Remove</button>
        </td>
      `;
      tableBody.appendChild(newRow);
    });
  } catch (error) {
    console.error('Error fetching existing borrowers data:', error);
  }
}

function removeBorrower(aId, applicantType) {
  // Call the backend endpoint to remove the borrower
  fetch('/remove_borrower', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      aId: aId,
      applicantType: applicantType,
    }),
  })
  .then(response => response.json())
  .then(data => {
    if (data.message) {
      alert(data.message); // Show alert on successful removal
      fetchExistingBorrower(); // Refresh the table after removal
    } else {
      console.error(data.error);
    }
  })
  .catch(error => {
    console.error('Error:', error);
  });
}


function editBorrower(aId, applyingAs) {
  // Redirect to edit_borrower endpoint with the selected A_ID and applyingAs
  window.location.href = `/edit_borrower?a_id=${aId}&applying_as=${applyingAs}`;
}


// Call fetchExistingLoans() when the page loads to populate the table
window.addEventListener('load', fetchExistingBorrower);

//====================================================================================================
// Existing loans TAB

async function fetchExistingLoans() {
  try {
    const response = await fetch('/get_existing_loans');
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    const data = await response.json();

    // Get a reference to the table body element
    const tableBody = document.getElementById('loanTableBody');

    // Clear the existing table rows
    tableBody.innerHTML = '';

    // Loop through the fetched data and create table rows
    data.data.forEach(row => {
      const newRow = document.createElement('tr');
      newRow.innerHTML = `
        <td>${row.BORROWING_ID}</td>
        <td>${row.LOAN_PURPOSE}</td>
        <td>${row.AMOUNT_REQUESTED}</td>
        <td>${row.PAYMENT_FREQUENCY}</td>

        <td>
          <button class="edit-button" onclick="editLoan(${row.BORROWING_ID})">Edit</button>
          <button class="remove-button" onclick="removeLoanInfo(${row.BORROWING_ID})">Remove</button>
        </td>
      `;
      tableBody.appendChild(newRow);
    });
  } catch (error) {
    console.error('Error fetching existing loans data:', error);
  }
}

// Function to handle the removal of a loan
async function removeLoanInfo(borrowingId) {
  try {
    const response = await fetch('/remove_loan_info', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ borrowing_id: borrowingId }),
    });

    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    // Refresh the list of existing loans after removal
    fetchExistingLoans();
  } catch (error) {
    console.error('Error removing loan:', error);
  }
}


function editLoan(borrowingId) {
  try {
    // Make a POST request to the backend to store the selected BORROWING_ID in the session
    fetch(`/store_selected_borrowing_id?borrowing_id=${borrowingId}`, {
      method: 'POST',
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      // Redirect to editLoan.html
      window.location.href = '/editLoan.html';
    })
    .catch(error => {
      console.error('Error storing selected BORROWING_ID in the session:', error);
    });
  } catch (error) {
    console.error('An error occurred in editLoan:', error);
  }
}


// Function to reload the page
function reloadPage() {
  window.location.reload();
}

// Call fetchExistingLoans() when the page loads to populate the table
window.addEventListener('load', fetchExistingLoans);


//=============================================================================================================================

// Existing Collaterals TAB

async function fetchExistingCollaterals() {
  try {
    const response = await fetch('/get_existing_collaterals');
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    const data = await response.json();

    // Get a reference to the table body element
    const tableBody = document.getElementById('collateraltablebody');

    // Clear the existing table rows
    tableBody.innerHTML = '';

    // Loop through the fetched data and create table rows
    data.data.forEach(row => {
      const newRow = document.createElement('tr');
      newRow.innerHTML = `
        <td>${row.LOAN_ID}</td>
        <td>${row.STATE_OF_PROPERTY_LOCATION}</td>
        <td>${row.COUNTY_OF_PROPERTY_LOCATION}</td>
        <td>${row.TOTAL_ACRES}</td>
        <td>${row.ESTIMATED_VALUE_TOTAL_VALUE}</td>
        <td>
          <button class="edit-button" onclick="openEditCollateralPage()">Edit</button>
          <button class="remove-button" onclick="removeCollateral()">Remove</button>
        </td>
      `;
      tableBody.appendChild(newRow);
    });
  } catch (error) {
    console.error('Error fetching existing collaterals data:', error);
  }
}

// Function to handle the removal of a collateral
async function removeCollateral() {
  try {
    const response = await fetch('/remove_collateral_info', {
      method: 'POST',
    });

    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    // Refresh the list of existing collaterals after removal
    fetchExistingCollaterals();
  } catch (error) {
    console.error('Error removing collateral:', error);
  }
}

// Call fetchExistingCollaterals when the page loads to populate the table
window.addEventListener('load', fetchExistingCollaterals);


function openEditCollateralPage() {
  window.location.href = 'editCollateral.html';
}

//=============================================================================

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
  
      fetch('/submit_otherInfo', {
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

//=================================================================

// Existing other info TAB

async function fetchExistingOtherInfo() {
  try {
    const response = await fetch('/get_existing_otherinfo');
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    const data = await response.json();

    // Get a reference to the table body element
    const tableBody = document.getElementById('otherInfotablebody');

    // Clear the existing table rows
    tableBody.innerHTML = '';

    // Loop through the fetched data and create table rows
    data.data.forEach(row => {
      const newRow = document.createElement('tr');
      newRow.innerHTML = `
        <td>${row.LOAN_ID}</td>

        <td>${row.TOTAL_ACRES_OWNED}</td>
        <td>${row.TOTAL_ACRES_RENTED}</td>

        <td>
          <button class="edit-button" onclick="openEditOtherInfoPage()" >Edit</button>
          <button class="view-button" disabled>View</button>
        </td>
      `;
      tableBody.appendChild(newRow);
    });
  } catch (error) {
    console.error('Error fetching existing Other info data:', error);
  }
}

// Function to reload the page
function reloadPage() {
  window.location.reload();
}

function openEditOtherInfoPage() {
  window.location.href = 'editOtherinfo.html';
}
// Call fetchExistingcollaterals when the page loads to populate the table
window.addEventListener('load', fetchExistingcollaterals);

// Call fetchExistingOtherInfo() when the page loads to populate the table
window.addEventListener('load', fetchExistingOtherInfo);

//=====================================================================================================================================
//DOCUMENTS TAB (Malika)

document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("documentForm");
  const secondButton = document.getElementById("second-button");
  const thirdButton = document.getElementById("third-button");
  const fourthButton = document.getElementById("forth-button");
  const fileInput = document.getElementById("file-input");
  const documentTypeDropdown = document.getElementById("documentTypeDropdown");
  const fileDescDropdown = document.getElementById("fileDescDropdown"); // Add this line
  const documentTypeInput = document.getElementById("documentType");
  const docNameInput = document.getElementById("doc_name");
  const docDateInput = document.getElementById("doc_date");
  const fileNameInput = document.getElementById("file_name");
  const fileDescInput = document.getElementById("file_Desc");

  const CompID = 1;
  const UserID = 11;
  const LoanID = 2;
  const DocNum = 1;
  const VerNum = 1.0;

  let selectedDocumentType = ""; // To store the selected document type
  let selectedFileDesc = ""; // To store the selected file description // Add this line

  // Function to generate the new file name based on the convention
  function generateNewFileName(selectedFile) {
    const fileName = selectedFile.name;
    const docName = fileName.substring(0, fileName.lastIndexOf('.')) || fileName; // Extract document name without extension
    const newFileName = `${CompID}_${UserID}_${LoanID}_${DocNum}_${selectedDocumentType}_${selectedFileDesc}__${docName}_${VerNum}`; // Update this line
    return newFileName;
  }

  secondButton.addEventListener("click", function () {
    // Trigger the file input click when the second button is clicked
    fileInput.click();
  });

  thirdButton.addEventListener("change", function () {
    const selectedDate = thirdButton.value;
    docDateInput.value = selectedDate;
  });

  // Event listener to update the second button with the selected file name
  fileInput.addEventListener("change", function () {
    if (fileInput.files.length > 0) {
      const selectedFile = fileInput.files[0];
      const fileName = selectedFile.name;

      // Extract the base name without the extension
      const docName = fileName.substring(0, fileName.lastIndexOf('.')) || fileName;

      secondButton.value = fileName;
      fourthButton.value = generateNewFileName(selectedFile); // Set the fourth button's value

      // Update the hidden input fields
      docNameInput.value = docName;
      fileNameInput.value = fourthButton.value

    } else {
      secondButton.value = "Choose File";
      fourthButton.value = "File Name"; // Reset the fourth button text

      // Reset the hidden input fields
      docNameInput.value = "";
      docDateInput.value = "";
      fileNameInput.value = "";
    }
  });

    // Dropdown functionality for Document Type
  const documentTypeDropdownContent = document.querySelector(".dropdown-content");

  documentTypeDropdown.addEventListener("click", function () {
    // Toggle the class 'show' on the dropdown content when the dropdown button is clicked
    documentTypeDropdownContent.classList.toggle("show");

    // If the dropdown content is currently displayed, set the selectedDocumentType to an empty string
    // Otherwise, set it to the currently selected text content
    selectedDocumentType = documentTypeDropdownContent.classList.contains("show") ? "" : documentTypeDropdown.textContent;
  });

  documentTypeDropdownContent.addEventListener("click", function (e) {
    if (e.target && e.target.id) {
      // Handle the selection of document type here
      selectedDocumentType = e.target.textContent; // Store the selected document type
      documentTypeDropdownContent.classList.remove("show");
      documentTypeDropdown.textContent = selectedDocumentType;
      documentTypeInput.value = selectedDocumentType;

      // Update File Desc options based on the selected document type
      updateFileDescOptions();
    }
  });

  // Dropdown functionality for File Desc
  const fileDescDropdownContent = document.querySelector("#fileDescOptions");

  fileDescDropdown.addEventListener("click", function () {
    // Toggle the class 'show' on the dropdown content when the dropdown button is clicked
    fileDescDropdownContent.classList.toggle("show");
  });

  fileDescDropdownContent.addEventListener("click", function (e) {
    if (e.target && e.target.textContent) {
      // Handle the selection of file description here
      selectedFileDesc = e.target.textContent; // Store the selected file description
      fileDescDropdownContent.classList.remove("show");
      fileDescDropdown.textContent = selectedFileDesc;
      fileDescInput.value = selectedFileDesc;
      // You can add an input field for file description if needed
    }
  });

  // Function to update File Desc options based on the selected document type
  function updateFileDescOptions() {
    const fileDescOptionsContainer = document.getElementById("fileDescOptions");

    // Clear existing options
    fileDescOptionsContainer.innerHTML = "";

    // Define options based on the selected document type
    let options = [];

    switch (selectedDocumentType) {
      case "Borrower":
        options = ["Purpose of Loan/ Special circumstance", "Specify who will be the borrower(s) and guarantor(s)", "Mailing address for each borrower/guarantor", "SSN/Tax ID for each borrower/guarantor", "Copy of each driver's license for each natural person", "Self-pulled credit report or credit score for each natural person", "W2 or supports for other sources of income"];
        break;
      case "Business":
        options = ["Business Description", "Business plan [explain any major variances in finances]", "Marketing plan and marketing contract [who buys the crops/livestock]", "Financial statement (previous 3 years) [CPA prepared]", "Financial projection (next 1-2 years) and annual cash budget [monthly details]", "Full tax statements for each entity and person (previous 3 years)", "Personal Financial Statement (PFS) for each natural person (current)", "Copy of all existing mortgage notes", "Lists of any third-party credits (distributor, vendor, machinery, equipment)", "Copy of any leases (to or from the borrower)", "Entity organization documents - Articles of Organization or Incorporation", "Any operating agreements or any partnership agreements"];
        break;
      case "Collateral":
        options = ["Recent appraisal of proposed collateral", "Crops insurance summary", "Schedule of insurance", "APH reporting", "Acreage reporting", "Any conservation program"];
        break;
      default:
        break;
    }

    // Add new options
    options.forEach(option => {
      const optionElement = document.createElement("a");
      optionElement.href = "#";
      optionElement.textContent = option;
      fileDescOptionsContainer.appendChild(optionElement);
    });
  }

  // Call updateFileDescOptions when the page loads to set initial options
  window.addEventListener('load', updateFileDescOptions);

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData(form);
    const selectedFile = fileInput.files[0];
    const newFileName = generateNewFileName(selectedFile);
    formData.append("file", selectedFile, newFileName); // Append the file with the new name

    try {
      const response = await fetch("/uploadfile", {
        method: "POST",
        body: formData,
      });

      if (response.status === 200) {
        alert("File uploaded successfully!");
        const tableBody = document.getElementById('doctablebody');
        const newRow = document.createElement('tr');
        newRow.innerHTML = `
        <td>${selectedDocumentType}</td>
        <td>${docNameInput.value}</td>
        <td>${fileDescInput.value}</td>
        <td>${docDateInput.value}</td>
        <input type="submit" onclick="downloadDoc('${newFileName}')" value="&#xf019;" id="fifth-button" class="fas" title="Download File">
        <input type="submit" onclick="DeleteDoc('${newFileName}')" value="&#xf1f8;" id="sixth-button" class="fas" title="Delete File">
        `;
        tableBody.appendChild(newRow);
        form.reset();
        secondButton.value = "Choose File"; // Reset the second button text
        thirdButton.value = "Date & Time"; // Reset the third button text
        fourthButton.value = "File Name"; // Reset the fourth button text
        docNameInput.value = "";
        docDateInput.value = "";
        fileNameInput.value = "";
      } else {
        alert("File upload failed. Please try again.");
      }
    } catch (error) {
      console.error("Error:", error);
    }
  });
  // Call fetchExistingDocs when the page loads to populate the table with existing documents
  window.addEventListener('load', fetchExistingDocs);
});

async function fetchExistingDocs() {
  try {
    const response = await fetch('/get_previous_documents');
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    const data = await response.json();

    // Get a reference to the table body element
    const tableBody = document.getElementById('doctablebody');

    // Clear the existing table rows
    tableBody.innerHTML = '';

    // Loop through the fetched data and create table rows
    data.data.forEach(row => {
      const newRow = document.createElement('tr');
      newRow.innerHTML = `
        <td>${row.FILE_CATEGORY}</td>
        <td>${row.DOC_NAME}</td>
        <td>${row.FILE_DESC}</td>
        <td>${row.FILE_DATE_AS_OF}</td>
        <input type="submit" onclick="downloadDoc('${row.FILE_NAME}')" value="&#xf019;" id="fifth-button" class="fas" title="Download File">
        <input type="submit" onclick="DeleteDoc('${row.FILE_NAME}')" value="&#xf1f8;" id="sixth-button" class="fas" title="Delete File">
        `;
      tableBody.appendChild(newRow);
    });
  } catch (error) {
    console.error('Error:', error);
  }
}

//=================================================================================================================================
function downloadDoc(fileName) {
  fetch(`/get_Doc_url?file_name=${fileName}`)
    .then(response => response.json())
    .then(data => {
      window.open(data.Doc_url, '_blank');
    })
    .catch(error => {
      console.error('Error:', error);
    });
}

function DeleteDoc(fileName) {
  fetch(`/delete_Doc?file_name=${fileName}`, { method: 'DELETE' })
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP Error: ${response.status} - ${response.statusText}`);
      }
      return response.json();
    })
    .then(data => {
      // Show a custom modal or alert on success
      alert(`File ${fileName} deleted succes`);
      console.log('Success:', data.message);
      fetchExistingDocs();
      // Add any additional logic you need after successful deletion
    })
    .catch(error => {
      // Show an alert with the error message from the server response
      alert(`Error: ${error.message || 'An error occurred'}`);
      console.error('Error:', error);
    });
}




// -----------------------------------------------------
function logout() {
  fetch('/logout', {
    method: 'POST', // Or 'GET' based on your server setup
    headers: {
      'Content-Type': 'application/json'
      // You might need to include additional headers or session tokens here
    }
  })
  .then(response => {
    // Redirect the user to the landing page after logout
    window.location.href = '/landingpage.html'; // Redirect to the landing page
  })
  .catch(error => {
    console.error('Error logging out:', error);
  });
}

// ------------------------------------------------------

function openPreviewPage() {
    window.location.href = 'preview.html'; // Replace 'preview.html' with your actual preview page URL
}
