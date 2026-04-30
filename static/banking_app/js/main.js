/* ═══════════════════════════════════════════════════
   VaultX Banking — main.js
   ═══════════════════════════════════════════════════ */
'use strict';

/* ── Password visibility toggle ─────────────────── */
function togglePwd(inputId, btn) {
  var input = document.getElementById(inputId);
  if (!input) return;
  var isHidden = input.type === 'password';
  input.type = isHidden ? 'text' : 'password';
  btn.innerHTML = isHidden
    ? '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94"/><path d="M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19"/><line x1="1" y1="1" x2="23" y2="23"/></svg>'
    : '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>';
}

/* ── CSRF ────────────────────────────────────────── */
function getCookie(name) {
  var m = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
  return m ? m.pop() : '';
}

/* ── Format INR ──────────────────────────────────── */
function formatINR(n) {
  return parseFloat(n).toLocaleString('en-IN', {
    minimumFractionDigits: 2, maximumFractionDigits: 2
  });
}

/* ── Wire a single group of PIN boxes ───────────── */
function wirePinGroup(group) {
  /* supports both .pin-group and .pin-input-group */
  var boxes  = Array.from(group.querySelectorAll('.pin-box'));
  var hidden = document.getElementById('pinHidden');
  if (!boxes.length) return;

  boxes.forEach(function(box, i) {
    box.addEventListener('keydown', function(e) {
      if (e.key === 'Backspace') {
        this.value = '';
        this.classList.remove('filled');
        sync();
        if (i > 0) boxes[i - 1].focus();
        return;
      }
      if (!/^\d$/.test(e.key) &&
          !['Tab','ArrowLeft','ArrowRight','Enter'].includes(e.key)) {
        e.preventDefault();
      }
    });

    box.addEventListener('input', function() {
      this.value = this.value.replace(/\D/g, '').slice(-1);
      this.classList.toggle('filled', !!this.value);
      sync();
      if (this.value && i < boxes.length - 1) boxes[i + 1].focus();
    });

    /* Paste support — paste "1234" fills all 4 boxes */
    box.addEventListener('paste', function(e) {
      e.preventDefault();
      var digits = (e.clipboardData.getData('text') || '').replace(/\D/g,'').slice(0,4);
      digits.split('').forEach(function(d, j) {
        if (boxes[j]) { boxes[j].value = d; boxes[j].classList.add('filled'); }
      });
      sync();
      var next = boxes[digits.length] || boxes[boxes.length - 1];
      if (next) next.focus();
    });
  });

  function sync() {
    if (hidden) hidden.value = boxes.map(function(b){ return b.value; }).join('');
  }
}

/* ── DOMContentLoaded ────────────────────────────── */
document.addEventListener('DOMContentLoaded', function() {

  /* ── Responsive Sidebar ── */
  var sidebar = document.querySelector('.sidebar');
  var toggle  = document.getElementById('sidebarToggle');

  var overlay = document.createElement('div');
  overlay.className = 'sidebar-overlay';
  document.body.appendChild(overlay);

  function openSidebar()  {
    if (sidebar) sidebar.classList.add('open');
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
  }
  function closeSidebar() {
    if (sidebar) sidebar.classList.remove('open');
    overlay.classList.remove('active');
    document.body.style.overflow = '';
  }

  if (toggle) {
    toggle.addEventListener('click', function() {
      sidebar && sidebar.classList.contains('open') ? closeSidebar() : openSidebar();
    });
  }
  overlay.addEventListener('click', closeSidebar);

  if (sidebar) {
    sidebar.querySelectorAll('.nav-link').forEach(function(link) {
      link.addEventListener('click', function() {
        if (window.innerWidth <= 768) closeSidebar();
      });
    });
  }

  window.addEventListener('resize', function() {
    if (window.innerWidth > 768) closeSidebar();
  });

  /* ── Auto-dismiss alerts ── */
  document.querySelectorAll('.alert').forEach(function(el) {
    setTimeout(function() {
      el.style.transition = 'opacity 0.4s';
      el.style.opacity = '0';
      setTimeout(function() { if (el.parentNode) el.remove(); }, 400);
    }, 5000);
  });

  /* ── Block negative amounts ── */
  document.querySelectorAll('input[type="number"]').forEach(function(inp) {
    inp.addEventListener('input', function() {
      if (parseFloat(this.value) < 0) this.value = '';
    });
  });

  /* ── Auto-wire ALL pin groups on page ──
     Supports BOTH .pin-group and .pin-input-group
  ── */
  pin-group.forEach(function(group) {
    wirePinGroup(group);
  });

  /* Focus first pin box on page load */
  var firstBox = document.querySelector('.pin-group .pin-box, .pin-input-group .pin-box');
  if (firstBox) firstBox.focus();

});
