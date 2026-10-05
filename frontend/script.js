/* ============================================================
   Vehicle Damage Analysis — Frontend Application
   ============================================================ */

'use strict';

const API = '';
const VIEW_KEYS = ['front', 'rear', 'left', 'right', 'closeup'];
const MAX_FILE_BYTES = 10 * 1024 * 1024;
const ALLOWED_TYPES = ['image/jpeg', 'image/jpg', 'image/png'];

const $  = (id) => document.getElementById(id);
const $$ = (sel) => Array.from(document.querySelectorAll(sel));

const state = {
  files: Object.fromEntries(VIEW_KEYS.map(v => [v, null])),
  videoFile: null,
  lastReport: null,
  camera: { stream: null, view: null, facing: 'environment', blob: null },
  user: null,
};

/* ============================================================
   VEHICLE HEATMAP SHAPES
   ============================================================ */
const VEHICLE_SVGS = {
  car_hatchback: `<svg viewBox="0 0 400 220" class="heatmap-svg"><ellipse cx="200" cy="195" rx="140" ry="10" fill="rgba(139,92,246,0.08)"/><path d="M70 140 l12-40 a14 14 0 0 1 13-9 h180 a14 14 0 0 1 13 9 l12 40 v34 a8 8 0 0 1-8 8 h-14 a8 8 0 0 1-8-8 v-10 H100 v10 a8 8 0 0 1-8 8 H78 a8 8 0 0 1-8-8z" fill="#17132e" stroke="#8b5cf6" stroke-width="1.5"/><circle class="heat critical" cx="90" cy="150" r="16"/><circle class="heat severe" cx="150" cy="110" r="14"/><circle class="heat moderate" cx="230" cy="120" r="12"/><circle class="heat low" cx="320" cy="150" r="11"/><circle cx="120" cy="178" r="13" fill="#0a0916" stroke="#3a3370" stroke-width="1.5"/><circle cx="290" cy="178" r="13" fill="#0a0916" stroke="#3a3370" stroke-width="1.5"/></svg>`,
  car_sedan: `<svg viewBox="0 0 400 220" class="heatmap-svg"><ellipse cx="200" cy="195" rx="150" ry="10" fill="rgba(139,92,246,0.08)"/><path d="M55 140 l12-44 a16 16 0 0 1 15-10 h206 a16 16 0 0 1 15 10 l12 44 v34 a8 8 0 0 1-8 8 h-16 a8 8 0 0 1-8-8 v-10 H92 v10 a8 8 0 0 1-8 8 H68 a8 8 0 0 1-8-8z" fill="#17132e" stroke="#8b5cf6" stroke-width="1.5"/><circle class="heat critical" cx="80" cy="150" r="18"/><circle class="heat severe" cx="150" cy="110" r="16"/><circle class="heat moderate" cx="230" cy="120" r="14"/><circle class="heat low" cx="320" cy="150" r="12"/><circle class="heat moderate" cx="200" cy="90" r="12"/><circle cx="120" cy="176" r="14" fill="#0a0916" stroke="#3a3370" stroke-width="1.5"/><circle cx="290" cy="176" r="14" fill="#0a0916" stroke="#3a3370" stroke-width="1.5"/></svg>`,
  car_suv: `<svg viewBox="0 0 400 220" class="heatmap-svg"><ellipse cx="200" cy="195" rx="160" ry="10" fill="rgba(139,92,246,0.08)"/><path d="M50 135 l10-40 a16 16 0 0 1 15-11 h250 a16 16 0 0 1 15 11 l10 40 v40 a8 8 0 0 1-8 8 h-16 a8 8 0 0 1-8-8 v-12 H82 v12 a8 8 0 0 1-8 8 H58 a8 8 0 0 1-8-8z" fill="#17132e" stroke="#8b5cf6" stroke-width="1.5"/><circle class="heat critical" cx="75" cy="145" r="18"/><circle class="heat severe" cx="150" cy="105" r="15"/><circle class="heat moderate" cx="230" cy="115" r="14"/><circle class="heat low" cx="330" cy="145" r="12"/><circle cx="120" cy="182" r="15" fill="#0a0916" stroke="#3a3370" stroke-width="1.5"/><circle cx="290" cy="182" r="15" fill="#0a0916" stroke="#3a3370" stroke-width="1.5"/></svg>`,
  car_luxury: `<svg viewBox="0 0 400 220" class="heatmap-svg"><ellipse cx="200" cy="195" rx="160" ry="10" fill="rgba(139,92,246,0.08)"/><path d="M45 145 l14-50 a18 18 0 0 1 17-12 h248 a18 18 0 0 1 17 12 l14 50 v30 a8 8 0 0 1-8 8 h-16 a8 8 0 0 1-8-8 v-10 H77 v10 a8 8 0 0 1-8 8 H58 a8 8 0 0 1-8-8z" fill="#17132e" stroke="#8b5cf6" stroke-width="1.5"/><circle class="heat critical" cx="70" cy="150" r="18"/><circle class="heat severe" cx="140" cy="100" r="16"/><circle class="heat moderate" cx="240" cy="110" r="14"/><circle class="heat low" cx="330" cy="150" r="12"/><circle cx="115" cy="180" r="15" fill="#0a0916" stroke="#3a3370" stroke-width="1.5"/><circle cx="285" cy="180" r="15" fill="#0a0916" stroke="#3a3370" stroke-width="1.5"/></svg>`,
  bike: `<svg viewBox="0 0 400 220" class="heatmap-svg"><ellipse cx="200" cy="200" rx="130" ry="8" fill="rgba(139,92,246,0.08)"/><circle cx="120" cy="150" r="45" fill="none" stroke="#3a3370" stroke-width="8"/><circle cx="120" cy="150" r="30" fill="none" stroke="#8b5cf6" stroke-width="2"/><circle cx="290" cy="150" r="45" fill="none" stroke="#3a3370" stroke-width="8"/><circle cx="290" cy="150" r="30" fill="none" stroke="#8b5cf6" stroke-width="2"/><path d="M120 150 L180 90 L240 90 L290 150 M180 90 L210 150 L120 150" fill="none" stroke="#8b5cf6" stroke-width="4" stroke-linejoin="round"/><path d="M240 90 L265 75 M240 90 L260 100" stroke="#8b5cf6" stroke-width="3" stroke-linecap="round"/><rect x="170" y="80" width="40" height="10" rx="4" fill="#17132e" stroke="#8b5cf6" stroke-width="1.5"/><circle class="heat critical" cx="200" cy="110" r="14"/><circle class="heat severe" cx="265" cy="85" r="11"/><circle class="heat moderate" cx="120" cy="140" r="10"/><circle class="heat low" cx="290" cy="140" r="9"/></svg>`,
  scooter: `<svg viewBox="0 0 400 220" class="heatmap-svg"><ellipse cx="200" cy="200" rx="120" ry="8" fill="rgba(139,92,246,0.08)"/><circle cx="130" cy="155" r="40" fill="none" stroke="#3a3370" stroke-width="8"/><circle cx="130" cy="155" r="26" fill="none" stroke="#8b5cf6" stroke-width="2"/><circle cx="280" cy="155" r="40" fill="none" stroke="#3a3370" stroke-width="8"/><circle cx="280" cy="155" r="26" fill="none" stroke="#8b5cf6" stroke-width="2"/><path d="M130 155 L180 90 L250 90 L280 155" fill="none" stroke="#8b5cf6" stroke-width="4"/><rect x="170" y="80" width="50" height="12" rx="5" fill="#17132e" stroke="#8b5cf6" stroke-width="1.5"/><path d="M250 90 L265 70" stroke="#8b5cf6" stroke-width="3" stroke-linecap="round"/><circle class="heat critical" cx="200" cy="115" r="13"/><circle class="heat severe" cx="265" cy="85" r="10"/><circle class="heat moderate" cx="130" cy="145" r="10"/></svg>`,
  truck: `<svg viewBox="0 0 400 220" class="heatmap-svg"><ellipse cx="200" cy="200" rx="160" ry="10" fill="rgba(139,92,246,0.08)"/><rect x="40" y="70" width="180" height="110" rx="4" fill="#17132e" stroke="#8b5cf6" stroke-width="1.5"/><path d="M220 90 L220 180 H340 L340 120 L300 90 z" fill="#17132e" stroke="#8b5cf6" stroke-width="1.5"/><path d="M240 100 h50 v30 H240 z" fill="rgba(139,92,246,0.15)" stroke="#8b5cf6" stroke-width="1"/><circle cx="90" cy="185" r="14" fill="#0a0916" stroke="#3a3370" stroke-width="1.5"/><circle cx="160" cy="185" r="14" fill="#0a0916" stroke="#3a3370" stroke-width="1.5"/><circle cx="280" cy="185" r="14" fill="#0a0916" stroke="#3a3370" stroke-width="1.5"/><circle class="heat critical" cx="60" cy="120" r="18"/><circle class="heat severe" cx="230" cy="110" r="14"/><circle class="heat moderate" cx="310" cy="140" r="12"/><circle class="heat low" cx="160" cy="100" r="11"/></svg>`,
  bus: `<svg viewBox="0 0 400 220" class="heatmap-svg"><ellipse cx="200" cy="200" rx="170" ry="10" fill="rgba(139,92,246,0.08)"/><rect x="40" y="60" width="320" height="120" rx="8" fill="#17132e" stroke="#8b5cf6" stroke-width="1.5"/><rect x="55" y="75" width="45" height="40" fill="rgba(139,92,246,0.15)" stroke="#8b5cf6" stroke-width="1"/><rect x="115" y="75" width="45" height="40" fill="rgba(139,92,246,0.15)" stroke="#8b5cf6" stroke-width="1"/><rect x="175" y="75" width="45" height="40" fill="rgba(139,92,246,0.15)" stroke="#8b5cf6" stroke-width="1"/><rect x="235" y="75" width="45" height="40" fill="rgba(139,92,246,0.15)" stroke="#8b5cf6" stroke-width="1"/><rect x="295" y="75" width="45" height="40" fill="rgba(139,92,246,0.15)" stroke="#8b5cf6" stroke-width="1"/><circle cx="100" cy="185" r="14" fill="#0a0916" stroke="#3a3370" stroke-width="1.5"/><circle cx="200" cy="185" r="14" fill="#0a0916" stroke="#3a3370" stroke-width="1.5"/><circle cx="300" cy="185" r="14" fill="#0a0916" stroke="#3a3370" stroke-width="1.5"/><circle class="heat critical" cx="60" cy="120" r="16"/><circle class="heat severe" cx="180" cy="120" r="14"/><circle class="heat moderate" cx="280" cy="120" r="12"/><circle class="heat low" cx="340" cy="120" r="11"/></svg>`,
  auto_rickshaw: `<svg viewBox="0 0 400 220" class="heatmap-svg"><ellipse cx="200" cy="200" rx="110" ry="8" fill="rgba(139,92,246,0.08)"/><path d="M100 160 L100 90 a10 10 0 0 1 10-10 h130 a10 10 0 0 1 10 10 v70 z" fill="#17132e" stroke="#8b5cf6" stroke-width="1.5"/><path d="M130 90 h80 v40 h-80 z" fill="rgba(139,92,246,0.15)" stroke="#8b5cf6" stroke-width="1"/><circle cx="130" cy="170" r="14" fill="#0a0916" stroke="#3a3370" stroke-width="1.5"/><circle cx="280" cy="170" r="12" fill="#0a0916" stroke="#3a3370" stroke-width="1.5"/><path d="M240 160 L280 160 L280 140" fill="none" stroke="#8b5cf6" stroke-width="3"/><circle class="heat critical" cx="120" cy="125" r="14"/><circle class="heat severe" cx="220" cy="115" r="12"/><circle class="heat moderate" cx="270" cy="150" r="10"/></svg>`,
  commercial: `<svg viewBox="0 0 400 220" class="heatmap-svg"><ellipse cx="200" cy="200" rx="170" ry="10" fill="rgba(139,92,246,0.08)"/><rect x="30" y="80" width="220" height="100" rx="4" fill="#17132e" stroke="#8b5cf6" stroke-width="1.5"/><path d="M250 100 L250 180 H370 L370 130 L330 100 z" fill="#17132e" stroke="#8b5cf6" stroke-width="1.5"/><path d="M270 115 h40 v25 H270 z" fill="rgba(139,92,246,0.15)" stroke="#8b5cf6" stroke-width="1"/><circle cx="80" cy="182" r="14" fill="#0a0916" stroke="#3a3370" stroke-width="1.5"/><circle cx="160" cy="182" r="14" fill="#0a0916" stroke="#3a3370" stroke-width="1.5"/><circle cx="300" cy="182" r="14" fill="#0a0916" stroke="#3a3370" stroke-width="1.5"/><circle class="heat critical" cx="50" cy="130" r="18"/><circle class="heat severe" cx="240" cy="120" r="14"/><circle class="heat moderate" cx="330" cy="150" r="12"/></svg>`,
};

