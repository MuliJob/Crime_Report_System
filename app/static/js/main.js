document.addEventListener('DOMContentLoaded', () => {
    const navLinks = document.querySelectorAll('.sidebar nav ul li a');
    const sections = document.querySelectorAll('.content-section');
    const reportedCrimesList = document.getElementById('reportedCrimesList');
  
    navLinks.forEach(link => {
      link.addEventListener('click', (event) => {
        event.preventDefault();
        const targetId = link.getAttribute('href').substring(1);
        
        sections.forEach(section => {
          if (section.id === targetId) {
            section.classList.add('active');
          } else {
            section.classList.remove('active');
          }
        });
      });
    });
  
    document.getElementById('crimeForm').addEventListener('submit', (event) => {
      event.preventDefault();
      const crimeType = document.getElementById('crimeType').value;
      const crimeDetails = document.getElementById('crimeDetails').value;
  
      const crimeItem = document.createElement('li');
      crimeItem.textContent = `Type: ${crimeType}, Details: ${crimeDetails}`;
      reportedCrimesList.appendChild(crimeItem);
  
      document.getElementById('crimeForm').reset();
    });
  
    document.getElementById('stolenPropertyForm').addEventListener('submit', (event) => {
      event.preventDefault();
      const propertyType = document.getElementById('propertyType').value;
      const propertyDetails = document.getElementById('propertyDetails').value;
  
      const propertyItem = document.createElement('li');
      propertyItem.textContent = `Type: ${propertyType}, Details: ${propertyDetails}`;
      reportedCrimesList.appendChild(propertyItem);
  
      document.getElementById('stolenPropertyForm').reset();
    });
  });


const navigationButtons = document.querySelectorAll('.navigation button');
const contentSections = document.querySelectorAll('.content-section');

navigationButtons.forEach(button => {
  button.addEventListener('click', (event) => {
    const targetSectionId = event.target.dataset.target;
    const targetSection = document.getElementById(targetSectionId);

    // Remove active class from all sections
    contentSections.forEach(section => section.classList.remove('active'));

    // Add active class to the clicked section
    targetSection.classList.add('active');

    // Update navigation button styles (optional)
    navigationButtons.forEach(button => button.classList.remove('active'));
    event.target.classList.add('active');
  });
});
  

  