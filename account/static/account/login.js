document.getElementById('loginForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const next = document.getElementById('nextInput') ? document.getElementById('nextInput').value : '';
    const errorDiv = document.getElementById('loginError');
    errorDiv.textContent = '';

    if (!email || !password) {
        errorDiv.textContent = 'Please fill in all fields.';
        return;
    }

    try {
        const response = await fetch('/api/account/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password, next })
        });
        const data = await response.json();
        if (response.ok) {
            // Store JWT tokens in localStorage (or cookies)
            localStorage.setItem('access', data.access);
            localStorage.setItem('refresh', data.refresh);
            // Redirect to dashboard or admin dashboard based on API response
            window.location.href = data.redirect_url || '/dashboard/';
        } else {
            errorDiv.textContent = data.detail || data.non_field_errors || 'Login failed.';
        }
    } catch (err) {
        errorDiv.textContent = 'Network error. Please try again.';
    }
}); 