function renderHeatmap(vehicleType) {
  const container = $("heatmapContainer");
  if (!container) return;
  const key = vehicleType && VEHICLE_SVGS[vehicleType] ? vehicleType : "car_sedan";
  container.innerHTML = VEHICLE_SVGS[key];
  container.setAttribute("data-vehicle", key);
  const heading = container.closest(".panel")?.querySelector("h3");
  if (heading) {
    const label = key.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());
    heading.textContent = `Vehicle Damage Heatmap — ${label}`;
  }
}

/* ============================================================
   TOAST
   ============================================================ */
let toastTimer = null;
function toast(msg, type = 'info', duration = 3000) {
  const el = $('toast');
  if (!el) return;
  el.textContent = msg;
  el.className = `toast show ${type}`;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.remove('show'), duration);
}

/* ============================================================
   SERVER HEALTH
   ============================================================ */
async function checkServer() {
  const el = $('serverStatus');
  if (!el) return;
  const txt = el.querySelector('.status-text');
  try {
    const res = await fetch(`${API}/api/health`, { cache: 'no-store' });
    if (!res.ok) throw new Error('bad status');
    el.classList.add('online');
    el.classList.remove('offline');
    if (txt) txt.textContent = 'Online';
  } catch {
    el.classList.add('offline');
    el.classList.remove('online');
    if (txt) txt.textContent = 'Offline';
  }
}
checkServer();
setInterval(checkServer, 15000);

/* ============================================================
   NAVBAR
   ============================================================ */
const navbar = $('navbar');
if (navbar) {
  window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.scrollY > 8);
  });
}

const mobileBtn = $('mobileMenuBtn');
const mobileDrawer = $('mobileDrawer');
if (mobileBtn && mobileDrawer) {
  mobileBtn.addEventListener('click', () => {
    const open = mobileDrawer.classList.toggle('open');
    mobileBtn.setAttribute('aria-expanded', String(open));
  });
  $$('.mobile-link').forEach(a => {
    a.addEventListener('click', () => {
      mobileDrawer.classList.remove('open');
      mobileBtn.setAttribute('aria-expanded', 'false');
    });
  });
}

function wireDropdown(btnId, menuId) {
  const btn = $(btnId);
  const menu = $(menuId);
  if (!btn || !menu) return;
  btn.addEventListener('click', (e) => {
    e.stopPropagation();
    const open = menu.classList.toggle('open');
    btn.setAttribute('aria-expanded', String(open));
    $$('.dropdown-menu').forEach(m => { if (m !== menu) m.classList.remove('open'); });
  });
  document.addEventListener('click', () => {
    menu.classList.remove('open');
    btn.setAttribute('aria-expanded', 'false');
  });
}
wireDropdown('notifBtn', 'notifMenu');
wireDropdown('profileBtn', 'profileMenu');

