function showMessage(elementId, message, isError) {
    const isErr = isError || false;
    const el = document.getElementById(elementId);
    if (!el) { return; }
    el.textContent = message;
    el.className = 'msg ' + (isErr ? 'error' : 'success');
    el.style.display = 'block';
    setTimeout(function() {
        el.style.display = 'none';
    }, 4000);
}

function getStatusClass(status) {
    if (status === 'APPROVED') { return 'status-approved'; }
    if (status === 'REJECTED') { return 'status-rejected'; }
    if (status === 'CANCELLED') { return 'status-cancelled'; }
    return 'status-submitted';
}

function getStatusBadge(status) {
    const cls = getStatusClass(status);
    return '<span class="status-badge ' + cls + '">'
        + status + '</span>';
}

function showConfirm(message, onConfirm) {
    const existing = document.getElementById('customModal');
    if (existing) { existing.remove(); }

    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.id = 'customModal';

    overlay.innerHTML = '<div class="modal-box">'
        + '<div class="modal-icon">&#x26A0;&#xFE0F;</div>'
        + '<div class="modal-title">Confirm Action</div>'
        + '<div class="modal-message">' + message + '</div>'
        + '<div class="modal-actions">'
        + '<button class="modal-btn-cancel" id="modalCancel">'
        + 'Cancel</button>'
        + '<button class="modal-btn-confirm" id="modalConfirm">'
        + 'Yes, Delete</button>'
        + '</div>'
        + '</div>';

    document.body.appendChild(overlay);

    document.getElementById('modalConfirm')
        .addEventListener('click', function() {
            overlay.remove();
            onConfirm();
        });

    document.getElementById('modalCancel')
        .addEventListener('click', function() {
            overlay.remove();
        });

    overlay.addEventListener('click', function(e) {
        if (e.target === overlay) {
            overlay.remove();
        }
    });
}

function logout() {
    localStorage.removeItem('userId');
    localStorage.removeItem('role');
    localStorage.removeItem('userName');
    localStorage.removeItem('userEmail');
    window.location.href = 'login.html';
}

function requireAuth(expectedRole) {
    const userId = localStorage.getItem('userId');
    const role = localStorage.getItem('role');
    if (!userId) {
        window.location.href = 'login.html';
        return false;
    }
    if (expectedRole && role !== expectedRole) {
        window.location.href = 'login.html';
        return false;
    }
    return true;
}

function setHeaderUserName() {
    const name = localStorage.getItem('userName');
    const el = document.getElementById('headerUserName');
    if (el && name) {
        el.textContent = name;
    }
}