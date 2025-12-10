// Global state
let clients = [];
let filteredClients = [];
let activeBlock = 'ALL';
let searchText = '';
let dateFrom = '';
let dateTo = '';
let editingId = null;

// Generate A-Z blocks
const BLOCKS = Array.from({ length: 26 }, (_, i) => String.fromCharCode(65 + i));

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    initializeUI();
    loadClients();
    attachEventListeners();
});

function initializeUI() {
    // Generate block buttons in sidebar
    const blocksGrid = document.getElementById('blocksGrid');
    if (blocksGrid) {
        blocksGrid.innerHTML = '<button class="block-btn active" data-block="ALL">All</button>';
        BLOCKS.forEach(block => {
            const btn = document.createElement('button');
            btn.className = 'block-btn';
            btn.textContent = block;
            btn.dataset.block = block;
            btn.addEventListener('click', () => selectBlock(block));
            blocksGrid.appendChild(btn);
        });
    }

    // Generate block options in form
    const blockSelect = document.querySelector('select[name="block"]');
    if (blockSelect) {
        blockSelect.innerHTML = '';
        BLOCKS.forEach(block => {
            const option = document.createElement('option');
            option.value = block;
            option.textContent = block;
            blockSelect.appendChild(option);
        });
    }
}

function attachEventListeners() {
    // Menu toggle
    const menuBtn = document.getElementById('menuBtn');
    if (menuBtn) {
        menuBtn.addEventListener('click', () => {
            document.getElementById('sidebar').classList.add('active');
            document.getElementById('sidebarOverlay').classList.add('active');
        });
    }

    const closeBtn = document.getElementById('closeBtn');
    if (closeBtn) {
        closeBtn.addEventListener('click', closeSidebar);
    }

    const sidebarOverlay = document.getElementById('sidebarOverlay');
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', closeSidebar);
    }

    // Blocks toggle
    const blocksToggle = document.getElementById('blocksToggle');
    if (blocksToggle) {
        blocksToggle.addEventListener('click', () => {
            document.getElementById('blocksToggle').classList.toggle('active');
            document.getElementById('blocksGrid').classList.toggle('active');
        });
    }

    // All clients button
    document.querySelectorAll('[data-block="ALL"]').forEach(btn => {
        btn.addEventListener('click', () => selectBlock('ALL'));
    });

    // Search
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            searchText = e.target.value;
            filterAndRender();
        });
    }

    const searchBtn = document.getElementById('searchBtn');
    if (searchBtn) {
        searchBtn.addEventListener('click', () => {
            filterAndRender();
        });
    }

    // Date filters
    const dateFromInput = document.getElementById('dateFrom');
    if (dateFromInput) {
        dateFromInput.addEventListener('change', (e) => {
            dateFrom = e.target.value;
            filterAndRender();
        });
    }

    const dateToInput = document.getElementById('dateTo');
    if (dateToInput) {
        dateToInput.addEventListener('change', (e) => {
            dateTo = e.target.value;
            filterAndRender();
        });
    }

    // Form submit
    const clientForm = document.getElementById('clientForm');
    if (clientForm) {
        clientForm.addEventListener('submit', handleFormSubmit);
    }

    const resetBtn = document.getElementById('resetBtn');
    if (resetBtn) {
        resetBtn.addEventListener('click', resetForm);
    }

    // Export/Import
    const exportBtn = document.getElementById('exportBtn');
    if (exportBtn) {
        exportBtn.addEventListener('click', exportData);
    }

    const importInput = document.getElementById('importInput');
    if (importInput) {
        importInput.addEventListener('change', handleImport);
    }
}

function closeSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    if (sidebar) sidebar.classList.remove('active');
    if (overlay) overlay.classList.remove('active');
}

function selectBlock(block) {
    activeBlock = block;

    // Update active state on buttons
    document.querySelectorAll('.block-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.block === block);
    });

    closeSidebar();
    filterAndRender();
}

