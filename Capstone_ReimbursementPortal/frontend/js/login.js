(function() {
    const hadSession = localStorage.getItem('userId');
    localStorage.removeItem('userId');
    localStorage.removeItem('role');
    localStorage.removeItem('userName');
    localStorage.removeItem('userEmail');
    if (hadSession) {
        const msg = document.getElementById('sessionMsg');
        if (msg) {
            msg.style.display = 'block';
        }
    }
})();

function togglePassword() {
    const passwordInput = document.getElementById('password');
    const type = passwordInput.getAttribute('type');
    passwordInput.setAttribute(
        'type', type === 'password' ? 'text' : 'password'
    );
}

async function handleLogin(event) {
    event.preventDefault();

    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const loginBtn = document.getElementById('loginBtn');

    if (!email) {
        showMessage('loginMsg', 'Email is required', true);
        return;
    }

    if (!email.endsWith('@company.com')) {
        showMessage('loginMsg',
            'Email must be a valid @company.com address', true);
        return;
    }

    if (!password || password.length < 8) {
        showMessage('loginMsg',
            'Password must be at least 8 characters', true);
        return;
    }

    loginBtn.textContent = 'Signing in...';
    loginBtn.disabled = true;

    const result = await loginUser({ email, password });

    if (result.status === 'success') {
        const user = result.data;
        localStorage.setItem('userId', user.id);
        localStorage.setItem('role', user.role);
        localStorage.setItem('userName', user.name);
        localStorage.setItem('userEmail', user.email);

        if (user.role === 'ADMIN') {
            window.location.href = 'users.html';
        } else if (user.role === 'MANAGER') {
            window.location.href = 'reviewer.html';
        } else {
            window.location.href = 'claims.html';
        }
    } else {
        showMessage('loginMsg',
            result.message || 'Invalid email or password', true);
        loginBtn.textContent = 'Sign In';
        loginBtn.disabled = false;
    }
}