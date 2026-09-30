(() => {
  'use strict';
  const pages = JSON.parse(document.getElementById('offline-pages').textContent);
  const rootURL = new URL('.', location.href);
  const panel = document.getElementById('offline-reader');
  let frame = document.getElementById('offline-frame');
  const title = document.getElementById('offline-reader-title');
  const back = document.getElementById('offline-reader-back');
  const close = document.getElementById('offline-reader-close');
  let depth = 0;
  let lastFocus = null;
  let previousOverflow = '';

  function newFrame() {
    const next = document.createElement('iframe');
    next.id = 'offline-frame';
    next.title = '离线正文阅读';
    next.referrerPolicy = 'no-referrer';
    return next;
  }

  function pathFor(url) {
    if (url.origin !== rootURL.origin || !url.pathname.startsWith(rootURL.pathname)) return null;
    return decodeURIComponent(url.pathname.slice(rootURL.pathname.length));
  }

  function show(path, hash = '') {
    const source = pages[path];
    if (typeof source !== 'string') return;
    if (!panel.open) {
      lastFocus = document.activeElement;
      previousOverflow = document.body.style.overflow;
      document.body.style.overflow = 'hidden';
      panel.showModal();
    }
    const parsed = new DOMParser().parseFromString(source, 'text/html');
    title.textContent = parsed.title || '本地正文';
    const base = parsed.createElement('base');
    base.href = new URL(path, rootURL).href;
    parsed.head.prepend(base);
    // A fresh browsing context avoids adding iframe navigation entries to the
    // report's own back/forward history when switching embedded documents.
    const nextFrame = newFrame();
    nextFrame.onload = () => {
      const doc = nextFrame.contentDocument;
      doc.addEventListener('click', event => follow(event, base.href));
      if (hash) doc.getElementById(decodeURIComponent(hash.slice(1)))?.scrollIntoView();
    };
    nextFrame.srcdoc = '<!doctype html>\n' + parsed.documentElement.outerHTML;
    nextFrame.dataset.path = path;
    frame.replaceWith(nextFrame);
    frame = nextFrame;
    back.textContent = depth > 1 ? '返回上一页' : '返回报告';
    close.focus({preventScroll: true});
  }

  function hide() {
    if (!panel.open) return;
    panel.close();
    const blank = newFrame();
    frame.replaceWith(blank);
    frame = blank;
    document.body.style.overflow = previousOverflow;
    lastFocus?.focus({preventScroll: true});
  }

  function open(path, hash) {
    depth += 1;
    const next = new URL(location.href);
    next.hash = 'offline=' + encodeURIComponent(path) + (hash ? '&anchor=' + encodeURIComponent(hash) : '');
    history.pushState({offlineReader: true, path, hash, depth}, '', next);
    show(path, hash);
  }

  function returnToReport(hash = '') {
    if (depth) {
      const steps = depth;
      if (hash) addEventListener('popstate', () => {
        document.getElementById(decodeURIComponent(hash.slice(1)))?.scrollIntoView();
      }, {once: true});
      history.go(-steps);
    } else {
      hide();
    }
  }

  function follow(event, baseURL) {
    const link = event.target.closest?.('a[href]');
    if (!link || event.defaultPrevented || event.button > 0) return;
    const raw = link.getAttribute('href');
    // Keep anchors inside the current document; public sources open normally.
    if (!raw || raw.startsWith('#') || link.hasAttribute('download')) return;
    const url = new URL(raw, baseURL);
    const path = pathFor(url);
    if (Object.prototype.hasOwnProperty.call(pages, path)) {
      event.preventDefault();
      open(path, url.hash);
    } else if (panel.open && (path === 'longbridge-research.html' || path === 'index.html' || path === '')) {
      event.preventDefault();
      returnToReport(url.hash);
    } else if (panel.open && url.origin !== rootURL.origin) {
      link.target = '_blank';
      link.rel = 'noopener';
    }
  }

  document.addEventListener('click', event => follow(event, document.baseURI));
  back.addEventListener('click', () => depth ? history.back() : hide());
  close.addEventListener('click', () => returnToReport());
  panel.addEventListener('cancel', event => {event.preventDefault(); returnToReport();});
  addEventListener('popstate', event => {
    if (event.state?.offlineReader && pages[event.state.path]) {
      depth = event.state.depth;
      show(event.state.path, event.state.hash);
    } else {
      depth = 0;
      hide();
    }
  });
  const requested = new URLSearchParams(location.hash.slice(1));
  const requestedPath = requested.get('offline');
  const initialURL = new URL(location.href);
  if (pages[requestedPath]) initialURL.hash = '';
  history.replaceState(null, '', initialURL);
  if (pages[requestedPath]) open(requestedPath, requested.get('anchor') || '');
  document.documentElement.removeAttribute('data-offline-preparing');
  document.getElementById('offline-status').textContent = '全部页面已加载，可断网阅读';
})();
