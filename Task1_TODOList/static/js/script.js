/**
 * CODSOFT Task 1 — To-Do List Application Frontend JavaScript
 * Handles modal dialogs, seamless AJAX requests with Flask backend,
 * real-time UI updates, dynamic animations, and input validation.
 */

// Global variable to store active delete task ID
let activeDeleteTaskId = null;

document.addEventListener('DOMContentLoaded', () => {
    initSearchFilter();
    initKeyboardShortcuts();
    autoDismissToasts();
});

/* ============================================================== */
/* Modal Management                                               */
/* ============================================================== */

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
        modal.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';

        // Focus first input inside modal
        const firstInput = modal.querySelector('input:not([type="hidden"]), select, textarea');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 100);
        }
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
        modal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
    }
}

// Close modals when clicking overlay outside modal card
document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
            closeModal(overlay.id);
        }
    });
});

// Escape key to close open modals
function initKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal-overlay.active').forEach(modal => {
                closeModal(modal.id);
            });
        }
    });
}

function openAddModal() {
    const form = document.getElementById('addTaskForm');
    if (form) form.reset();
    openModal('addModal');
}

/* ============================================================== */
/* Add Task Handler                                               */
/* ============================================================== */

async function handleAddTask(event) {
    event.preventDefault();
    const form = event.target;
    const submitBtn = document.getElementById('submitAddBtn');

    const titleInput = document.getElementById('addTitle');
    const title = titleInput.value.trim();
    const description = document.getElementById('addDescription').value.trim();
    const priority = document.getElementById('addPriority').value;
    const dueDate = document.getElementById('addDueDate').value;

    if (!title) {
        showToast('Please enter a task title.', 'danger');
        titleInput.focus();
        return;
    }

    // Disable button during request
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="ri-loader-4-line ri-spin"></i> Saving...';

    try {
        const response = await fetch('/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({
                title: title,
                description: description,
                priority: priority,
                due_date: dueDate
            })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            closeModal('addModal');
            form.reset();
            showToast(data.message, 'success');
            
            // Reload page to re-render server-side template or update DOM smoothly
            setTimeout(() => {
                window.location.reload();
            }, 300);
        } else {
            showToast(data.message || 'Failed to create task.', 'danger');
        }
    } catch (error) {
        console.error('Error adding task:', error);
        // Fallback: submit standard form if fetch fails
        form.submit();
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="ri-check-line"></i> <span>Save Task</span>';
    }
}

/* ============================================================== */
/* Edit Task Handler                                              */
/* ============================================================== */

async function openEditModal(taskId) {
    try {
        const response = await fetch(`/api/tasks/${taskId}`);
        const data = await response.json();

        if (data.success && data.task) {
            const task = data.task;
            document.getElementById('editTaskId').value = task.id;
            document.getElementById('editTitle').value = task.title || '';
            document.getElementById('editDescription').value = task.description || '';
            document.getElementById('editPriority').value = task.priority || 'MEDIUM';
            document.getElementById('editDueDate').value = task.due_date || '';

            openModal('editModal');
        } else {
            showToast(data.message || 'Unable to load task data.', 'danger');
        }
    } catch (error) {
        console.error('Error fetching task details:', error);
        showToast('Network error while loading task.', 'danger');
    }
}

