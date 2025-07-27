document.addEventListener('DOMContentLoaded', function() {
    const signupForm = document.getElementById('signupForm');
    const errorDiv = document.getElementById('signupError');
    const submitBtn = signupForm.querySelector('button[type="submit"]');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm_password');
    const strengthBar = document.getElementById('strengthBar');
    
    // Password requirements elements
    const reqLength = document.getElementById('req-length');
    const reqUppercase = document.getElementById('req-uppercase');
    const reqLowercase = document.getElementById('req-lowercase');
    const reqNumber = document.getElementById('req-number');
    const reqSpecial = document.getElementById('req-special');
    
    const originalBtnText = submitBtn.textContent;
    
    function showLoading() {
        submitBtn.innerHTML = '<div class="spinner"></div> Creating Account...';
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
    
    function validatePassword(password) {
        const requirements = {
            length: password.length >= 8,
            uppercase: /[A-Z]/.test(password),
            lowercase: /[a-z]/.test(password),
            number: /\d/.test(password),
            special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
        };
        
        // Update requirement indicators
        reqLength.classList.toggle('met', requirements.length);
        reqUppercase.classList.toggle('met', requirements.uppercase);
        reqLowercase.classList.toggle('met', requirements.lowercase);
        reqNumber.classList.toggle('met', requirements.number);
        reqSpecial.classList.toggle('met', requirements.special);
        
        // Calculate strength
        const metCount = Object.values(requirements).filter(Boolean).length;
        const strength = metCount / 5;
        
        // Update strength bar
        strengthBar.style.width = (strength * 100) + '%';
        strengthBar.className = 'strength-bar';
        
        if (strength < 0.4) {
            strengthBar.classList.add('strength-weak');
        } else if (strength < 0.8) {
            strengthBar.classList.add('strength-medium');
        } else {
            strengthBar.classList.add('strength-strong');
        }
        
        return metCount >= 4; // At least 4 requirements met
    }
    
    function validateForm() {
        const fullName = document.getElementById('full_name').value.trim();
        const email = document.getElementById('email').value.trim();
        const phoneNumber = document.getElementById('phone_number').value.trim();
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;
        
        if (!fullName) {
            showError('Please enter your full name.');
            return false;
        }
        
        if (!email || !email.includes('@')) {
            showError('Please enter a valid email address.');
            return false;
        }
        
        if (!phoneNumber) {
            showError('Please enter your phone number.');
            return false;
        }
        
        if (!validatePassword(password)) {
            showError('Please ensure your password meets all requirements.');
            return false;
        }
        
        if (password !== confirmPassword) {
            showError('Passwords do not match.');
            return false;
        }
        
        return true;
    }

    signupForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        hideError();

        if (!validateForm()) {
            return;
        }

        showLoading();

        const formData = {
            full_name: document.getElementById('full_name').value.trim(),
            email: document.getElementById('email').value.trim(),
            phone_number: document.getElementById('phone_number').value.trim(),
            password: passwordInput.value,
            confirm_password: confirmPasswordInput.value
        };

        try {
            const response = await fetch('/api/account/signup/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(formData)
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Success animation
                submitBtn.innerHTML = '✓ Account Created!';
                submitBtn.style.background = 'linear-gradient(135deg, #27ae60, #2ecc71)';
                
                // Store tokens if provided
                if (data.access && data.refresh) {
                    localStorage.setItem('access', data.access);
                    localStorage.setItem('refresh', data.refresh);
                }
                
                // Redirect to login or dashboard
                setTimeout(() => {
                    window.location.href = '/api/account/login-page/';
                }, 1500);
            } else {
                hideLoading();
                let errorMessage = 'Signup failed. Please try again.';
                
                if (data.email) {
                    errorMessage = data.email[0];
                } else if (data.password) {
                    errorMessage = data.password[0];
                } else if (data.non_field_errors) {
                    errorMessage = data.non_field_errors[0];
                } else if (data.detail) {
                    errorMessage = data.detail;
                }
                
                showError(errorMessage);
                
                // Shake animation for error
                signupForm.style.animation = 'shake 0.5s ease-in-out';
                setTimeout(() => {
                    signupForm.style.animation = '';
                }, 500);
            }
        } catch (err) {
            hideLoading();
            showError('Network error. Please check your connection and try again.');
        }
    });
    
    // Real-time password validation
    passwordInput.addEventListener('input', function() {
        validatePassword(this.value);
        hideError();
    });
    
    // Confirm password validation
    confirmPasswordInput.addEventListener('input', function() {
        if (this.value && this.value !== passwordInput.value) {
            this.style.borderColor = '#e74c3c';
        } else {
            this.style.borderColor = '#e1e5e9';
        }
        hideError();
    });
    
    // Input focus effects
    const inputs = signupForm.querySelectorAll('input');
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