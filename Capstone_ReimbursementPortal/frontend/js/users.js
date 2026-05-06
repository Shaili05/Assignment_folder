if (!requireAuth('ADMIN')) {
    window.location.href = 'login.html';
}

window.addEventListener('pageshow', function(event) {
    if (event.persisted) {
        window.location.replace(window.location.href);
    }
});

setHeaderUserName();

const ADMIN_ID = parseInt(localStorage.getItem('userId'), 10);

function handleLoadUsers() {
    loadUsers().catch(function(err) {
        console.error('Failed to load users', err);
    });
}

function handleLoadAdminClaims() {
    loadAdminClaims().catch(function(err) {
        console.error('Failed to load admin claims', err);
    });
}

handleLoadUsers();

async function handleCreateUser() {
    const name = document.getElementById('name').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const role = document.getElementById('role').value;

    if (!name) {
        showMessage('createMsg', 'Name is required', true);
        return;
    }
    if (!email || !email.endsWith('@company.com')) {
        showMessage('createMsg',
            'Email must be a valid @company.com address', true);
        return;
    }
    if (!password || password.length < 8) {
        showMessage('createMsg',
            'Password must be at least 8 characters', true);
        return;
    }
    if (!role) {
        showMessage('createMsg', 'Please select a role', true);
        return;
    }

    const result = await createUser({ name, email, password, role });

    if (result.status === 'success') {
        showMessage('createMsg', 'User created successfully');
        document.getElementById('name').value = '';
        document.getElementById('email').value = '';
        document.getElementById('password').value = '';
        document.getElementById('role').value = '';
        await loadUsers();
    } else {
        showMessage('createMsg',
            result.message || 'Something went wrong', true);
    }
}

async function handleAssignManager() {
    const empSelect = document.getElementById('employeeSelect');
    const mgrSelect = document.getElementById('managerSelect');
    const empId = empSelect ? empSelect.value : '';
    const mgrId = mgrSelect ? mgrSelect.value : '';

    if (!empId) {
        showMessage('assignMsg', 'Please select an employee', true);
        return;
    }
    if (!mgrId) {
        showMessage('assignMsg', 'Please select a manager', true);
        return;
    }

    const result = await assignManager(empId, mgrId);

    if (result.status === 'success') {
        showMessage('assignMsg', 'Manager assigned successfully');
        await loadUsers();
    } else {
        showMessage('assignMsg',
            result.message || 'Something went wrong', true);
    }
}

function formatManagerName(managerName) {
    if (!managerName) { return '-'; }
    const name = String(managerName).trim();
    if (name.toLowerCase() === 'admin user'
        || name.toLowerCase() === 'admin') {
        return 'Admin';
    }
    return name;
}

async function loadUsers() {
    const result = await getAllUsers();

    if (result.status === 'success') {
        const allUsers = result.data.content;
        const users = allUsers.filter(function(u) {
            return u.role !== 'ADMIN';
        });

        const empSelect = document.getElementById('employeeSelect');
        const mgrSelect = document.getElementById('managerSelect');

        if (empSelect) {
            empSelect.innerHTML =
                '<option value="">-- Select Employee --</option>';
        }
        if (mgrSelect) {
            mgrSelect.innerHTML =
                '<option value="">-- Select Manager --</option>';
        }

        users.forEach(function(user) {
            if (empSelect && user.role === 'EMPLOYEE') {
                empSelect.innerHTML +=
                    '<option value="' + user.id + '">'
                    + user.name + ' (ID: ' + user.id + ')'
                    + '</option>';
            }
            if (mgrSelect && user.role === 'MANAGER') {
                mgrSelect.innerHTML +=
                    '<option value="' + user.id + '">'
                    + user.name + ' (ID: ' + user.id + ')'
                    + '</option>';
            }
        });

        if (users.length === 0) {
            document.getElementById('usersTable')
                .style.display = 'none';
            document.getElementById('usersEmpty')
                .style.display = 'block';
            return;
        }

        let rows = '';
        users.forEach(function(user) {
            const mgrName = formatManagerName(user.managerName);
            const roleLower = user.role.toLowerCase();
            rows += '<tr>'
                + '<td>' + user.id + '</td>'
                + '<td>' + user.name + '</td>'
                + '<td>' + user.email + '</td>'
                + '<td><span class="role-badge role-' + roleLower
                + '">' + user.role + '</span></td>'
                + '<td>' + mgrName + '</td>'
                + '<td><button class="btn-delete" onclick="'
                + 'confirmDeleteUser(' + user.id + ', \''
                + user.name + '\')">'
                + 'Delete</button></td>'
                + '</tr>';
        });

        document.getElementById('usersBody').innerHTML = rows;
        document.getElementById('usersTable').style.display = 'table';
        document.getElementById('usersEmpty').style.display = 'none';
    } else {
        showMessage('usersMsg',
            result.message || 'Failed to load users', true);
    }
}

