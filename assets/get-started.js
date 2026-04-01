// Get Started page - dropdown filter functionality
(function() {
  var grid = document.getElementById('versionGrid');
  if (!grid) return;

  var cards = grid.querySelectorAll('.gs-card');
  var countEl = document.getElementById('gsCount');
  var selects = document.querySelectorAll('.gs-select');

  function applyFilters() {
    var filters = {};
    selects.forEach(function(sel) {
      filters[sel.dataset.group] = sel.value;
    });

    var visible = 0;
    cards.forEach(function(card) {
      var tags = card.dataset.tags || '';
      var show = true;

      for (var group in filters) {
        var val = filters[group];
        if (val !== 'all' && tags.indexOf(val) === -1) {
          show = false;
          break;
        }
      }

      if (show) {
        card.classList.remove('gs-hidden');
        visible++;
      } else {
        card.classList.add('gs-hidden');
      }
    });

    if (countEl) {
      countEl.textContent = visible + ' / ' + cards.length;
    }
  }

  selects.forEach(function(sel) {
    sel.addEventListener('change', applyFilters);
  });

  applyFilters();
})();