const navLinks = $$('.nav-link');
const sections = navLinks
  .map(l => l.getAttribute('href'))
  .filter(h => h && h.startsWith('#'))
  .map(id => document.querySelector(id))
  .filter(Boolean);

if ('IntersectionObserver' in window && sections.length) {
  const navObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        navLinks.forEach(l => l.classList.toggle('active', l.getAttribute('href') === `#${entry.target.id}`));
      }
    });
  }, { rootMargin: '-40% 0px -55% 0px' });
  sections.forEach(s => navObserver.observe(s));
}

const globalSearch = $('globalSearch');
if (globalSearch) {
  globalSearch.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      const q = globalSearch.value.trim();
      if (q) toast(`Searching for "${q}"…`, 'info');
    }
  });
}

/* ============================================================
   REVEAL ANIMATIONS
   ============================================================ */
const revealTargets = $$('.metric-card, .feature-card, .how-step, .result-card, .panel, .testi, .price-card, .tech-card');
revealTargets.forEach(el => el.classList.add('reveal'));
if ('IntersectionObserver' in window) {
  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('in');
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });
  revealTargets.forEach(el => revealObserver.observe(el));
} else {
  revealTargets.forEach(el => el.classList.add('in'));
}

/* ============================================================
   METRICS COUNTER
   ============================================================ */
function animateCounters() {
  $$('.metric-value[data-count]').forEach(el => {
    if (el.dataset.counted) return;
    const rect = el.getBoundingClientRect();
    if (rect.top > window.innerHeight || rect.bottom < 0) return;
    el.dataset.counted = '1';
    const target = parseFloat(el.dataset.count);
    const decimals = parseInt(el.dataset.decimals || '0', 10);
    const suffix = el.dataset.suffix || '';
    const duration = 1400;
    const start = performance.now();
    function tick(now) {
      const t = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - t, 3);
      const value = target * eased;
      el.textContent = decimals > 0
        ? value.toFixed(decimals) + suffix
        : Math.round(value).toLocaleString() + suffix;
      if (t < 1) requestAnimationFrame(tick);
      else el.textContent = decimals > 0
        ? target.toFixed(decimals) + suffix
        : target.toLocaleString() + suffix;
    }
    requestAnimationFrame(tick);
  });
}
window.addEventListener('scroll', animateCounters, { passive: true });
animateCounters();

/* ============================================================
   UPLOAD
   ============================================================ */
function humanSize(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
}

function setFile(view, file) {
  if (!file) return;
  if (!ALLOWED_TYPES.includes(file.type)) {
    toast(`Unsupported format for ${view}. Use JPG, JPEG, or PNG.`, 'error');
    return;
  }
  if (file.size > MAX_FILE_BYTES) {
    toast(`${file.name} exceeds 10 MB.`, 'error');
    return;
  }
  state.files[view] = file;

  const card = document.querySelector(`.upload-card[data-view="${view}"]`);
  if (!card) return;

  const preview = card.querySelector('.upload-preview');
  const nameEl  = card.querySelector('.file-name');
  const sizeEl  = card.querySelector('.file-size');
  const chip    = card.querySelector('.status-chip');

  if (preview) preview.src = URL.createObjectURL(file);
  if (nameEl)  nameEl.textContent  = file.name;
  if (sizeEl)  sizeEl.textContent  = humanSize(file.size);
  if (chip)    chip.textContent    = 'Ready';

  card.classList.add('has-image');
  updateUploadProgress();
}

function clearFile(view) {
  state.files[view] = null;
  const card = document.querySelector(`.upload-card[data-view="${view}"]`);
  const input = $(view);
  if (input) input.value = '';
  if (card) {
    const preview = card.querySelector('.upload-preview');
    if (preview) preview.src = '';
    card.classList.remove('has-image');
    const chip = card.querySelector('.status-chip');
    if (chip) chip.textContent = 'Awaiting upload';
    const nameEl = card.querySelector('.file-name');
    const sizeEl = card.querySelector('.file-size');
    if (nameEl) nameEl.textContent = '';
    if (sizeEl) sizeEl.textContent = '';
  }
  updateUploadProgress();
}

function updateUploadProgress() {
  const total = VIEW_KEYS.length;
  const ready = VIEW_KEYS.filter(v => state.files[v]).length;
  const pct = (ready / total) * 100;
  const fill = $('uploadProgressFill');
  const label = $('uploadProgressLabel');
  if (fill)  fill.style.width = pct + '%';
  if (label) label.textContent = `${ready} of ${total} views ready`;
}

VIEW_KEYS.forEach(view => {
  const card = document.querySelector(`.upload-card[data-view="${view}"]`);
  const input = $(view);
  if (!card || !input) return;

  card.addEventListener('click', (e) => {
    if (e.target.closest('.camera-btn') || e.target.closest('.mini-btn')) return;
    input.click();
  });

  input.addEventListener('change', () => {
    if (input.files && input.files[0]) setFile(view, input.files[0]);
  });

  ['dragenter', 'dragover'].forEach(evt => {
    card.addEventListener(evt, (e) => { e.preventDefault(); card.classList.add('dragover'); });
  });
  ['dragleave', 'drop'].forEach(evt => {
    card.addEventListener(evt, (e) => { e.preventDefault(); card.classList.remove('dragover'); });
  });
  card.addEventListener('drop', (e) => {
    const file = e.dataTransfer.files[0];
    if (file) setFile(view, file);
  });

  const replaceBtn = card.querySelector('.mini-btn.replace');
  const removeBtn  = card.querySelector('.mini-btn.remove');
  if (replaceBtn) replaceBtn.addEventListener('click', (e) => { e.stopPropagation(); input.click(); });
  if (removeBtn)  removeBtn.addEventListener('click',  (e) => { e.stopPropagation(); clearFile(view); });
});

updateUploadProgress();

/* ============================================================
   VIDEO UPLOAD
   ============================================================ */
const videoInput = $('video');
if (videoInput) {
  videoInput.addEventListener('change', () => {
    const file = videoInput.files[0];
    if (!file) return;
    if (file.size > 50 * 1024 * 1024) { toast('Video exceeds 50 MB.', 'error'); return; }
    state.videoFile = file;
    const card = videoInput.closest('.upload-card');
    const preview = card ? card.querySelector('video') : null;
    if (preview) preview.src = URL.createObjectURL(file);
    if (card) card.classList.add('has-image');
    toast('Video attached.', 'success');
  });
}

/* ============================================================
   CAMERA
   ============================================================ */
const cameraModal = $('cameraModal');
const cameraVideo = $('cameraVideo');
const cameraCanvas = $('cameraCanvas');
const snapshotPreview = $('snapshotPreview');
const cameraTitle = $('cameraTitle');
const cameraErrorEl = $('cameraError');

async function openCamera(view) {
  if (!cameraModal) return;
  state.camera.view = view;
  if (cameraTitle) cameraTitle.textContent = `Capture ${view} view`;
  cameraModal.classList.remove('hidden');
  if (cameraErrorEl) cameraErrorEl.classList.add('hidden');
  resetCameraUI();
  await startCamera();
}

function stopCamera() {
  if (state.camera.stream) {
    state.camera.stream.getTracks().forEach(t => t.stop());
    state.camera.stream = null;
  }
}

function resetCameraUI() {
  if (cameraVideo) cameraVideo.classList.remove('hidden');
  if (snapshotPreview) snapshotPreview.classList.add('hidden');
  const cap = $('captureBtn'), sw = $('switchCameraBtn'), rt = $('retakeBtn'), us = $('usePhotoBtn');
  if (cap) cap.classList.remove('hidden');
  if (sw)  sw.classList.remove('hidden');
  if (rt)  rt.classList.add('hidden');
  if (us)  us.classList.add('hidden');
}

