document.getElementById('signupForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const full_name = document.getElementById('full_name').value;
    const email = document.getElementById('email').value;
    const phone_number = document.getElementById('phone_number').value;
    const password = document.getElementById('password').value;
    const confirm_password = document.getElementById('confirm_password').value;
    const errorDiv = document.getElementById('signupError');
    errorDiv.textContent = '';

    if (!full_name || !email || !phone_number || !password || !confirm_password) {
        errorDiv.textContent = 'Please fill in all fields.';
        return;
    }
    if (password.length < 8) {
        errorDiv.textContent = 'Password must be at least 8 characters.';
        return;
    }
    if (password !== confirm_password) {
        errorDiv.textContent = 'Passwords do not match.';
        return;
    }

    try {
        const response = await fetch('/api/account/signup/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ full_name, email, phone_number, password, confirm_password })
        });
        const data = await response.json();
        if (response.ok) {
            // Store JWT tokens in localStorage (or cookies)
            localStorage.setItem('access', data.access);
            localStorage.setItem('refresh', data.refresh);
            // Redirect to dashboard or home
            window.location.href = '/dashboard/';
        } else {
            errorDiv.textContent = data.detail || Object.values(data).join(' ') || 'Signup failed.';
        }
    } catch (err) {
        errorDiv.textContent = 'Network error. Please try again.';
    }
}); 