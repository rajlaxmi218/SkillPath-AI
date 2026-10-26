// ===== ROADMAP TABS (Overview / Phase View / Skill View) =====
const tabs = document.querySelectorAll('.tab');

tabs.forEach(function(tab) {
  tab.addEventListener('click', function(event) {
    event.preventDefault();

    tabs.forEach(function(t) {
      t.classList.remove('active');
    });
    tab.classList.add('active');
  });
});

// ===== SIDEBAR MENU TOGGLE =====
const menuToggle = document.getElementById('menuToggle');
const navMenu = document.querySelector('.nav-menu');

menuToggle.addEventListener('click', function() {
  navMenu.classList.toggle('show');
});