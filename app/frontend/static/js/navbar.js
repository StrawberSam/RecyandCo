document.addEventListener('DOMContentLoaded', () => {
  const menuToggle = document.getElementById('menu-toggle');
  const header = document.querySelector('header');

  if(menuToggle && header) {
    menuToggle.addEventListener('click', () => {
      header.classList.toggle('active');
    });
  }
});
