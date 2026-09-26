/**
 * Contact Book — script.js
 * iOS-style glass UI interactions
 */
"use strict";

// ── REFS ──────────────────────────────────────
const overlay        = document.getElementById("overlay");
const contactModal   = document.getElementById("contactModal");
const deleteModal    = document.getElementById("deleteModal");
const modalTitle     = document.getElementById("modalTitle");
const contactForm    = document.getElementById("contactForm");
const formErrors     = document.getElementById("formErrors");
const editIdInput    = document.getElementById("editId");
const submitBtn      = document.getElementById("submitBtn");
const submitLabel    = document.getElementById("submitLabel");
const submitSpinner  = document.getElementById("submitSpinner");
const cancelBtn      = document.getElementById("cancelBtn");
const modalClose     = document.getElementById("modalClose");

const searchInput    = document.getElementById("searchInput");
const clearSearch    = document.getElementById("clearSearch");

const contactGrid    = document.getElementById("contactGrid");
const contactCount   = document.getElementById("contactCount");
const contactsHdg    = document.getElementById("contactsHeading");

const statTotal      = document.getElementById("statTotal");
const statFav        = document.getElementById("statFav");

// Theme
const themeToggle    = document.getElementById("themeToggle");
const iconMoon       = document.getElementById("iconMoon");
const iconSun        = document.getElementById("iconSun");
const bnavThemeBtn   = document.getElementById("bnavTheme");
const bnavThemeIcon  = document.getElementById("bnavThemeIcon");

// Header / bottom nav
const navHome        = document.getElementById("navHome");
const navFavs        = document.getElementById("navFavs");
const bnavHome       = document.getElementById("bnavHome");
const bnavSearch     = document.getElementById("bnavSearch");
const bnavAdd        = document.getElementById("bnavAdd");
const bnavFavsBtn    = document.getElementById("bnavFavs");

// Delete state
let pendingDelId   = null;
let pendingDelName = null;

// Search debounce
let searchTimer = null;

// Current filter view: 'home' | 'favs'
let currentView = 'home';

// ── TOAST ────────────────────────────────────
let toastTimer = null;
function showToast(msg, type = "success") {
  const el = document.getElementById("toast");
  el.textContent = msg;
  el.className   = `toast ${type} show`;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { el.className = "toast"; }, 3200);
}

// ── THEME ────────────────────────────────────
function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem("cb_theme", theme);

  const isDark = theme === "dark";

  // Header toggle icons
  iconMoon.style.display = isDark ? "block" : "none";
  iconSun.style.display  = isDark ? "none"  : "block";

  // Bottom nav theme icon
  if (bnavThemeIcon) {
    bnavThemeIcon.innerHTML = isDark
      ? `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>`
      : `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>`;
  }
}

// Initialise
(function () {
  const saved = localStorage.getItem("cb_theme") || "dark";
  applyTheme(saved);
})();

function toggleTheme() {
  const cur = document.documentElement.getAttribute("data-theme");
  const next = cur === "dark" ? "light" : "dark";
  applyTheme(next);
  showToast(next === "dark" ? "Dark mode on" : "Light mode on");
}

themeToggle.addEventListener("click", toggleTheme);
if (bnavThemeBtn) bnavThemeBtn.addEventListener("click", toggleTheme);

// ── MODAL HELPERS ─────────────────────────────
function openModal(modal) {
  overlay.classList.add("active");
  modal.classList.add("open");
  modal.setAttribute("aria-hidden", "false");
  document.body.style.overflow = "hidden";
  const first = modal.querySelector("input, button");
  if (first) setTimeout(() => first.focus(), 80);
}
function closeModal(modal) {
  overlay.classList.remove("active");
  modal.classList.remove("open");
  modal.setAttribute("aria-hidden", "true");
  document.body.style.overflow = "";
}
function closeAll() {
  closeModal(contactModal);
  closeModal(deleteModal);
}

overlay.addEventListener("click", closeAll);
document.addEventListener("keydown", e => { if (e.key === "Escape") closeAll(); });