async function startCamera() {
  stopCamera();
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    showCameraError('Camera not supported in this browser.');
    return;
  }
  try {
    state.camera.stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: { ideal: state.camera.facing }, width: { ideal: 1280 }, height: { ideal: 720 } },
      audio: false,
    });
    if (cameraVideo) cameraVideo.srcObject = state.camera.stream;
  } catch (err) {
    let msg = 'Unable to access camera.';
    if (err.name === 'NotAllowedError') msg = 'Camera permission denied. Please allow access.';
    else if (err.name === 'NotFoundError') msg = 'No camera device found. Use the Upload option instead.';
    else if (err.name === 'NotReadableError') msg = 'Camera is in use by another app.';
    showCameraError(msg);
  }
}

function showCameraError(msg) {
  if (!cameraErrorEl) return;
  cameraErrorEl.textContent = msg;
  cameraErrorEl.classList.remove('hidden');
  if (cameraVideo) cameraVideo.classList.add('hidden');
}

function closeCamera() {
  stopCamera();
  if (cameraModal) cameraModal.classList.add('hidden');
  state.camera.view = null;
  state.camera.blob = null;
}

function captureFrame() {
  if (!state.camera.stream || !cameraVideo || !cameraCanvas) return;
  const vw = cameraVideo.videoWidth;
  const vh = cameraVideo.videoHeight;
  cameraCanvas.width = vw;
  cameraCanvas.height = vh;
  cameraCanvas.getContext('2d').drawImage(cameraVideo, 0, 0, vw, vh);
  cameraCanvas.toBlob((blob) => {
    state.camera.blob = blob;
    if (snapshotPreview) {
      snapshotPreview.src = URL.createObjectURL(blob);
      snapshotPreview.classList.remove('hidden');
    }
    if (cameraVideo) cameraVideo.classList.add('hidden');
    const cap = $('captureBtn'), sw = $('switchCameraBtn'), rt = $('retakeBtn'), us = $('usePhotoBtn');
    if (cap) cap.classList.add('hidden');
    if (sw)  sw.classList.add('hidden');
    if (rt)  rt.classList.remove('hidden');
    if (us)  us.classList.remove('hidden');
  }, 'image/jpeg', 0.92);
}

function usePhoto() {
  if (!state.camera.blob || !state.camera.view) return;
  const view = state.camera.view;
  const filename = `${view}_${Date.now()}.jpg`;
  const file = new File([state.camera.blob], filename, { type: 'image/jpeg' });
  setFile(view, file);
  closeCamera();
}

$$('.camera-btn').forEach(btn => {
  btn.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    openCamera(btn.dataset.view);
  });
});

const closeCam  = $('closeCameraBtn'); if (closeCam)  closeCam.addEventListener('click', closeCamera);
const capBtn    = $('captureBtn');     if (capBtn)    capBtn.addEventListener('click', captureFrame);
const retakeBtn = $('retakeBtn');      if (retakeBtn) retakeBtn.addEventListener('click', () => { state.camera.blob = null; resetCameraUI(); });
const useBtn    = $('usePhotoBtn');    if (useBtn)    useBtn.addEventListener('click', usePhoto);
const switchBtn = $('switchCameraBtn');if (switchBtn) switchBtn.addEventListener('click', () => {
  state.camera.facing = state.camera.facing === 'environment' ? 'user' : 'environment';
  startCamera();
});

if (cameraModal) {
  cameraModal.addEventListener('click', (e) => { if (e.target === cameraModal) closeCamera(); });
}
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && cameraModal && !cameraModal.classList.contains('hidden')) closeCamera();
});

/* ============================================================
   GEOLOCATION
   ============================================================ */
async function detectMyLocation() {
  const statusEl = $('locationStatus');
  const btn = $('detectLocationBtn');

  const setStatus = (text, cls = '') => {
    if (statusEl) {
      statusEl.textContent = text;
      statusEl.className = 'location-status ' + cls;
    }
  };

  if (!navigator.geolocation) {
    setStatus('Geolocation not supported. Trying IP…', 'error');
    await detectByIP();
    return;
  }

  if (btn) btn.disabled = true;
  setStatus('Detecting your location…', 'loading');

  navigator.geolocation.getCurrentPosition(
    (position) => {
      const lat = position.coords.latitude;
      const lon = position.coords.longitude;
      const accuracy = position.coords.accuracy;

      if ($('lat')) $('lat').value = lat.toFixed(6);
      if ($('lon')) $('lon').value = lon.toFixed(6);

      const note = `Accuracy ±${Math.round(accuracy)} m · just now`;
      if ($('latNote')) $('latNote').textContent = note;
      if ($('lonNote')) $('lonNote').textContent = note;

      setStatus(`Detected (${lat.toFixed(4)}, ${lon.toFixed(4)})`, 'success');
      toast('📍 Location detected.', 'success');
      loadShopsFromSensors();
      if (btn) btn.disabled = false;
    },
    (error) => {
      if (error.code === error.PERMISSION_DENIED) {
        setStatus('Permission denied. Trying IP lookup…', 'error');
        detectByIP();
      } else if (error.code === error.POSITION_UNAVAILABLE) {
        setStatus('Location unavailable.', 'error');
        if (btn) btn.disabled = false;
      } else if (error.code === error.TIMEOUT) {
        setStatus('Location request timed out.', 'error');
        if (btn) btn.disabled = false;
      } else {
        setStatus('Unable to detect location.', 'error');
        if (btn) btn.disabled = false;
      }
    },
    { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 }
  );
}

async function detectByIP() {
  const statusEl = $('locationStatus');
  const btn = $('detectLocationBtn');
  try {
    const res = await fetch('https://ipapi.co/json/');
    if (!res.ok) throw new Error('IP lookup failed');
    const data = await res.json();
    const lat = parseFloat(data.latitude);
    const lon = parseFloat(data.longitude);

    if ($('lat')) $('lat').value = lat.toFixed(6);
    if ($('lon')) $('lon').value = lon.toFixed(6);

    const note = `${data.city || ''}, ${data.country_name || ''} · IP-based`;
    if ($('latNote')) $('latNote').textContent = note;
    if ($('lonNote')) $('lonNote').textContent = note;

    if (statusEl) {
      statusEl.textContent = `Approximate: ${data.city || ''}, ${data.region || ''}`;
      statusEl.className = 'location-status success';
    }
    toast('📍 Approximate location via IP.', 'info');
    loadShopsFromSensors();
  } catch (e) {
    console.warn('IP fallback failed:', e);
    if (statusEl) {
      statusEl.textContent = 'Location unavailable. Enter manually.';
      statusEl.className = 'location-status error';
    }
  } finally {
    if (btn) btn.disabled = false;
  }
}

function clearLocation() {
  if ($('lat')) $('lat').value = 19.0760;
  if ($('lon')) $('lon').value = 72.8770;
  if ($('latNote')) $('latNote').textContent = 'Mumbai, IN (default)';
  if ($('lonNote')) $('lonNote').textContent = 'Last updated: just now';
  const statusEl = $('locationStatus');
  if (statusEl) {
    statusEl.textContent = 'Reset to default';
    statusEl.className = 'location-status';
  }
  toast('Location cleared.', 'info');
}

/* ============================================================
   IOT SIMULATION
   ============================================================ */
const simulateBtn = $('simulateSensorsBtn');
if (simulateBtn) {
  simulateBtn.addEventListener('click', () => {
    const impact = +(Math.random() * 5 + 1).toFixed(1);
    const rotation = Math.round(Math.random() * 120 + 20);
    const lat = +(19 + Math.random() * 2).toFixed(4);
    const lon = +(72 + Math.random() * 2).toFixed(4);
    if ($('impact'))   $('impact').value = impact;
    if ($('rotation')) $('rotation').value = rotation;
    if ($('lat'))      $('lat').value = lat;
    if ($('lon'))      $('lon').value = lon;
    toast('Simulated sensor data applied.', 'info');
    if (window._socket && window._socket.connected) {
      window._socket.emit('sensor_stream', { type: 'accelerometer', magnitude: impact });
    }
  });
}

