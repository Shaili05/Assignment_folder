const BASE_URL = 'http://localhost:8081';

async function loginUser(data) {
    try {
        const res = await fetch(`${BASE_URL}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return res.json();
    } catch (err) {
        return { status: 'error', message: 'Could not connect to server' };
    }
}

async function createUser(data) {
    try {
        const res = await fetch(`${BASE_URL}/api/users`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return res.json();
    } catch (err) {
        return { status: 'error', message: 'Could not connect to server' };
    }
}

async function getAllUsers(page = 0, size = 10) {
    try {
        const res = await fetch(
            `${BASE_URL}/api/users?page=${page}&size=${size}`
        );
        return res.json();
    } catch (err) {
        return { status: 'error', message: 'Could not connect to server' };
    }
}

async function deleteUser(id) {
    try {
        const res = await fetch(`${BASE_URL}/api/users/${id}`, {
            method: 'DELETE'
        });
        return res.json();
    } catch (err) {
        return { status: 'error', message: 'Could not connect to server' };
    }
}

async function assignManager(employeeId, managerId) {
    try {
        const res = await fetch(
            `${BASE_URL}/api/users/${employeeId}/assign-manager/${managerId}`,
            { method: 'PUT' }
        );
        return res.json();
    } catch (err) {
        return { status: 'error', message: 'Could not connect to server' };
    }
}

async function submitClaim(data) {
    try {
        const res = await fetch(`${BASE_URL}/api/claims`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return res.json();
    } catch (err) {
        return { status: 'error', message: 'Could not connect to server' };
    }
}

async function getMyClaims(employeeId, page = 0, size = 10) {
    try {
        const res = await fetch(
            `${BASE_URL}/api/claims/employee-claims`
            + `?employeeId=${employeeId}&page=${page}&size=${size}`
        );
        return res.json();
    } catch (err) {
        return { status: 'error', message: 'Could not connect to server' };
    }
}

async function getReviewerClaims(reviewerId, page = 0, size = 10) {
    try {
        const res = await fetch(
            `${BASE_URL}/api/claims/reviewer-claims`
            + `?reviewerId=${reviewerId}&page=${page}&size=${size}`
        );
        return res.json();
    } catch (err) {
        return { status: 'error', message: 'Could not connect to server' };
    }
}

async function getManagerOwnClaims(managerId, page = 0, size = 10) {
    try {
        const res = await fetch(
            `${BASE_URL}/api/claims/manager-own-claims`
            + `?managerId=${managerId}&page=${page}&size=${size}`
        );
        return res.json();
    } catch (err) {
        return { status: 'error', message: 'Could not connect to server' };
    }
}

async function approveClaim(claimId, reviewerId, comment) {
    try {
        const res = await fetch(
            `${BASE_URL}/api/claims/${claimId}/approve`,
            {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ reviewerId, comment })
            }
        );
        return res.json();
    } catch (err) {
        return { status: 'error', message: 'Could not connect to server' };
    }
}

async function rejectClaim(claimId, reviewerId, comment) {
    try {
        const res = await fetch(
            `${BASE_URL}/api/claims/${claimId}/reject`,
            {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ reviewerId, comment })
            }
        );
        return res.json();
    } catch (err) {
        return { status: 'error', message: 'Could not connect to server' };
    }
}