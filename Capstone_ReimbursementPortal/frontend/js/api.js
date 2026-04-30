const BASE_URL = 'http://localhost:8081';

async function createUser(data) {
    const res = await fetch(`${BASE_URL}/api/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    return res.json();
}

async function getAllUsers(page = 0, size = 10) {
    const res = await fetch(`${BASE_URL}/api/users?page=${page}&size=${size}`);
    return res.json();
}

async function assignManager(employeeId, managerId) {
    const res = await fetch(`${BASE_URL}/api/users/${employeeId}/assign-manager/${managerId}`, {
        method: 'PUT'
    });
    return res.json();
}

async function submitClaim(data) {
    const res = await fetch(`${BASE_URL}/api/claims`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    return res.json();
}

async function getMyClaims(employeeId, page = 0, size = 10) {
    const res = await fetch(`${BASE_URL}/api/claims/my?employeeId=${employeeId}&page=${page}&size=${size}`);
    return res.json();
}

async function getReviewerClaims(reviewerId, page = 0, size = 10) {
    const res = await fetch(`${BASE_URL}/api/claims/reviewer?reviewerId=${reviewerId}&page=${page}&size=${size}`);
    return res.json();
}

async function approveClaim(claimId, reviewerId, comment) {
    const res = await fetch(`${BASE_URL}/api/claims/${claimId}/approve`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reviewerId, comment })
    });
    return res.json();
}

async function rejectClaim(claimId, reviewerId, comment) {
    const res = await fetch(`${BASE_URL}/api/claims/${claimId}/reject`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reviewerId, comment })
    });
    return res.json();
}

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