// API calls
async function loadClients() {
    try {
        const response = await fetch('/api/clients');
        if (response.status === 401) {
            window.location.href = '/login';
            return;
        }
        clients = await response.json();
        filterAndRender();
    } catch (error) {
        console.error('Error loading clients:', error);
        showError('Failed to load clients');
    }
}

async function handleFormSubmit(e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());

    // Validate
    if (!data.name && !data.plotNo) {
        if (!confirm('No name or plot number provided. Save anyway?')) {
            return;
        }
    }

    try {
        const response = await fetch('/api/clients', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            const newClient = await response.json();
            clients.unshift(newClient);
            filterAndRender();
            resetForm();
            showSuccess('Client saved successfully!');
        } else {
            showError('Failed to save client');
        }
    } catch (error) {
        console.error('Error saving client:', error);
        showError('Failed to save client');
    }
}

// Edit Client
function editClient(id) {
    const client = clients.find(c => c.id === id);
    if (!client) return;

    const card = document.querySelector(`[data-id="${id}"]`);
    if (!card) return;

    // Create edit form HTML
    const editHtml = `
        <div class="edit-form">
            <div class="edit-grid">
                <input type="text" name="name" value="${client.name || ''}" placeholder="Name" class="edit-input">
                <input type="text" name="contact" value="${client.contact || ''}" placeholder="Contact" class="edit-input">
                <input type="text" name="society" value="${client.society || ''}" placeholder="Society" class="edit-input">
                <input type="text" name="plotNo" value="${client.plotNo || ''}" placeholder="Plot No" class="edit-input">
                <select name="block" class="edit-input">
                    ${generateBlockOptions(client.block)}
                </select>
                <input type="text" name="price" value="${client.price || ''}" placeholder="Price" class="edit-input">
                <input type="text" name="size" value="${client.size || ''}" placeholder="Size" class="edit-input">
                <input type="date" name="date" value="${client.date || ''}" class="edit-input">
                <input type="text" name="description" value="${client.description || ''}" placeholder="Description" class="edit-input" style="grid-column: 1 / -1">
            </div>
            <div class="edit-actions">
                <button onclick="saveEdit('${id}')" class="btn-save">Save</button>
                <button onclick="cancelEdit('${id}')" class="btn-cancel">Cancel</button>
            </div>
        </div>
    `;

    // Hide info and show form
    const infoDiv = card.querySelector('.client-info');
    const actionsDiv = card.querySelector('.client-actions');

    if (infoDiv) infoDiv.style.display = 'none';
    if (actionsDiv) actionsDiv.style.display = 'none';

    const formContainer = document.createElement('div');
    formContainer.className = 'edit-container';
    formContainer.innerHTML = editHtml;
    card.appendChild(formContainer);
}

function generateBlockOptions(selectedBlock) {
    return BLOCKS.map(block =>
        `<option value="${block}" ${block === selectedBlock ? 'selected' : ''}>${block}</option>`
    ).join('');
}

function cancelEdit(id) {
    const card = document.querySelector(`[data-id="${id}"]`);
    if (!card) return;

    const formContainer = card.querySelector('.edit-container');
    if (formContainer) formContainer.remove();

    const infoDiv = card.querySelector('.client-info');
    const actionsDiv = card.querySelector('.client-actions');

    if (infoDiv) infoDiv.style.display = 'block';
    if (actionsDiv) actionsDiv.style.display = 'flex';
}

async function saveEdit(id) {
    const card = document.querySelector(`[data-id="${id}"]`);
    if (!card) return;

    const inputs = card.querySelectorAll('.edit-input');
    const data = {};

    inputs.forEach(input => {
        data[input.name] = input.value;
    });

    try {
        const response = await fetch(`/api/clients/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            const updatedClient = await response.json();
            // Update local state
            clients = clients.map(c => c.id === id ? updatedClient : c);
            filterAndRender();
            showSuccess('Client updated successfully!');
        } else {
            showError('Failed to update client');
        }
    } catch (error) {
        console.error('Error updating client:', error);
        showError('Failed to update client');
    }
}

async function deleteClient(id) {
    const result = await Swal.fire({
        title: 'Are you sure?',
        text: "You won't be able to revert this!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#e11d48',
        cancelButtonColor: '#64748b',
        confirmButtonText: 'Yes, delete it!'
    });

    if (!result.isConfirmed) return;

    try {
        const response = await fetch(`/api/clients/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            clients = clients.filter(c => c.id !== id);
            filterAndRender();
            Swal.fire(
                'Deleted!',
                'Client has been deleted.',
                'success'
            );
        } else {
            showError('Failed to delete client');
        }
    } catch (error) {
        console.error('Error deleting client:', error);
        showError('Failed to delete client');
    }
}

