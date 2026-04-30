loadUsers();

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
        showMessage('createMsg', 'User created successfully!');
        loadUsers();
    } else {
        showMessage('createMsg',
            result.message || 'Something went wrong', true);
    }
}

async function handleAssignManager() {
    const empId = document.getElementById('empId').value;
    const mgrId = document.getElementById('mgrId').value;

    if (!empId || !mgrId) {
        showMessage('assignMsg', 'Please enter both IDs', true);
        return;
    }

    const result = await assignManager(empId, mgrId);

    if (result.status === 'success') {
        showMessage('assignMsg', 'Manager assigned successfully!');
        loadUsers();
    } else {
        showMessage('assignMsg',
            result.message || 'Something went wrong', true);
    }
}

async function loadUsers() {
    const result = await getAllUsers();

    if (result.status === 'success') {
        const users = result.data.content;
        let rows = '';

        users.forEach(user => {
            rows += `
                <tr>
                    <td>${user.id}</td>
                    <td>${user.name}</td>
                    <td>${user.email}</td>
                    <td>${user.role}</td>
                    <td>${user.managerName || '-'}</td>
                    <td>
                        <button onclick="handleDeleteUser(${user.id})">
                            Delete
                        </button>
                    </td>
                </tr>
            `;
        });

        document.getElementById('usersBody').innerHTML = rows;
        document.getElementById('usersTable').style.display = 'table';
    } else {
        showMessage('usersMsg',
            result.message || 'Failed to load users', true);
    }
}

async function handleDeleteUser(id) {
    if (!confirm('Are you sure you want to delete this user?')) return;

    const result = await deleteUser(id);

    if (result.status === 'success') {
        showMessage('usersMsg', 'User deleted!');
        loadUsers();
    } else {
        showMessage('usersMsg',
            result.message || 'Delete failed', true);
    }
}