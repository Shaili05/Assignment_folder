function showMessage(elementId, message, isError = false) {
    const el = document.getElementById(elementId);
    el.textContent = message;
    el.className = 'msg ' + (isError ? 'error' : 'success');
    el.style.display = 'block';
    setTimeout(() => { el.style.display = 'none'; }, 4000);
}

function getStatusClass(status) {
    if (status === 'APPROVED') return 'status-approved';
    if (status === 'REJECTED') return 'status-rejected';
    return 'status-submitted';
}