function resetForm() {
    const form = document.getElementById('clientForm');
    if (form) form.reset();
}

// Filtering
function filterAndRender() {
    filteredClients = clients.filter(client => {
        // Block filter
        const matchBlock = activeBlock === 'ALL' || client.block === activeBlock;

        // Search filter
        const q = searchText.trim().toLowerCase();
        const matchText = q === '' || Object.values(client).join(' ').toLowerCase().includes(q);

        // Date filter
        const d = client.date || '';
        let matchDate = true;
        if (dateFrom && !dateTo) matchDate = d >= dateFrom;
        if (dateFrom && dateTo) matchDate = d >= dateFrom && d <= dateTo;
        if (!dateFrom && dateTo) matchDate = d <= dateTo;

        return matchBlock && matchText && matchDate;
    });

    renderClients();
}

// Rendering
function renderClients() {
    const container = document.getElementById('clientList');
    const recordCount = document.getElementById('recordCount');

    if (recordCount) recordCount.textContent = filteredClients.length;

    if (!container) return;

    if (filteredClients.length === 0) {
        container.innerHTML = '<div class="no-records">No records found</div>';
        return;
    }

    container.innerHTML = filteredClients.map(client => `
        <div class="client-card" data-id="${client.id}">
            <div class="client-header">
                <div class="client-info">
                    <div class="client-name">${highlightText(client.name || '-', searchText)}</div>
                    <div class="client-details">
                        ${highlightText((client.society || '-') + ' • Plot ' + (client.plotNo || '-') + ' • Block ' + (client.block || '-'), searchText)}
                    </div>
                    <div class="client-meta">
                        Price: <strong>${highlightText(client.price || '-', searchText)}</strong> | 
                        Size: <strong>${highlightText(client.size || '-', searchText)}</strong>
                    </div>
                    ${client.description ? `<div class="client-description">${highlightText(client.description, searchText)}</div>` : ''}
                    <div class="client-date">Date: ${client.date || '-'}</div>
                </div>
                <div class="client-actions">
                    <button class="btn-edit" onclick="editClient('${client.id}')">Edit</button>
                    <button class="btn-delete" onclick="deleteClient('${client.id}')">Delete</button>
                </div>
            </div>
        </div>
    `).join('');
}

function highlightText(text, query) {
    if (!query) return text;

    const esc = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const re = new RegExp(`(${esc})`, 'gi');

    return String(text).replace(re, '<mark>$1</mark>');
}

// Export/Import
function exportData() {
    const data = JSON.stringify(clients, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `unionestate_clients_${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
    showSuccess('Data exported successfully!');
}

async function handleImport(e) {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = async (event) => {
        try {
            const data = JSON.parse(event.target.result);

            if (!Array.isArray(data)) {
                showError('Invalid JSON format');
                return;
            }

            if (!confirm(`Import ${data.length} records? This will replace all existing data.`)) {
                return;
            }

            const response = await fetch('/api/clients/import', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                await loadClients();
                showSuccess(`Imported ${data.length} records successfully!`);
            } else {
                showError('Failed to import data');
            }
        } catch (error) {
            console.error('Import error:', error);
            showError('Invalid JSON file');
        }
    };
    reader.readAsText(file);

    // Reset input
    e.target.value = '';
}

// Notifications
function showSuccess(message) {
    // You could replace this with a nice toast notification
    alert(message);
}

function showError(message) {
    alert(message);
}
