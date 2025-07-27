document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const errorDiv = document.getElementById('loginError');
    const submitBtn = loginForm.querySelector('button[type="submit"]');
    
    // Add loading spinner to button
    const originalBtnText = submitBtn.textContent;
    
    function showLoading() {
        submitBtn.innerHTML = '<div class="spinner"></div> Logging in...';
        submitBtn.disabled = true;
    }
    
    function hideLoading() {
        submitBtn.textContent = originalBtnText;
        submitBtn.disabled = false;
    }
    
    function showError(message) {
        errorDiv.textContent = message;
        errorDiv.classList.add('show');
        setTimeout(() => {
            errorDiv.classList.remove('show');
        }, 5000);
    }
    
    function hideError() {
        errorDiv.classList.remove('show');
    }

    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;
        const next = document.getElementById('nextInput') ? document.getElementById('nextInput').value : '';
        
        hideError();

        // Validation
        if (!email || !password) {
            showError('Please fill in all fields.');
            return;
        }
        
        if (!email.includes('@')) {
            showError('Please enter a valid email address.');
            return;
        }

        showLoading();

        try {
            const response = await fetch('/api/account/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ email, password, next })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Store JWT tokens
                localStorage.setItem('access', data.access);
                localStorage.setItem('refresh', data.refresh);
                
                // Success animation
                submitBtn.innerHTML = '✓ Success!';
                submitBtn.style.background = 'linear-gradient(135deg, #27ae60, #2ecc71)';
                
                // Redirect after a brief delay
                setTimeout(() => {
                    window.location.href = data.redirect_url || '/dashboard/';
                }, 1000);
            } else {
                hideLoading();
                const errorMessage = data.detail || data.non_field_errors || data.email || data.password || 'Login failed. Please check your credentials.';
                showError(errorMessage);
                
                // Shake animation for error
                loginForm.style.animation = 'shake 0.5s ease-in-out';
                setTimeout(() => {
                    loginForm.style.animation = '';
                }, 500);
            }
        } catch (err) {
            hideLoading();
            showError('Network error. Please check your connection and try again.');
        }
    });
    
    // Input focus effects
    const inputs = loginForm.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            if (!this.value) {
                this.parentElement.classList.remove('focused');
            }
        });
        
        // Auto-hide error when user starts typing
        input.addEventListener('input', hideError);
    });
    
    // Get CSRF token from cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});

// Add shake animation
const style = document.createElement('style');
style.textContent = `
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
    
    .input-group.focused label {
        color: #667eea;
        transform: translateY(-2px);
    }
    
    .input-group.focused input {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
`;
document.head.appendChild(style); 