// ── ADD MODAL ────────────────────────────────
function openAddModal() {
  modalTitle.textContent  = "Add Contact";
  submitLabel.textContent = "Save Contact";
  contactForm.reset();
  editIdInput.value = "";
  clearErrors();
  openModal(contactModal);
}

cancelBtn.addEventListener("click",  () => closeModal(contactModal));
modalClose.addEventListener("click", () => closeModal(contactModal));

// Desktop header
document.getElementById("openAddModal")?.addEventListener("click", openAddModal);
// Mobile bottom nav center button
if (bnavAdd) bnavAdd.addEventListener("click", openAddModal);

// Empty state button (may not exist on initial load if contacts exist)
document.getElementById("openAddModalEmpty")?.addEventListener("click", openAddModal);

// ── FORM ERRORS ──────────────────────────────
function clearErrors() {
  formErrors.style.display = "none";
  formErrors.innerHTML = "";
  document.querySelectorAll(".f-input.error").forEach(el => el.classList.remove("error"));
}
function showErrors(errors) {
  formErrors.innerHTML = errors.map(e => `<span>• ${e}</span>`).join("");
  formErrors.style.display = "flex";
}

// ── SUBMIT ───────────────────────────────────
contactForm.addEventListener("submit", async e => {
  e.preventDefault();
  clearErrors();

  const id  = editIdInput.value;
  const url = id ? `/edit/${id}` : "/add";
  const fd  = new FormData(contactForm);

  submitBtn.disabled         = true;
  submitLabel.style.display  = "none";
  submitSpinner.style.display = "inline-block";

  try {
    const res  = await fetch(url, { method: "POST", body: fd });
    const json = await res.json();
    if (json.success) {
      closeModal(contactModal);
      showToast(json.message || "Saved!", "success");
      await refreshAll();
    } else {
      showErrors(json.errors || ["Something went wrong."]);
    }
  } catch {
    showErrors(["Network error — please try again."]);
  } finally {
    submitBtn.disabled          = false;
    submitLabel.style.display   = "inline";
    submitSpinner.style.display = "none";
  }
});

// ── EDIT ─────────────────────────────────────
async function openEditModal(id) {
  clearErrors();
  try {
    const res = await fetch(`/edit/${id}`);
    if (!res.ok) { showToast("Contact not found.", "error"); return; }
    const c = await res.json();

    modalTitle.textContent  = "Edit Contact";
    submitLabel.textContent = "Save Changes";
    editIdInput.value = c.id;

    document.getElementById("fieldName").value    = c.name    || "";
    document.getElementById("fieldPhone").value   = c.phone   || "";
    document.getElementById("fieldEmail").value   = c.email   || "";
    document.getElementById("fieldAddress").value = c.address || "";
    document.getElementById("fieldCompany").value = c.company || "";
    document.getElementById("fieldNotes").value   = c.notes   || "";

    openModal(contactModal);
  } catch {
    showToast("Failed to load contact.", "error");
  }
}

// ── DELETE ───────────────────────────────────
function openDeleteModal(id, name) {
  pendingDelId   = id;
  pendingDelName = name;
  document.getElementById("deleteDesc").textContent =
    `"${name}" will be permanently removed. This cannot be undone.`;
  openModal(deleteModal);
}

document.getElementById("cancelDelete")?.addEventListener("click", () => closeModal(deleteModal));

document.getElementById("confirmDelete")?.addEventListener("click", async () => {
  if (!pendingDelId) return;
  const id   = pendingDelId;
  const name = pendingDelName;
  closeModal(deleteModal);

  try {
    const res  = await fetch(`/delete/${id}`, { method: "POST" });
    const json = await res.json();
    if (json.success) {
      const card = document.getElementById(`card-${id}`);
      if (card) {
        card.style.transition = "opacity .22s, transform .22s";
        card.style.opacity    = "0";
        card.style.transform  = "scale(.94) translateY(8px)";
        setTimeout(() => card.remove(), 240);
      }
      showToast(`"${name}" deleted.`, "success");
      await refreshAll();
    } else {
      showToast(json.errors?.[0] || "Delete failed.", "error");
    }
  } catch {
    showToast("Network error.", "error");
  }

  pendingDelId   = null;
  pendingDelName = null;
});

