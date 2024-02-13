// Function to show the loader
function showLoader() {
    document.getElementById("loader-container").classList.remove("d-none");
}

// Function to hide the loader after a delay
function hideLoader() {
    setTimeout(function () {
        document.getElementById("loader-container").classList.add("d-none");
    }, 2000); // Set the delay to 30 seconds (3000 milliseconds)
}

// Event listener to show the loader when the page starts loading
document.addEventListener("DOMContentLoaded", function () {
    showLoader();
});

// Event listener to hide the loader after at least 30 seconds 
window.addEventListener("load", function () {
    hideLoader();
});