async function handleUpdateTask(event) {
    event.preventDefault();
    const form = event.target;
    const taskId = document.getElementById('editTaskId').value;
    const submitBtn = document.getElementById('submitEditBtn');

    const title = document.getElementById('editTitle').value.trim();
    const description = document.getElementById('editDescription').value.trim();
    const priority = document.getElementById('editPriority').value;
    const dueDate = document.getElementById('editDueDate').value;

    if (!title) {
        showToast('Task title cannot be empty.', 'danger');
        return;
    }

    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="ri-loader-4-line ri-spin"></i> Updating...';

    try {
        const response = await fetch(`/update/${taskId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({
                title: title,
                description: description,
                priority: priority,
                due_date: dueDate
            })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            closeModal('editModal');
            showToast(data.message, 'success');
            setTimeout(() => {
                window.location.reload();
            }, 300);
        } else {
            showToast(data.message || 'Failed to update task.', 'danger');
        }
    } catch (error) {
        console.error('Error updating task:', error);
        showToast('An error occurred while updating the task.', 'danger');
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="ri-save-line"></i> <span>Update Task</span>';
    }
}

/* ============================================================== */
/* Toggle Task Status (Complete / Pending)                        */
/* ============================================================== */

async function toggleTaskStatus(taskId) {
    const card = document.getElementById(`task-card-${taskId}`);
    const toggleBtn = card ? card.querySelector('.task-toggle-btn') : null;

    try {
        const response = await fetch(`/toggle/${taskId}`, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        const data = await response.json();

        if (response.ok && data.success) {
            const task = data.task;
            const stats = data.stats;

            // Update UI card state
            if (card && toggleBtn) {
                if (task.completed === 1) {
                    card.classList.add('task-completed');
                    toggleBtn.classList.add('checked');
                    toggleBtn.title = 'Mark as pending';
                    card.setAttribute('data-completed', '1');
                } else {
                    card.classList.remove('task-completed');
                    toggleBtn.classList.remove('checked');
                    toggleBtn.title = 'Mark as completed';
                    card.setAttribute('data-completed', '0');
                }
            }

            // Update Statistics
            if (stats) {
                updateStatsUI(stats);
            }

            showToast(data.message, 'info');

            // If active filter is PENDING or COMPLETED, gently hide the card
            const currentFilter = document.querySelector('.filter-pill.active')?.dataset?.filter;
            if (currentFilter && currentFilter !== 'ALL') {
                if ((currentFilter === 'PENDING' && task.completed === 1) || 
                    (currentFilter === 'COMPLETED' && task.completed === 0)) {
                    card.style.transition = 'all 0.3s ease';
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(10px)';
                    setTimeout(() => card.remove(), 300);
                }
            }
        } else {
            showToast(data.message || 'Failed to toggle task.', 'danger');
        }
    } catch (error) {
        console.error('Error toggling task:', error);
        showToast('Failed to change task status.', 'danger');
    }
}

/* ============================================================== */
/* Delete Task Handler                                            */
/* ============================================================== */

function openDeleteModal(taskId, taskTitle) {
    activeDeleteTaskId = taskId;
    const previewEl = document.getElementById('deleteTaskTitlePreview');
    if (previewEl) {
        previewEl.textContent = `"${taskTitle}"`;
    }
    openModal('deleteModal');
}

async function handleConfirmDelete() {
    if (!activeDeleteTaskId) return;

    const taskId = activeDeleteTaskId;
    const confirmBtn = document.getElementById('confirmDeleteBtn');
    confirmBtn.disabled = true;
    confirmBtn.innerHTML = '<i class="ri-loader-4-line ri-spin"></i> Deleting...';

    try {
        const response = await fetch(`/delete/${taskId}`, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        const data = await response.json();

        if (response.ok && data.success) {
            closeModal('deleteModal');
            showToast(data.message, 'info');

            // Smoothly remove card from DOM
            const card = document.getElementById(`task-card-${taskId}`);
            if (card) {
                card.style.transition = 'all 0.3s ease';
                card.style.opacity = '0';
                card.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    card.remove();
                    // Check if list is empty
                    const remainingCards = document.querySelectorAll('.task-card');
                    if (remainingCards.length === 0) {
                        window.location.reload();
                    }
                }, 300);
            }

            // Update stats
            if (data.stats) {
                updateStatsUI(data.stats);
            }
        } else {
            showToast(data.message || 'Failed to delete task.', 'danger');
        }
    } catch (error) {
        console.error('Error deleting task:', error);
        showToast('Failed to delete task.', 'danger');
    } finally {
        confirmBtn.disabled = false;
        confirmBtn.innerHTML = '<i class="ri-delete-bin-line"></i> <span>Delete</span>';
        activeDeleteTaskId = null;
    }
}

/* ============================================================== */
/* Real-Time UI Statistics Update                                 */
/* ============================================================== */

function updateStatsUI(stats) {
    const totalEl = document.getElementById('statTotal');
    const completedEl = document.getElementById('statCompleted');
    const pendingEl = document.getElementById('statPending');
    const percentEl = document.getElementById('progressPercent');
    const progressFill = document.getElementById('progressFill');

    if (totalEl) totalEl.textContent = stats.total;
    if (completedEl) completedEl.textContent = stats.completed;
    if (pendingEl) pendingEl.textContent = stats.pending;
    if (percentEl) percentEl.textContent = `${stats.percent}%`;
    if (progressFill) {
        progressFill.style.width = `${stats.percent}%`;
    }
}

/* ============================================================== */
/* Search & Filter Interactions                                   */
/* ============================================================== */

function initSearchFilter() {
    const searchInput = document.getElementById('taskSearchInput');
    const clearBtn = document.getElementById('clearSearchBtn');

    if (!searchInput) return;

    // Instant client-side filtering as user types
    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase().trim();
        const cards = document.querySelectorAll('.task-card');
        let visibleCount = 0;

        cards.forEach(card => {
            const title = card.querySelector('.task-title')?.textContent.toLowerCase() || '';
            const desc = card.querySelector('.task-desc')?.textContent.toLowerCase() || '';

            if (title.includes(query) || desc.includes(query)) {
                card.style.display = 'flex';
                visibleCount++;
            } else {
                card.style.display = 'none';
            }
        });

        // Show/hide clear button
        if (clearBtn) {
            clearBtn.style.display = query ? 'flex' : 'none';
        }
    });

    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            searchInput.value = '';
            searchInput.dispatchEvent(new Event('input'));
            searchInput.focus();
        });
    }
}

/* ============================================================== */
/* Toast Notification Helper                                      */
/* ============================================================== */

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast-alert toast-${type}`;
    toast.setAttribute('role', 'alert');

    let iconClass = 'ri-information-fill';
    if (type === 'success') iconClass = 'ri-checkbox-circle-fill';
    else if (type === 'danger') iconClass = 'ri-error-warning-fill';
    else if (type === 'warning') iconClass = 'ri-alert-fill';

    toast.innerHTML = `
        <div class="toast-icon"><i class="${iconClass}"></i></div>
        <div class="toast-text">${escapeHtml(message)}</div>
        <button type="button" class="toast-close" onclick="this.parentElement.remove()" aria-label="Close notification">
            <i class="ri-close-line"></i>
        </button>
    `;

    container.appendChild(toast);

    // Auto dismiss after 4 seconds
    setTimeout(() => {
        if (toast.parentElement) {
            toast.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(40px)';
            setTimeout(() => toast.remove(), 300);
        }
    }, 4000);
}

function autoDismissToasts() {
    document.querySelectorAll('.toast-alert').forEach(toast => {
        setTimeout(() => {
            if (toast.parentElement) {
                toast.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                toast.style.opacity = '0';
                toast.style.transform = 'translateX(40px)';
                setTimeout(() => toast.remove(), 300);
            }
        }, 4000);
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