// ── FAVOURITE ────────────────────────────────
async function toggleFav(id, btn) {
  try {
    const res  = await fetch(`/toggle_favorite/${id}`, { method: "POST" });
    const json = await res.json();
    if (!json.success) return;

    const star = btn.querySelector("svg");
    if (json.favorite) {
      btn.classList.add("is-fav");
      star.setAttribute("fill", "currentColor");
      btn.setAttribute("aria-label", "Remove from favourites");
    } else {
      btn.classList.remove("is-fav");
      star.setAttribute("fill", "none");
      btn.setAttribute("aria-label", "Add to favourites");
    }
    // Refresh stats
    await refreshStats();
  } catch {
    showToast("Failed to update.", "error");
  }
}

// ── EVENT DELEGATION (grid) ──────────────────
contactGrid.addEventListener("click", e => {
  const editBtn = e.target.closest(".act-btn--edit");
  const delBtn  = e.target.closest(".act-btn--del");
  const favBtn  = e.target.closest(".fav-btn");

  if (editBtn) openEditModal(editBtn.dataset.id);
  if (delBtn)  openDeleteModal(delBtn.dataset.id, delBtn.dataset.name);
  if (favBtn)  toggleFav(favBtn.dataset.id, favBtn);
});

// ── SEARCH ───────────────────────────────────
searchInput.addEventListener("input", () => {
  const q = searchInput.value.trim();
  clearSearch.style.display = q ? "flex" : "none";
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => performSearch(q), 260);
});

clearSearch.addEventListener("click", () => {
  searchInput.value         = "";
  clearSearch.style.display = "none";
  performSearch("");
  searchInput.focus();
});

async function performSearch(q) {
  try {
    const favOnly = currentView === "favs";
    let url = q ? `/contacts/json?q=${encodeURIComponent(q)}` : "/contacts/json";
    const res   = await fetch(url);
    let data    = await res.json();
    if (favOnly) data = data.filter(c => c.favorite);
    renderGrid(data, q);
  } catch {
    showToast("Search error.", "error");
  }
}

// ── NAVIGATION ───────────────────────────────
function setView(view) {
  currentView = view;

  // Header nav
  navHome?.classList.toggle("active", view === "home");
  navFavs?.classList.toggle("active", view === "favs");

  // Bottom nav
  bnavHome?.classList.toggle("active",    view === "home");
  bnavFavsBtn?.classList.toggle("active", view === "favs");

  // ARIA
  navHome?.setAttribute("aria-current",     view === "home" ? "page" : "false");
  navFavs?.setAttribute("aria-current",     view === "favs" ? "page" : "false");
  bnavHome?.setAttribute("aria-current",    view === "home" ? "page" : "false");
  bnavFavsBtn?.setAttribute("aria-current", view === "favs" ? "page" : "false");

  performSearch(searchInput.value.trim());
}

navHome?.addEventListener("click",    () => setView("home"));
navFavs?.addEventListener("click",   () => setView("favs"));
bnavHome?.addEventListener("click",  () => setView("home"));
bnavFavsBtn?.addEventListener("click", () => setView("favs"));

// Bottom nav — search: scroll to search input & focus
bnavSearch?.addEventListener("click", () => {
  searchInput.scrollIntoView({ behavior: "smooth", block: "center" });
  setTimeout(() => searchInput.focus(), 350);
});

// ── RENDER GRID ──────────────────────────────
function renderGrid(contacts, q = "") {
  const n = contacts.length;
  contactCount.textContent = n;
  contactsHdg.textContent  = currentView === "favs"
    ? "Favourites"
    : q ? `Results for "${q}"` : "All Contacts";

  if (!n) {
    const isFavView = currentView === "favs";
    contactGrid.innerHTML = `
      <div class="empty-view" id="emptyState">
        <div class="empty-orb">
          <svg width="52" height="52" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>
          </svg>
        </div>
        ${isFavView
          ? `<h3 class="empty-h">No favourites yet</h3>
             <p class="empty-p">Tap the star on a contact to add it here.</p>`
          : q
            ? `<h3 class="empty-h">No contacts found</h3>
               <p class="empty-p">Nothing matched "<strong>${esc(q)}</strong>".</p>`
            : `<h3 class="empty-h">No contacts yet</h3>
               <p class="empty-p">Add your first contact to get started.</p>
               <button class="pill-btn" id="openAddModalEmpty">
                 <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
                   <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
                 </svg>
                 Add Contact
               </button>`
        }
      </div>`;
    document.getElementById("openAddModalEmpty")?.addEventListener("click", openAddModal);
    return;
  }

  contactGrid.innerHTML = contacts.map(buildCard).join("");
}

