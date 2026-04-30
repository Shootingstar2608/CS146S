/* ── Helpers ──────────────────────────────────────── */
async function fetchJSON(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(await res.text());
  if (res.status === 204) return null;
  return res.json();
}

function toast(msg, type = 'success') {
  const c = document.getElementById('toasts');
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.textContent = msg;
  c.appendChild(el);
  setTimeout(() => el.remove(), 3200);
}

/* ── Notes ────────────────────────────────────────── */
let notesCache = [];

async function loadNotes(query) {
  const url = query ? `/notes/search/?q=${encodeURIComponent(query)}` : '/notes/';
  notesCache = await fetchJSON(url);
  renderNotes();
}

function renderNotes() {
  const list = document.getElementById('notes');
  list.innerHTML = '';
  if (!notesCache.length) {
    list.innerHTML = '<li class="empty-state">No notes yet — add one above!</li>';
    return;
  }
  for (const n of notesCache) {
    const li = document.createElement('li');
    li.dataset.id = n.id;
    li.innerHTML = `
      <div class="item-text">
        <div class="item-title">${esc(n.title)}</div>
        <div class="item-content">${esc(n.content)}</div>
      </div>
      <div class="item-actions">
        <button class="btn-ghost btn-sm" onclick="openEdit(${n.id})">✏️</button>
        <button class="btn-danger btn-sm" onclick="deleteNote(${n.id})">🗑</button>
      </div>`;
    list.appendChild(li);
  }
}

function esc(s) {
  const d = document.createElement('div');
  d.textContent = s;
  return d.innerHTML;
}

async function deleteNote(id) {
  const prev = [...notesCache];
  notesCache = notesCache.filter(n => n.id !== id);
  renderNotes();
  try {
    await fetchJSON(`/notes/${id}`, { method: 'DELETE' });
    toast('Note deleted');
  } catch {
    notesCache = prev;
    renderNotes();
    toast('Failed to delete', 'error');
  }
}

function openEdit(id) {
  const note = notesCache.find(n => n.id === id);
  if (!note) return;
  document.getElementById('edit-id').value = id;
  document.getElementById('edit-title').value = note.title;
  document.getElementById('edit-content').value = note.content;
  document.getElementById('edit-modal').classList.add('active');
}

/* ── Action Items ────────────────────────────────── */
let actionsCache = [];
let currentFilter = 'all';
let selectedIds = new Set();

async function loadActions() {
  let url = '/action-items/';
  if (currentFilter === 'open') url += '?completed=false';
  else if (currentFilter === 'done') url += '?completed=true';
  actionsCache = await fetchJSON(url);
  selectedIds.clear();
  renderActions();
}

function renderActions() {
  const list = document.getElementById('actions');
  list.innerHTML = '';
  updateBulkBar();
  if (!actionsCache.length) {
    list.innerHTML = '<li class="empty-state">No action items here.</li>';
    return;
  }
  for (const a of actionsCache) {
    const li = document.createElement('li');
    if (a.completed) li.classList.add('completed');
    li.dataset.id = a.id;
    const chk = a.completed ? '✓' : '';
    li.innerHTML = `
      <div class="checkbox ${a.completed ? 'checked' : ''}" onclick="toggleSelect(${a.id}, this)">${chk}</div>
      <div class="item-text">${esc(a.description)}</div>`;
    if (!a.completed) {
      li.innerHTML += `<div class="item-actions">
        <button class="btn-success btn-sm" onclick="completeOne(${a.id})">✓</button>
      </div>`;
    }
    list.appendChild(li);
  }
}

function toggleSelect(id, el) {
  const item = actionsCache.find(a => a.id === id);
  if (item && item.completed) return;
  if (selectedIds.has(id)) { selectedIds.delete(id); el.classList.remove('checked'); el.textContent = ''; }
  else { selectedIds.add(id); el.classList.add('checked'); el.textContent = '✓'; }
  updateBulkBar();
}

function updateBulkBar() {
  const bar = document.getElementById('bulk-bar');
  const cnt = document.getElementById('bulk-count');
  if (selectedIds.size > 0) {
    bar.classList.add('visible');
    cnt.textContent = `${selectedIds.size} selected`;
  } else {
    bar.classList.remove('visible');
  }
}

async function completeOne(id) {
  try {
    await fetchJSON(`/action-items/${id}/complete`, { method: 'PUT' });
    toast('Completed!');
    loadActions();
  } catch { toast('Failed', 'error'); }
}

async function bulkComplete() {
  if (!selectedIds.size) return;
  const ids = [...selectedIds];
  try {
    await fetchJSON('/action-items/bulk-complete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ids }),
    });
    toast(`${ids.length} items completed`);
    loadActions();
  } catch { toast('Bulk complete failed', 'error'); }
}

/* ── Init ────────────────────────────────────────── */
window.addEventListener('DOMContentLoaded', () => {
  // Note form
  document.getElementById('note-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const title = document.getElementById('note-title').value;
    const content = document.getElementById('note-content').value;
    const optimistic = { id: Date.now(), title, content };
    notesCache.unshift(optimistic);
    renderNotes();
    try {
      await fetchJSON('/notes/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, content }),
      });
      e.target.reset();
      toast('Note created');
      loadNotes();
    } catch {
      notesCache = notesCache.filter(n => n.id !== optimistic.id);
      renderNotes();
      toast('Failed to create note', 'error');
    }
  });

  // Action form
  document.getElementById('action-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const description = document.getElementById('action-desc').value;
    try {
      await fetchJSON('/action-items/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description }),
      });
      e.target.reset();
      toast('Action item added');
      loadActions();
    } catch { toast('Failed to add action item', 'error'); }
  });

  // Search
  let searchTimer;
  document.getElementById('note-search').addEventListener('input', (e) => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => loadNotes(e.target.value), 300);
  });

  // Filters
  document.querySelectorAll('#action-filters button').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('#action-filters button').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentFilter = btn.dataset.filter;
      loadActions();
    });
  });

  // Bulk complete
  document.getElementById('bulk-complete-btn').addEventListener('click', bulkComplete);

  // Edit modal
  document.getElementById('edit-cancel').addEventListener('click', () => {
    document.getElementById('edit-modal').classList.remove('active');
  });
  document.getElementById('edit-modal').addEventListener('click', (e) => {
    if (e.target === e.currentTarget) e.currentTarget.classList.remove('active');
  });
  document.getElementById('edit-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('edit-id').value;
    const title = document.getElementById('edit-title').value;
    const content = document.getElementById('edit-content').value;
    try {
      await fetchJSON(`/notes/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, content }),
      });
      document.getElementById('edit-modal').classList.remove('active');
      toast('Note updated');
      loadNotes();
    } catch { toast('Failed to update note', 'error'); }
  });

  loadNotes();
  loadActions();
});
