// ===== Elements =====
const chapters = Array.from(document.querySelectorAll('.chapter'));
const sidebarLinks = Array.from(document.querySelectorAll('.sidebar-link'));
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const prevTitle = document.getElementById('prevTitle');
const nextTitle = document.getElementById('nextTitle');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const sidebarToggle = document.getElementById('sidebarToggle');
const bookSidebar = document.getElementById('bookSidebar');

const chapterIds = chapters.map(ch => ch.id);
const chapterTitles = chapters.map(ch => ch.querySelector('h1').textContent);
let currentIndex = 0;
const readSet = new Set();

// ===== Scroll spy =====
function updateActiveChapter() {
  const scrollY = window.scrollY + 120;
  let active = 0;

  chapters.forEach((ch, i) => {
    if (ch.offsetTop <= scrollY) active = i;
  });

  if (active !== currentIndex) {
    currentIndex = active;
    updateSidebar();
    updatePager();
  }

  // Mark as read if scrolled past 40% of chapter
  chapters.forEach((ch, i) => {
    const chBottom = ch.offsetTop + ch.offsetHeight * 0.4;
    if (scrollY >= chBottom && !readSet.has(i)) {
      readSet.add(i);
      updateProgress();
    }
  });
}

function updateSidebar() {
  sidebarLinks.forEach((link, i) => {
    link.classList.toggle('active', i === currentIndex);
  });
}

function updatePager() {
  if (currentIndex > 0) {
    prevBtn.classList.remove('hidden');
    prevBtn.href = '#' + chapterIds[currentIndex - 1];
    prevTitle.textContent = chapterTitles[currentIndex - 1];
  } else {
    prevBtn.classList.add('hidden');
  }

  if (currentIndex < chapters.length - 1) {
    nextBtn.classList.remove('hidden');
    nextBtn.href = '#' + chapterIds[currentIndex + 1];
    nextTitle.textContent = chapterTitles[currentIndex + 1];
  } else {
    nextBtn.classList.add('hidden');
  }
}

function updateProgress() {
  const total = chapters.length;
  const done = readSet.size;
  const pct = Math.round((done / total) * 100);
  progressFill.style.width = pct + '%';
  progressText.textContent = done + ' / ' + total;

  sidebarLinks.forEach((link, i) => {
    if (readSet.has(i) && i !== currentIndex) {
      link.classList.add('read');
    }
  });
}

// ===== Sidebar link clicks =====
sidebarLinks.forEach(link => {
  link.addEventListener('click', (e) => {
    e.preventDefault();
    const target = document.getElementById(link.dataset.chapter);
    if (target) {
      target.scrollIntoView({ behavior: 'smooth' });
      // Close mobile sidebar
      bookSidebar.classList.remove('open');
    }
  });
});

// ===== Pager clicks =====
[prevBtn, nextBtn].forEach(btn => {
  btn.addEventListener('click', (e) => {
    e.preventDefault();
    const id = btn.getAttribute('href').substring(1);
    const target = document.getElementById(id);
    if (target) target.scrollIntoView({ behavior: 'smooth' });
  });
});

// ===== Mobile sidebar toggle =====
sidebarToggle.addEventListener('click', () => {
  bookSidebar.classList.toggle('open');
});

// Close sidebar when clicking outside on mobile
document.addEventListener('click', (e) => {
  if (window.innerWidth <= 900 &&
      bookSidebar.classList.contains('open') &&
      !bookSidebar.contains(e.target) &&
      e.target !== sidebarToggle) {
    bookSidebar.classList.remove('open');
  }
});

// ===== Init =====
window.addEventListener('scroll', updateActiveChapter, { passive: true });
updateActiveChapter();
updatePager();
updateProgress();