function confirmDeleteUser(id, name) {
    showConfirm(
        'Are you sure you want to delete <strong>'
        + name + '</strong>?<br>This action cannot be undone.',
        function() {
            handleDeleteUser(id).catch(function(err) {
                console.error('Delete error', err);
            });
        }
    );
}

async function handleDeleteUser(id) {
    const result = await deleteUser(id);
    if (result.status === 'success') {
        showMessage('usersMsg', 'User deleted successfully');
        await loadUsers();
    } else {
        showMessage('usersMsg',
            result.message || 'Delete failed', true);
    }
}

async function loadAdminClaims() {
    const result = await getReviewerClaims(ADMIN_ID);

    if (result.status === 'success') {
        const claims = result.data.content;

        if (claims.length === 0) {
            document.getElementById('adminClaimsTable')
                .style.display = 'none';
            document.getElementById('adminClaimsEmpty')
                .style.display = 'block';
            document.getElementById('adminActionSection')
                .style.display = 'none';
            return;
        }

        let rows = '';
        claims.forEach(function(claim) {
            const empName = claim.employeeName
                ? String(claim.employeeName) : '-';
            const actionBtn = claim.status === 'SUBMITTED'
                ? '<button class="btn-small btn-action" onclick="'
                + 'prefillAdminAction(' + claim.id + ')">'
                + 'Action</button>'
                : '<span class="done-label">Done</span>';

            rows += '<tr>'
                + '<td>' + claim.id + '</td>'
                + '<td>' + empName + '</td>'
                + '<td>&#x20B9;' + claim.amount + '</td>'
                + '<td>' + claim.date + '</td>'
                + '<td>' + claim.description + '</td>'
                + '<td>' + getStatusBadge(claim.status) + '</td>'
                + '<td>' + actionBtn + '</td>'
                + '</tr>';
        });

        document.getElementById('adminClaimsBody').innerHTML = rows;
        document.getElementById('adminClaimsTable')
            .style.display = 'table';
        document.getElementById('adminClaimsEmpty')
            .style.display = 'none';
        document.getElementById('adminActionSection')
            .style.display = 'block';
    } else {
        showMessage('adminClaimsMsg',
            result.message || 'Failed to load claims', true);
    }
}

function prefillAdminAction(claimId) {
    const el = document.getElementById('adminClaimId');
    if (el) {
        el.value = claimId;
        document.getElementById('adminActionSection')
            .scrollIntoView({ behavior: 'smooth' });
    }
}

async function handleAdminApprove() {
    const claimIdEl = document.getElementById('adminClaimId');
    const claimId = parseInt(claimIdEl.value, 10);
    const comment = document.getElementById('adminComment')
        .value.trim();

    if (!claimId || claimId <= 0) {
        showMessage('adminActionMsg',
            'Please enter a valid Claim ID', true);
        return;
    }
    if (!comment) {
        showMessage('adminActionMsg',
            'Comment is required', true);
        return;
    }

    const result = await approveClaim(claimId, ADMIN_ID, comment);

    if (result.status === 'success') {
        showMessage('adminActionMsg', 'Claim approved successfully');
        document.getElementById('adminClaimId').value = '';
        document.getElementById('adminComment').value = '';
        await loadAdminClaims();
    } else {
        showMessage('adminActionMsg',
            result.message || 'Something went wrong', true);
    }
}

async function handleAdminReject() {
    const claimIdEl = document.getElementById('adminClaimId');
    const claimId = parseInt(claimIdEl.value, 10);
    const comment = document.getElementById('adminComment')
        .value.trim();

    if (!claimId || claimId <= 0) {
        showMessage('adminActionMsg',
            'Please enter a valid Claim ID', true);
        return;
    }
    if (!comment) {
        showMessage('adminActionMsg',
            'Comment is required', true);
        return;
    }

    const result = await rejectClaim(claimId, ADMIN_ID, comment);

    if (result.status === 'success') {
        showMessage('adminActionMsg', 'Claim rejected successfully');
        document.getElementById('adminClaimId').value = '';
        document.getElementById('adminComment').value = '';
        await loadAdminClaims();
    } else {
        showMessage('adminActionMsg',
            result.message || 'Something went wrong', true);
    }
}