/* ============================================================
   ANALYSIS
   ============================================================ */
function resetSteps() {
  $$('.analysis-steps .step').forEach(s => s.classList.remove('active', 'done'));
}
function markStep(i, cls) {
  const step = document.querySelector(`.analysis-steps .step[data-step="${i}"]`);
  if (!step) return;
  step.classList.remove('active', 'done');
  step.classList.add(cls);
}
async function runAnalysisSteps() {
  resetSteps();
  for (let i = 1; i <= 8; i++) {
    markStep(i, 'active');
    await new Promise(r => setTimeout(r, 180));
    markStep(i, 'done');
  }
}

async function pushSensors() {
  const impact   = parseFloat($('impact')?.value)   || 0;
  const rotation = parseFloat($('rotation')?.value) || 0;
  const lat      = parseFloat($('lat')?.value)      || 0;
  const lon      = parseFloat($('lon')?.value)      || 0;

  const push = (payload) =>
    fetch(`${API}/api/sensor/ingest`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }).catch(() => null);

  await fetch(`${API}/api/sensor/reset`, { method: 'POST' }).catch(() => null);
  await push({ type: 'accelerometer', x: 0, y: 0, z: impact, magnitude: impact });
  await push({ type: 'gyroscope', x: 0, y: 0, z: rotation, magnitude: rotation });
  await push({ type: 'gps', location: { lat, lon } });
}

async function analyze() {
  const btn = $('analyzeBtn');
  const status = $('status');
  const vehicleType = $('vehicleType')?.value || "";

  if (!vehicleType) {
    toast('Please select a vehicle type first.', 'error');
    if (status) status.textContent = 'Select a vehicle type.';
    return;
  }

  const ready = VIEW_KEYS.filter(v => state.files[v]);
  if (!ready.length) {
    toast('Please upload at least one vehicle image.', 'error');
    if (status) status.textContent = 'Upload at least one image.';
    return;
  }

  const latNow = parseFloat($('lat')?.value);
  const lonNow = parseFloat($('lon')?.value);
  const stillDefault = Math.abs(latNow - 19.0760) < 0.001 && Math.abs(lonNow - 72.8770) < 0.001;
  if (stillDefault && navigator.geolocation) {
    if (status) status.textContent = 'Detecting location…';
    await new Promise((resolve) => {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          if ($('lat')) $('lat').value = pos.coords.latitude.toFixed(6);
          if ($('lon')) $('lon').value = pos.coords.longitude.toFixed(6);
          resolve();
        },
        () => resolve(),
        { enableHighAccuracy: true, timeout: 5000 }
      );
    });
  }

  btn.disabled = true;
  if (status) status.textContent = 'Pushing sensor data…';

  try {
    await pushSensors();
    if (status) status.textContent = 'Analyzing damage…';

    const form = new FormData();
    ready.forEach(v => form.append(v, state.files[v], state.files[v].name));
    form.append('vehicle_type', vehicleType);

    const stepsPromise = runAnalysisSteps();

    const res = await fetch(`${API}/api/damage/analyze`, { method: 'POST', body: form });
    if (!res.ok) {
      const errText = await res.text().catch(() => '');
      throw new Error(errText || `Server responded ${res.status}`);
    }
    const data = await res.json();
    data.vehicle_type = vehicleType;

    await stepsPromise;

    renderResults(data);
    state.lastReport = data;

    if (status) status.textContent = 'Analysis complete.';
    toast('Assessment complete.', 'success');
  } catch (err) {
    if (status) status.textContent = `Analysis failed: ${err.message}`;
    toast(`Analysis failed: ${err.message}`, 'error', 5000);
  } finally {
    btn.disabled = false;
  }
}

/* ============================================================
   RENDER RESULTS
   ============================================================ */
