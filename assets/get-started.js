// Get Started page - filter functionality
(function() {
  const grid = document.getElementById('versionGrid');
  if (!grid) return;

  const cards = grid.querySelectorAll('.gs-card');
  const buttons = document.querySelectorAll('.gs-filter-btn');
  const countEl = document.getElementById('gsCount');

  function updateCount() {
    const visible = grid.querySelectorAll('.gs-card:not(.gs-hidden)').length;
    countEl.textContent = '显示 ' + visible + ' / ' + cards.length + ' 个版本';
  }

  buttons.forEach(function(btn) {
    btn.addEventListener('click', function() {
      const filter = this.dataset.filter;

      // Update active button
      buttons.forEach(function(b) { b.classList.remove('active'); });
      this.classList.add('active');

      // Filter cards
      cards.forEach(function(card) {
        if (filter === 'all') {
          card.classList.remove('gs-hidden');
        } else {
          var tags = card.dataset.tags || '';
          if (tags.indexOf(filter) !== -1) {
            card.classList.remove('gs-hidden');
          } else {
            card.classList.add('gs-hidden');
          }
        }
      });

      updateCount();
    });
  });

  updateCount();
})();
