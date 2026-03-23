// ===== Role Tabs =====
const roleTabs = document.querySelectorAll('.role-tab');
const caseContents = document.querySelectorAll('.case-content');

roleTabs.forEach(tab => {
  tab.addEventListener('click', () => {
    roleTabs.forEach(t => t.classList.remove('active'));
    caseContents.forEach(c => c.classList.remove('active'));
    tab.classList.add('active');
    const target = document.querySelector(`.case-content[data-role="${tab.dataset.role}"]`);
    if (target) target.classList.add('active');
  });
});