function prettify(text) {
  if (!text) return '—';
  return String(text).replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

function levelClass(level) {
  const l = (level || '').toLowerCase();
  if (l.includes('critical')) return 'critical';
  if (l.includes('high')) return 'high';
  if (l.includes('medium') || l.includes('moderate')) return 'medium';
  return 'low';
}

function renderResults(data) {
  const results = $('results');
  if (!results) return;
  results.classList.remove('hidden');

  const fusion = data.fusion || {};
  const hidden = data.hidden_damage || {};
  const repair = data.repair || {};
  const cost   = data.cost || {};
  const views  = data.views || {};

  const score = data.severity_score ?? Math.round((fusion.fused_severity_score || 0) * 100);
  const label = data.severity_label ?? prettify(fusion.dominant_damage);
  if ($('dominant'))       $('dominant').textContent = prettify(fusion.dominant_damage);
  if ($('fusedSeverity'))  $('fusedSeverity').textContent = `${score}/100 · ${label}`;
  if ($('numDetections'))  $('numDetections').textContent = (fusion.fused_detections || []).length;
  if ($('numViews'))       $('numViews').textContent = Object.keys(views).length;

  const riskLvl = $('riskLevel');
  if (riskLvl) {
    const cls = levelClass(hidden.risk_level);
    riskLvl.textContent = (hidden.risk_level || '—').toUpperCase();
    riskLvl.className = `risk-badge ${cls}`;
  }
  if ($('riskRec'))   $('riskRec').textContent = hidden.inspection_recommendation || '—';
  if ($('riskScore')) $('riskScore').textContent = (hidden.risk_score != null) ? `${Math.round(hidden.risk_score * 100)}%` : '—';

  const pct = (hidden.risk_score ?? 0) * 100;
  const fill = $('riskFill');
  if (fill) requestAnimationFrame(() => { fill.style.width = pct + '%'; });

  const gaugePath = $('riskGaugePath');
  if (gaugePath) {
    const dash = 157;
    const offset = dash - (pct / 100) * dash;
    gaugePath.style.transition = 'stroke-dashoffset 1s ease';
    gaugePath.setAttribute('stroke-dashoffset', String(offset));
  }

  if ($('repairAction')) $('repairAction').textContent = (repair.action || '—').toUpperCase();
  if ($('repairDesc'))   $('repairDesc').textContent = repair.description || '—';
  if ($('component'))    $('component').textContent = prettify(data.component);

  const currency = cost.currency || 'INR';
  if ($('costRange')) $('costRange').textContent = `${currency} ${(cost.cost_min ?? 0).toLocaleString()} – ${(cost.cost_max ?? 0).toLocaleString()}`;
  if ($('currency'))  $('currency').textContent = currency;

  const mid = ((cost.cost_min ?? 0) + (cost.cost_max ?? 0)) / 2;
  if ($('costParts'))      $('costParts').textContent      = `${currency} ${Math.round(mid * 0.65).toLocaleString()}`;
  if ($('costLabor'))      $('costLabor').textContent      = `${currency} ${Math.round(mid * 0.25).toLocaleString()}`;
  if ($('costInspection')) $('costInspection').textContent = `${currency} ${Math.round(mid * 0.10).toLocaleString()}`;
  if ($('costConfidence')) {
    const conf = Math.round((fusion.fused_severity_score || 0.9) * 100);
    $('costConfidence').textContent = `${Math.min(97, Math.max(78, conf))}%`;
  }

  const distEl = $('classDist');
  if (distEl) {
    const dist = fusion.class_distribution || {};
    distEl.innerHTML = '';
    const total = Object.values(dist).reduce((a, b) => a + b, 0) || 1;
    const entries = Object.entries(dist);
    if (!entries.length) {
      distEl.innerHTML = '<span class="class-pill">No damage classes detected</span>';
    } else {
      entries.forEach(([c, count]) => {
        const p = Math.round((count / total) * 100);
        const pill = document.createElement('span');
        pill.className = 'class-pill';
        pill.innerHTML = `${prettify(c)}: <strong>${count}</strong> <span class="pct">${p}%</span>`;
        distEl.appendChild(pill);
      });
    }
  }

  const annEl = $('annotated');
  if (annEl) {
    annEl.innerHTML = '';
    const ann = data.annotated_images || {};
    const annEntries = Object.entries(ann);
    if (!annEntries.length) {
      annEl.innerHTML = '<p class="panel-sub">No annotated images available.</p>';
    } else {
      annEntries.forEach(([view, path]) => {
        const filename = path.split(/[\\/]/).pop();
        const fig = document.createElement('figure');
        const img = document.createElement('img');
        img.src = `${API}/api/damage/result/${filename}`;
        img.alt = `${view} annotated`;
        fig.appendChild(img);

        const overlay = document.createElement('span');
        overlay.className = 'annotated-overlay';
        overlay.textContent = prettify(view);
        fig.appendChild(overlay);

        const risk = document.createElement('span');
        risk.className = 'annotated-risk-dot';
        const lvl = levelClass(hidden.risk_level);
        const colors = { low: '#22c55e', medium: '#f59e0b', high: '#ef4444', critical: '#dc2626' };
        risk.style.background = colors[lvl] || '#22c55e';
        fig.appendChild(risk);

        const cap = document.createElement('figcaption');
        const sev = (views[view]?.severity?.severity) || 'n/a';
        const detCount = (views[view]?.detections || []).length;
        cap.innerHTML = `<span class="view-tag">${prettify(view)}</span><span class="view-meta">${detCount} detection${detCount !== 1 ? 's' : ''} · ${prettify(sev)}</span>`;

        const ev = views[view]?.evidence;
        if (ev && ev.evidence_id) {
          cap.innerHTML += `<br><span class="view-meta" style="font-size:0.68rem">EV-ID: ${ev.evidence_id}</span>`;
        }
        fig.appendChild(cap);
        fig.addEventListener('click', () => openLightbox(img.src, img.alt));
        annEl.appendChild(fig);
      });
    }
  }

  const insDate = new Date().toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
  if ($('insId'))       $('insId').textContent = data.inspection_id || '—';
  if ($('insVehicle'))  $('insVehicle').textContent = prettify(data.vehicle_type);
  if ($('insDate'))     $('insDate').textContent = insDate;
  if ($('insImages'))   $('insImages').textContent = `${Object.keys(views).length} / 5`;
  if ($('insSeverity')) $('insSeverity').textContent = `${prettify(fusion.dominant_damage)} · ${label}`;
  if ($('insRisk'))     $('insRisk').textContent = `${(hidden.risk_level || '—').toUpperCase()} (${Math.round((hidden.risk_score || 0) * 100)}%)`;
  if ($('insCost'))     $('insCost').textContent = `${currency} ${(cost.cost_min ?? 0).toLocaleString()} – ${(cost.cost_max ?? 0).toLocaleString()}`;
  if ($('insAction'))   $('insAction').textContent = prettify(repair.action);
  if ($('resultsTimestamp')) $('resultsTimestamp').textContent = `Generated ${new Date().toLocaleTimeString()}`;

  // Dynamic Repair Recommendation Breakdown
  const cmp = prettify(data.component) || "Component";
  const action = (repair.action || "repair").toUpperCase();

  const immEl = $('rbImmediate');
  if (immEl) {
    const items = [];
    if (hidden.risk_level === "high" || hidden.risk_level === "critical") {
      items.push("Professional inspection required");
      items.push("Avoid driving if structural damage suspected");
    } else if (hidden.risk_level === "medium") {
      items.push("Consider inspection for hidden damage");
      items.push("Monitor for any post-accident changes");
    } else {
      items.push("No immediate action required");
      items.push("Complete recommended repairs when convenient");
    }
    items.push("Photograph all affected areas");
    immEl.innerHTML = items.map(t => `<li>${t}</li>`).join("");
  }

  const repEl = $('rbRepairs');
  if (repEl) {
    const items = [];
    if (action === "REPLACE") items.push(`Replace ${cmp.toLowerCase()}`);
    else if (action === "REPAIR") items.push(`Repair ${cmp.toLowerCase()}`);
    else if (action === "REPAINT") items.push(`Repaint ${cmp.toLowerCase()}`);
    if (hidden.risk_level === "high" || hidden.risk_level === "critical") {
      items.push("Inspect internal frame");
    }
    if (fusion.class_distribution && Object.keys(fusion.class_distribution).length > 1) {
      items.push("Address secondary damage areas");
    }
    repEl.innerHTML = items.map(t => `<li>${t}</li>`).join("");
  }

  const partsEl = $('rbParts');
  if (partsEl) {
    partsEl.innerHTML = `<li>${cmp}</li>`;
    if (hidden.risk_level === "high" || hidden.risk_level === "critical") {
      partsEl.innerHTML += `<li>Adjacent mounting hardware</li>`;
    }
  }

  const cost_min = cost.cost_min ?? 0;
  const cost_max = cost.cost_max ?? 0;
  const partsMin = Math.round(cost_min * 0.60);
  const partsMax = Math.round(cost_max * 0.60);
  const laborMin = Math.round(cost_min * 0.30);
  const laborMax = Math.round(cost_max * 0.30);

  if ($('rbLabor'))      $('rbLabor').textContent      = `₹${laborMin.toLocaleString()} – ₹${laborMax.toLocaleString()}`;
  if ($('rbPartsPrice')) $('rbPartsPrice').textContent = `₹${partsMin.toLocaleString()} – ₹${partsMax.toLocaleString()}`;

  renderHeatmap(data.vehicle_type || $('vehicleType')?.value || "car_sedan");
  loadShopsFromSensors();
  loadHistory();

  results.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/* ============================================================
   LIGHTBOX
   ============================================================ */
const lightbox = $('lightbox');
const lightboxImg = $('lightboxImg');
const lightboxClose = $('lightboxClose');

function openLightbox(src, alt) {
  if (!lightbox || !lightboxImg) return;
  lightboxImg.src = src;
  lightboxImg.alt = alt || 'preview';
  lightbox.classList.remove('hidden');
}
function closeLightbox() { if (lightbox) lightbox.classList.add('hidden'); }
if (lightboxClose) lightboxClose.addEventListener('click', closeLightbox);
if (lightbox) lightbox.addEventListener('click', (e) => { if (e.target === lightbox) closeLightbox(); });
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeLightbox(); });

/* ============================================================
   RESET
   ============================================================ */
function resetInspection() {
  VIEW_KEYS.forEach(clearFile);
  if ($('impact'))   $('impact').value = 3.5;
  if ($('rotation')) $('rotation').value = 45;
  if ($('lat'))      $('lat').value = 19.0760;
  if ($('lon'))      $('lon').value = 72.8770;
  const results = $('results');
  if (results) results.classList.add('hidden');
  const status = $('status');
  if (status) status.textContent = 'Ready to analyze.';
  resetSteps();
  state.lastReport = null;
  state.videoFile = null;
  const vt = $('vehicleType');
  renderHeatmap(vt ? vt.value : 'car_sedan');
  toast('Inspection reset.', 'info');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}
const resetBtn = $('resetBtn');
if (resetBtn) resetBtn.addEventListener('click', resetInspection);

/* ============================================================
   REPORT
   ============================================================ */
