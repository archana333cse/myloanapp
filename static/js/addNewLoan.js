// Function to show a specific tab
function showTab(tabId) {
  const tabs = document.querySelectorAll('.tab-panel');
  tabs.forEach(tab => {
    if (tab.id === tabId) {
      tab.classList.add('active');
    } else {
      tab.classList.remove('active');
    }
  });
}

// Function to check if all required fields are filled
function areAllFieldsFilled(form) {
  const requiredInputs = form.querySelectorAll('input[required]:not([type="radio"]), textarea, select');
  for (const input of requiredInputs) {
    if (!input.value.trim()) {
      return false;
    }
  }
  return true;
}

// Function to submit the form
async function submitForm(event) {
  event.preventDefault();

  const currentForm = event.target;
  if (areAllFieldsFilled(currentForm)) {
    try {
      const response = await fetch('/submit_loan', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(Object.fromEntries(new FormData(currentForm))),
      });

      const responseData = await response.json();

      if (response.ok) {
        alert(responseData.message);
        window.location.href = "application.html";

      } else {
        alert(`Error: ${responseData.error}`);
      }
    } catch (error) {
      alert(`An error occurred: ${error}`);
    }
  } else {
    alert('Form submission unsuccessful. Please fill in all required fields.');
  }
}

// Function to close the form and show tab2
function closeForm() {
  console.log("Close button clicked");
  window.location.href = '/application.html#tab2';
  showTab("tab2");
}

document.addEventListener('DOMContentLoaded', function () {
  // Add a submit event listener to the form
  const loanForm = document.getElementById('loanForm');
  loanForm.addEventListener('submit', submitForm);

  // Set the default tab to be displayed when the page loads
  showTab("tab1"); // Change "tab1" to the default tab you want to display initially

  // Add a click event listener to the close button
  const closeButton = document.getElementById('closeButton');
  closeButton.addEventListener('click', closeForm);
});
