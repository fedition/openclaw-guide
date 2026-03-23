// ===== Navbar scroll effect =====
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
  navbar.classList.toggle('scrolled', window.scrollY > 10);
});

// ===== Mobile nav toggle =====
const navToggle = document.getElementById('navToggle');
const navLinks = document.getElementById('navLinks');
navToggle.addEventListener('click', () => {
  navLinks.classList.toggle('open');
});
// Close mobile nav when clicking a link
navLinks.querySelectorAll('a').forEach(link => {
  link.addEventListener('click', () => navLinks.classList.remove('open'));
});

// ===== Version filter tabs =====
const filterTabs = document.querySelectorAll('.filter-tab');
const versionCards = document.querySelectorAll('.version-card');

filterTabs.forEach(tab => {
  tab.addEventListener('click', () => {
    filterTabs.forEach(t => t.classList.remove('active'));
    tab.classList.add('active');

    const filter = tab.dataset.filter;
    versionCards.forEach(card => {
      if (filter === 'all') {
        card.classList.remove('hidden');
      } else {
        const tags = card.dataset.tags || '';
        card.classList.toggle('hidden', !tags.includes(filter));
      }
    });
  });
});

// ===== Deploy toggle (cloud / local) =====
const deployTabs = document.querySelectorAll('.deploy-tab');
const deployContents = document.querySelectorAll('.deploy-content');

deployTabs.forEach(tab => {
  tab.addEventListener('click', () => {
    deployTabs.forEach(t => t.classList.remove('active'));
    deployContents.forEach(c => c.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById('deploy-' + tab.dataset.deploy).classList.add('active');
  });
});

// ===== Smooth scroll for anchor links =====
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', (e) => {
    const target = document.querySelector(anchor.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth' });
    }
  });
});