async function downloadPDF() {
  if (!state.lastReport) { toast('Run an analysis first.', 'error'); return; }
  const btn = $('reportBtn');
  if (btn) btn.disabled = true;
  try {
    const res = await fetch(`${API}/api/report/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeader() },
      body: JSON.stringify(state.lastReport),
    });
    if (!res.ok) throw new Error(`Server ${res.status}`);
    const data = await res.json();
    if (data.pdf_report) {
      window.open(`${API}/api/report/download?path=${encodeURIComponent(data.pdf_report)}`, '_blank');
      toast('PDF report opened.', 'success');
    } else {
      toast('PDF path missing in response.', 'error');
    }
  } catch (err) {
    toast(`PDF generation failed: ${err.message}`, 'error');
  } finally {
    if (btn) btn.disabled = false;
  }
}
const reportBtn = $('reportBtn');
if (reportBtn) reportBtn.addEventListener('click', downloadPDF);

function downloadJSON() {
  if (!state.lastReport) { toast('Run an analysis first.', 'error'); return; }
  const blob = new Blob([JSON.stringify(state.lastReport, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `vehicle_assessment_${Date.now()}.json`;
  a.click();
  URL.revokeObjectURL(url);
  toast('JSON downloaded.', 'success');
}
const jsonBtn = $('jsonBtn');
if (jsonBtn) jsonBtn.addEventListener('click', downloadJSON);

const printBtn = $('printBtn');
if (printBtn) printBtn.addEventListener('click', () => window.print());

const generateInsBtn = $('generateInsBtn');
if (generateInsBtn) generateInsBtn.addEventListener('click', downloadPDF);
const downloadInsBtn = $('downloadInsBtn');
if (downloadInsBtn) downloadInsBtn.addEventListener('click', downloadJSON);
const shareInsBtn = $('shareInsBtn');
if (shareInsBtn) shareInsBtn.addEventListener('click', async () => {
  const url = location.href;
  if (navigator.share) {
    try { await navigator.share({ title: 'Vehicle Damage Report', url }); }
    catch { /* cancelled */ }
  } else {
    try { await navigator.clipboard.writeText(url); toast('Link copied.', 'success'); }
    catch { toast('Unable to share.', 'error'); }
  }
});

/* ============================================================
   HISTORY FROM DATABASE
   ============================================================ */
async function loadHistory() {
  try {
    const res = await fetch(`${API}/api/history/?limit=20`, { headers: authHeader() });
    if (!res.ok) return;
    const rows = await res.json();
    const tbody = $('historyBody');
    if (!tbody) return;
    tbody.innerHTML = "";
    if (!rows.length) {
      tbody.innerHTML = '<tr><td colspan="9" style="text-align:center;color:var(--muted);padding:20px;">No inspections yet</td></tr>';
      return;
    }
    rows.forEach(r => {
      const tr = document.createElement('tr');
      const sevClass = (r.severity_label || '').toLowerCase();
      tr.innerHTML = `
        <td>${r.inspection_id}</td>
        <td>${new Date(r.created_at).toLocaleDateString()}</td>
        <td>${(r.vehicle_type || '').replace(/_/g, ' ')}</td>
        <td>${(r.dominant_damage || '').replace(/_/g, ' ')}</td>
        <td><span class="pill ${sevClass}">${r.severity_label || '—'}</span></td>
        <td>${Math.round((r.hidden_risk || 0) * 100)}%</td>
        <td>₹${(r.cost_min || 0).toLocaleString()}</td>
        <td><span class="pill ok">Completed</span></td>
        <td><button class="link">View</button></td>
      `;
      tbody.appendChild(tr);
    });
  } catch (e) {
    console.warn("History load failed:", e);
  }
}

/* ============================================================
   HISTORY FILTERS
   ============================================================ */
const histSearch = $('histSearch');
const histFilter = $('histFilter');
const historyBody = $('historyBody');

function filterHistory() {
  if (!historyBody) return;
  const q = (histSearch?.value || '').toLowerCase().trim();
  const sev = (histFilter?.value || '').toLowerCase();
  Array.from(historyBody.children).forEach(row => {
    const text = row.textContent.toLowerCase();
    const rowSevMatch = row.querySelector('.pill');
    const rowSev = rowSevMatch ? rowSevMatch.className.replace('pill', '').trim() : '';
    const matchQ = !q || text.includes(q);
    const matchSev = !sev || rowSev === sev;
    row.style.display = (matchQ && matchSev) ? '' : 'none';
  });
}
if (histSearch) histSearch.addEventListener('input', filterHistory);
if (histFilter) histFilter.addEventListener('change', filterHistory);

$$('#historyTable th[data-sort]').forEach(th => {
  th.addEventListener('click', () => {
    if (!historyBody) return;
    const rows = Array.from(historyBody.children);
    const dir = th.dataset.dir === 'asc' ? 'desc' : 'asc';
    th.dataset.dir = dir;
    const idx = Array.from(th.parentNode.children).indexOf(th);
    rows.sort((a, b) => {
      const av = a.children[idx].textContent.trim();
      const bv = b.children[idx].textContent.trim();
      const an = parseFloat(av.replace(/[^\d.]/g, ''));
      const bn = parseFloat(bv.replace(/[^\d.]/g, ''));
      if (!isNaN(an) && !isNaN(bn)) return dir === 'asc' ? an - bn : bn - an;
      return dir === 'asc' ? av.localeCompare(bv) : bv.localeCompare(av);
    });
    rows.forEach(r => historyBody.appendChild(r));
  });
});

/* ============================================================
   PRICING TOGGLE
   ============================================================ */
const billBtns = $$('.bill-btn');
billBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    billBtns.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    const mode = btn.dataset.bill;
    $$('.price-card .amount').forEach(el => {
      const val = el.dataset[mode];
      if (val) el.textContent = val;
    });
  });
});

/* ============================================================
   TIMELINE HOVER
   ============================================================ */
$$('.tl-step').forEach(step => {
  step.addEventListener('mouseenter', () => {
    const info = $('timelineInfo');
    if (info) info.textContent = step.dataset.info || '';
  });
});

/* ============================================================
   BACK TO TOP
   ============================================================ */
const backTop = $('backToTop');
if (backTop) {
  window.addEventListener('scroll', () => {
    backTop.classList.toggle('visible', window.scrollY > 400);
  });
  backTop.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
}

/* ============================================================
   NEWSLETTER
   ============================================================ */
const newsForm = $('newsletterForm');
if (newsForm) {
  newsForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const email = $('newsletterEmail').value.trim();
    if (!email || !email.includes('@')) { toast('Enter a valid email.', 'error'); return; }
    toast('Subscribed. Watch your inbox.', 'success');
    $('newsletterEmail').value = '';
  });
}

/* ============================================================
   SMOOTH SCROLL
   ============================================================ */
document.addEventListener('click', (e) => {
  const a = e.target.closest('a[href^="#"]');
  if (!a) return;
  const id = a.getAttribute('href');
  if (!id || id === '#') return;
  const el = document.querySelector(id);
  if (!el) return;
  e.preventDefault();
  const offset = 70;
  const top = el.getBoundingClientRect().top + window.scrollY - offset;
  window.scrollTo({ top, behavior: 'smooth' });
});

/* ============================================================
   NEARBY REPAIR SHOPS (BACKEND API)
   ============================================================ */
function setShopsMessage(text, isError = false) {
  const list = $("shopsList");
  if (!list) return;
  list.innerHTML = `<p class="muted" style="${isError ? "color:#ef4444" : ""}">${text}</p>`;
  const status = $("shopsStatus");
  if (status) status.textContent = isError ? "Unavailable" : "Ready";
}

function escapeHtml(str) {
  return String(str).replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

function buildShopCard(shop, userLat, userLon) {
  const distance = shop.distance_km;
  const card = document.createElement("div");
  card.className = "shop-card";
  card.innerHTML = `
    <div class="shop-head">
      <div class="shop-name">${escapeHtml(shop.name)}</div>
      <span class="shop-distance">${distance} km</span>
    </div>
    <div class="shop-address">${escapeHtml(shop.address)}</div>
    <div class="shop-meta">
      ${shop.opening_hours ? `<span class="shop-tag">${escapeHtml(shop.opening_hours)}</span>` : ""}
      ${shop.phone ? `<span>${escapeHtml(shop.phone)}</span>` : ""}
    </div>
    <div class="shop-actions">
      <a href="https://www.openstreetmap.org/?mlat=${shop.lat}&mlon=${shop.lon}#map=17/${shop.lat}/${shop.lon}" target="_blank" rel="noopener">View Map</a>
      <a href="https://www.google.com/maps/dir/?api=1&destination=${shop.lat},${shop.lon}" target="_blank" rel="noopener">Directions</a>
      ${shop.website ? `<a href="${escapeHtml(shop.website)}" target="_blank" rel="noopener">Website</a>` : ""}
    </div>
  `;
  return card;
}

async function loadNearbyShops(lat, lon, vehicleType) {
  setShopsMessage("Searching nearby repair shops…");
  try {
    const params = new URLSearchParams({ lat, lon, vehicle_type: vehicleType || "car_sedan" });
    const res = await fetch(`${API}/api/shop/nearby?${params}`);
    if (!res.ok) throw new Error("Server error");
    const data = await res.json();
    if (!data.shops || !data.shops.length) {
      setShopsMessage("No repair shops found within 15 km.", true);
      return;
    }
    const list = $("shopsList");
    list.innerHTML = "";
    data.shops.forEach(s => list.appendChild(buildShopCard(s, lat, lon)));
    const status = $("shopsStatus");
    if (status) status.textContent = `${data.count} shops found`;
  } catch (err) {
    console.error(err);
    setShopsMessage("Could not load nearby shops.", true);
  }
}

function loadShopsFromSensors() {
  const lat = parseFloat($("lat")?.value) || 19.076;
  const lon = parseFloat($("lon")?.value) || 72.877;
  const vt = $("vehicleType")?.value || "car_sedan";
  loadNearbyShops(lat, lon, vt);
}

/* ============================================================
   AUTHENTICATION
   ============================================================ */
function authHeader() {
  const t = localStorage.getItem("vda_token");
  return t ? { "Authorization": `Bearer ${t}` } : {};
}

function updateUserUI() {
  const username = localStorage.getItem("vda_user");
  const nameEl = $("userName");
  const roleEl = $("userRole");
  const avatarEl = $("userAvatar");
  const loginItem = $("loginMenuItem");
  const logoutItem = $("logoutMenuItem");

  if (username) {
    if (nameEl) nameEl.textContent = username;
    if (roleEl) roleEl.textContent = "Inspector";
    if (avatarEl) avatarEl.textContent = username.substring(0, 2).toUpperCase();
    if (loginItem) loginItem.style.display = "none";
    if (logoutItem) logoutItem.style.display = "";
  } else {
    if (nameEl) nameEl.textContent = "Guest";
    if (roleEl) roleEl.textContent = "Not signed in";
    if (avatarEl) avatarEl.textContent = "?";
    if (loginItem) loginItem.style.display = "";
    if (logoutItem) logoutItem.style.display = "none";
  }
}

const authModal = $("authModal");
let authMode = "login";

function openAuthModal(mode = "login") {
  authMode = mode;
  const title = $("authTitle");
  const toggle = $("authToggleBtn");
  const submit = $("authSubmitBtn");
  if (title) title.textContent = mode === "login" ? "Sign In" : "Create Account";
  if (toggle) toggle.textContent = mode === "login" ? "Switch to Register" : "Switch to Sign In";
  if (submit) submit.textContent = mode === "login" ? "Sign In" : "Register";
  if (authModal) authModal.classList.remove("hidden");
}

function closeAuthModal() {
  if (authModal) authModal.classList.add("hidden");
}

const closeAuthBtn = $("closeAuthBtn");
if (closeAuthBtn) closeAuthBtn.addEventListener("click", closeAuthModal);

const authToggleBtn = $("authToggleBtn");
if (authToggleBtn) authToggleBtn.addEventListener("click", () => {
  openAuthModal(authMode === "login" ? "register" : "login");
});

const authSubmitBtn = $("authSubmitBtn");
if (authSubmitBtn) authSubmitBtn.addEventListener("click", async () => {
  const username = $("authUsername")?.value?.trim();
  const password = $("authPassword")?.value;
  if (!username || !password) { toast("Enter username and password", "error"); return; }

  const url = authMode === "login" ? "/api/auth/login" : "/api/auth/register";
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    const data = await res.json();
    if (!res.ok) { toast(data.error || "Auth failed", "error"); return; }
    if (authMode === "login") {
      localStorage.setItem("vda_token", data.token);
      localStorage.setItem("vda_user", data.username);
      updateUserUI();
      toast(`Welcome, ${data.username}!`, "success");
      closeAuthModal();
    } else {
      toast("Account created. Please sign in.", "success");
      openAuthModal("login");
    }
  } catch (e) {
    toast(`Auth error: ${e.message}`, "error");
  }
});

const loginMenuItem = $("loginMenuItem");
if (loginMenuItem) loginMenuItem.addEventListener("click", (e) => { e.preventDefault(); openAuthModal("login"); });

const logoutMenuItem = $("logoutMenuItem");
if (logoutMenuItem) logoutMenuItem.addEventListener("click", (e) => {
  e.preventDefault();
  localStorage.removeItem("vda_token");
  localStorage.removeItem("vda_user");
  updateUserUI();
  toast("Signed out.", "info");
});

/* ============================================================
   SOCKET.IO
   ============================================================ */
try {
  if (typeof io === 'function') {
    const socket = io();
    window._socket = socket;

    socket.on("connect", () => console.log("[SocketIO] connected"));
    socket.on("disconnect", () => console.log("[SocketIO] disconnected"));
    socket.on("impact_alert", (data) => {
      toast(data.message || "Impact detected", "error", 5000);
      const iot = $("iot");
      if (iot) {
        iot.classList.add("flash-alert");
        setTimeout(() => iot.classList.remove("flash-alert"), 1500);
      }
    });
    socket.on("sensor_error", (data) => toast(`Sensor error: ${data.error}`, "error"));
  }
} catch (e) {
  console.warn("SocketIO not available", e);
}

/* ============================================================
   ANALYZE BUTTON + INIT
   ============================================================ */
const analyzeBtn = $('analyzeBtn');
if (analyzeBtn) analyzeBtn.addEventListener('click', analyze);

if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js').catch(() => {});
}

document.addEventListener('DOMContentLoaded', () => {
  updateUploadProgress();

  const vt = $('vehicleType');
  renderHeatmap(vt ? vt.value : 'car_sedan');
  if (vt) vt.addEventListener('change', () => renderHeatmap(vt.value));

  updateUserUI();
  loadHistory();

  const detectBtn = $('detectLocationBtn');
  if (detectBtn) detectBtn.addEventListener('click', detectMyLocation);
  const clearBtn = $('clearLocationBtn');
  if (clearBtn) clearBtn.addEventListener('click', clearLocation);

  const latVal = parseFloat($('lat')?.value);
  const lonVal = parseFloat($('lon')?.value);
  const isDefault = Math.abs(latVal - 19.0760) < 0.001 && Math.abs(lonVal - 72.8770) < 0.001;
  if (isDefault && !sessionStorage.getItem('vda_geo_tried')) {
    sessionStorage.setItem('vda_geo_tried', '1');
    setTimeout(() => detectMyLocation(), 1500);
  }

  setTimeout(() => {
    $$('.confidence-ring').forEach(ring => {
      const val = parseFloat(ring.dataset.value) || 0;
      const circle = ring.querySelector('.ring');
      if (!circle) return;
      const dash = 264;
      const offset = dash - (val / 100) * dash;
      circle.style.strokeDashoffset = String(offset);
    });
  }, 400);
});