function buildCard(c) {
  const init    = (c.name || "?")[0].toUpperCase();
  const isFav   = !!c.favorite;
  const fill    = isFav ? "currentColor" : "none";
  const favCls  = isFav ? "fav-btn is-fav" : "fav-btn";
  const favLbl  = isFav ? "Remove from favourites" : "Add to favourites";

  return `
<article class="c-card" id="card-${c.id}" data-id="${c.id}">
  <div class="c-card__top">
    <div class="c-avatar">${esc(init)}</div>
    <div class="c-meta">
      <h3 class="c-name">${esc(c.name)}</h3>
      ${c.company ? `<span class="c-company">${esc(c.company)}</span>` : ""}
    </div>
    <button class="${favCls}" data-id="${c.id}" aria-label="${favLbl}">
      <svg width="17" height="17" viewBox="0 0 24 24" fill="${fill}" stroke="currentColor" stroke-width="2" stroke-linecap="round">
        <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
      </svg>
    </button>
  </div>
  <div class="c-card__body">
    <div class="c-row">
      <span class="c-row__icon">${phoneIcon()}</span>
      <span class="c-row__val">${esc(c.phone)}</span>
    </div>
    ${c.email ? `<div class="c-row"><span class="c-row__icon">${emailIcon()}</span><span class="c-row__val c-clamp">${esc(c.email)}</span></div>` : ""}
    ${c.address ? `<div class="c-row"><span class="c-row__icon">${pinIcon()}</span><span class="c-row__val c-clamp">${esc(c.address)}</span></div>` : ""}
    ${c.notes ? `<div class="c-row c-row--note"><span class="c-row__icon">${noteIcon()}</span><span class="c-row__val c-clamp">${esc(c.notes)}</span></div>` : ""}
  </div>
  <div class="c-card__actions">
    <button class="act-btn act-btn--edit" data-id="${c.id}" aria-label="Edit ${esc(c.name)}">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round">
        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
      </svg>
      Edit
    </button>
    <button class="act-btn act-btn--del" data-id="${c.id}" data-name="${escAttr(c.name)}" aria-label="Delete ${esc(c.name)}">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round">
        <polyline points="3 6 5 6 21 6"/>
        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/>
      </svg>
      Delete
    </button>
  </div>
</article>`;
}

// ── REFRESH ──────────────────────────────────
async function refreshAll() {
  await Promise.all([refreshGrid(), refreshStats()]);
}

async function refreshGrid() {
  const q = searchInput.value.trim();
  let url = q ? `/contacts/json?q=${encodeURIComponent(q)}` : "/contacts/json";
  try {
    const res  = await fetch(url);
    let data   = await res.json();
    if (currentView === "favs") data = data.filter(c => c.favorite);
    renderGrid(data, q);
  } catch {}
}

async function refreshStats() {
  try {
    const res   = await fetch("/contacts/json");
    const all   = await res.json();
    statTotal.textContent = all.length;
    statFav.textContent   = all.filter(c => c.favorite).length;
  } catch {}
}

// ── SVG ICONS ────────────────────────────────
const phoneIcon = () => `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 12 19.79 19.79 0 0 1 1.61 3.41 2 2 0 0 1 3.6 1.23h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L7.91 8.85a16 16 0 0 0 6 6l.91-.91a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 21.73 16z"/></svg>`;
const emailIcon = () => `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>`;
const pinIcon   = () => `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>`;
const noteIcon  = () => `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>`;

// ── ESCAPE HELPERS ───────────────────────────
function esc(s) {
  if (!s) return "";
  return String(s)
    .replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;")
    .replace(/"/g,"&quot;").replace(/'/g,"&#39;");
}
function escAttr(s) { return esc(s); }
