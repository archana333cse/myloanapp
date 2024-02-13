
window.addEventListener("load", ()=>{
  const loader=dcument.querySelector(".loader");
  loader.classList.add("loader-hidden");

  loader.addEventListener("transitioned",()=>{
    document.body.removeChild("loader");
  })
})


// Function to toggle the dropdown
function toggleDropdown() {
    var dropdownContent = document.querySelector(".dropdown-content");
    if (dropdownContent.style.display === "block") {
      dropdownContent.style.display = "none";
    } else {
      dropdownContent.style.display = "block";
    }
  }
  