// 虾逛 Analytics Tracker - 轻量级 PV/UV 统计
(function() {
  var endpoint = (location.hostname === 'localhost' || location.hostname === '127.0.0.1')
    ? 'http://localhost:8790/api/track'
    : 'http://139.180.152.53:8790/api/track';

  function getVisitorId() {
    var id = localStorage.getItem('_xa_vid');
    if (!id) {
      id = 'v_' + Math.random().toString(36).substr(2, 12) + Date.now().toString(36);
      localStorage.setItem('_xa_vid', id);
    }
    return id;
  }

  function track() {
    var data = {
      url: location.pathname,
      title: document.title,
      referrer: document.referrer || '',
      vid: getVisitorId(),
      screen: screen.width + 'x' + screen.height,
      lang: navigator.language || '',
      ts: Date.now()
    };

    if (navigator.sendBeacon) {
      navigator.sendBeacon(endpoint, JSON.stringify(data));
    } else {
      var xhr = new XMLHttpRequest();
      xhr.open('POST', endpoint, true);
      xhr.setRequestHeader('Content-Type', 'application/json');
      xhr.send(JSON.stringify(data));
    }
  }

  // Track on page load
  if (document.readyState === 'complete') {
    track();
  } else {
    window.addEventListener('load', track);
  }
})();
