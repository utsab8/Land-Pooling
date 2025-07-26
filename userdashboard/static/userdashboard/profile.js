// Smooth Scrolling Functionality for Profile Page
document.addEventListener('DOMContentLoaded', function() {
    initializeSmoothScrolling();
    initializeScrollAnimations();
    initializeScrollToTop();
});

// Initialize smooth scrolling functionality
function initializeSmoothScrolling() {
    // Cache DOM elements for better performance
    const navDots = document.querySelectorAll('.nav-dot');
    const sections = [
        'profile-overview',
        'profile-details', 
        'password-section',
        'activity-section',
        'data-management',
        'danger-zone'
    ];
    
    // Cache section elements
    const sectionElements = sections.map(id => document.getElementById(id)).filter(el => el !== null);
    
    // Smooth scroll to section function
    window.scrollToSection = function(sectionId) {
        const element = document.getElementById(sectionId);
        if (element) {
            element.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    };

    // Scroll to top function
    window.scrollToTop = function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    };

    // Update active navigation dot based on scroll position
    function updateActiveNavDot() {
        const scrollPosition = window.scrollY + 150; // Reduced offset for better performance
        
        let activeIndex = -1;
        
        // Find which section is currently in view
        for (let i = 0; i < sectionElements.length; i++) {
            const section = sectionElements[i];
            const sectionTop = section.offsetTop;
            const sectionBottom = sectionTop + section.offsetHeight;
            
            if (scrollPosition >= sectionTop && scrollPosition < sectionBottom) {
                activeIndex = i;
                break;
            }
        }
        
        // Only update if the active section changed
        if (activeIndex !== -1) {
            navDots.forEach((dot, index) => {
                if (index === activeIndex) {
                    dot.classList.add('active');
                } else {
                    dot.classList.remove('active');
                }
            });
        }
    }

    // Improved throttle function for better performance
    function throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        }
    }

    // Use passive event listener for better scroll performance
    const throttledUpdateNav = throttle(updateActiveNavDot, 150); // Increased throttle time
    
    window.addEventListener('scroll', throttledUpdateNav, { passive: true });
    
    // Initial call to set active dot
    updateActiveNavDot();
}

// Initialize scroll animations with optimized observer
function initializeScrollAnimations() {
    // Use a more efficient intersection observer
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px' // Increased margin for better performance
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // Use requestAnimationFrame for smoother animations
                requestAnimationFrame(() => {
                    entry.target.classList.add('visible');
                });
            }
        });
    }, observerOptions);

    // Observe all profile section blocks
    const sectionBlocks = document.querySelectorAll('.profile-section-block');
    sectionBlocks.forEach(block => {
        observer.observe(block);
    });
}

// Initialize scroll to top button with optimized performance
function initializeScrollToTop() {
    const scrollToTopBtn = document.querySelector('.scroll-to-top');
    
    if (scrollToTopBtn) {
        let isVisible = false;
        
        const checkScrollPosition = () => {
            const shouldBeVisible = window.scrollY > 300;
            
            if (shouldBeVisible !== isVisible) {
                isVisible = shouldBeVisible;
                if (isVisible) {
                    scrollToTopBtn.classList.add('visible');
                } else {
                    scrollToTopBtn.classList.remove('visible');
                }
            }
        };
        
        // Throttle the scroll check for better performance
        const throttledCheck = throttle(checkScrollPosition, 100);
        window.addEventListener('scroll', throttledCheck, { passive: true });
    }
}

// Avatar preview, validation, and upload enhancements
const avatarInput = document.getElementById('avatarInput');
const avatarPreview = document.getElementById('avatarPreview');
const profileForm = document.getElementById('profileForm');
const profileMsg = document.getElementById('profileMsg');

// Toast notification
function showToast(msg, success = true) {
    let toast = document.createElement('div');
    toast.className = 'profile-toast ' + (success ? 'success' : 'error');
    toast.textContent = msg;
    document.body.appendChild(toast);
    setTimeout(() => { toast.classList.add('show'); }, 10);
    setTimeout(() => { toast.classList.remove('show'); setTimeout(() => toast.remove(), 400); }, 2500);
}

// Remove/reset avatar
function addRemoveAvatarBtn() {
    let btn = document.getElementById('removeAvatarBtn');
    if (!btn) {
        btn = document.createElement('button');
        btn.type = 'button';
        btn.id = 'removeAvatarBtn';
        btn.className = 'avatar-remove-btn';
        btn.textContent = 'Remove';
        avatarPreview.parentNode.appendChild(btn);
        btn.onclick = function() {
            avatarPreview.src = '/static/userdashboard/user.png';
            if (avatarInput) avatarInput.value = '';
            showToast('Avatar reset to default.', true);
        };
    }
}

if (avatarInput && avatarPreview) {
    avatarInput.addEventListener('change', function() {
        if (avatarInput.files && avatarInput.files[0]) {
            const file = avatarInput.files[0];
            // Validate type
            if (!file.type.startsWith('image/')) {
                showToast('Please select an image file.', false);
                avatarInput.value = '';
                return;
            }
            // Validate size (2MB max)
            if (file.size > 2 * 1024 * 1024) {
                showToast('Image must be less than 2MB.', false);
                avatarInput.value = '';
                return;
            }
            const reader = new FileReader();
            reader.onload = function(e) {
                avatarPreview.src = e.target.result;
                addRemoveAvatarBtn();
            };
            reader.readAsDataURL(file);
        }
    });
}

// AJAX profile update with progress
if (profileForm) {
    profileForm.addEventListener('submit', function(e) {
        e.preventDefault();
        profileMsg.textContent = '';
        const formData = new FormData(profileForm);
        
        // Show progress bar
        let progressBar = document.getElementById('avatarProgressBar');
        if (!progressBar) {
            progressBar = document.createElement('div');
            progressBar.id = 'avatarProgressBar';
            progressBar.className = 'avatar-progress-bar';
            profileForm.appendChild(progressBar);
        }
        progressBar.style.width = '0%';
        progressBar.style.display = 'block';
        
        // Show loading state
        const submitBtn = profileForm.querySelector('.profile-update-btn');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Updating...';
        submitBtn.disabled = true;
        
        // AJAX upload
        const xhr = new XMLHttpRequest();
        xhr.open('POST', window.location.pathname, true);
        xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
        
        xhr.upload.onprogress = function(e) {
            if (e.lengthComputable) {
                const percent = Math.round((e.loaded / e.total) * 100);
                progressBar.style.width = percent + '%';
            }
        };
        
        xhr.onload = function() {
            progressBar.style.display = 'none';
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
            
            if (xhr.status === 200) {
                try {
                    const response = JSON.parse(xhr.responseText);
                    showToast(response.message, response.status === 'success');
                    
                    if (response.status === 'success') {
                        // Update profile completion
                        updateProfileCompletion();
                        
                        // Clear form fields if needed
                        if (response.clearFields) {
                            profileForm.reset();
                        }
                        
                        // Update avatar preview if it was changed
                        if (response.avatar_url) {
                            avatarPreview.src = response.avatar_url;
                        }
                    }
                } catch (e) {
                    // If response is not JSON, it's a full page reload
                    showToast('Profile updated successfully!', true);
                    updateProfileCompletion();
                    // Reload page to show updated data
                    setTimeout(() => {
                        window.location.reload();
                    }, 1500);
                }
            } else if (xhr.status === 403) {
                showToast('CSRF token error. Please refresh the page and try again.', false);
            } else {
                showToast('Upload failed. Please try again.', false);
            }
        };
        
        xhr.onerror = function() {
            progressBar.style.display = 'none';
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
            showToast('Network error. Please check your connection and try again.', false);
        };
        
        xhr.send(formData);
    });
}

// Update profile completion percentage
function updateProfileCompletion() {
    const fields = [
        document.getElementById('full_name').value.trim(),
        document.getElementById('phone_number').value.trim(),
        document.getElementById('linkedin').value.trim(),
        document.getElementById('github').value.trim(),
        avatarPreview.src.indexOf('user.png') === -1
    ];
    
    const filled = fields.filter(field => field).length;
    const percentage = Math.round((filled / fields.length) * 100);
    
    const fill = document.getElementById('profileCompletionFill');
    if (fill) {
        fill.style.width = percentage + '%';
        fill.textContent = percentage + '%';
    }
}

// Password change AJAX
const passwordForm = document.getElementById('passwordForm');
const passwordMsg = document.getElementById('passwordMsg');
if (passwordForm) {
    passwordForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        passwordMsg.textContent = '';
        
        // Enhanced client-side validation
        const currentPassword = document.getElementById('current_password').value;
        const newPassword = document.getElementById('new_password').value;
        const confirmPassword = document.getElementById('confirm_password').value;
        
        if (!currentPassword) {
            showToast('Current password is required.', false);
            return;
        }
        if (!newPassword) {
            showToast('New password is required.', false);
            return;
        }
        if (newPassword.length < 8) {
            showToast('New password must be at least 8 characters long.', false);
            return;
        }
        if (newPassword.length > 128) {
            showToast('New password must be less than 128 characters.', false);
            return;
        }
        if (newPassword !== confirmPassword) {
            showToast('New passwords do not match.', false);
            return;
        }
        if (newPassword === currentPassword) {
            showToast('New password must be different from current password.', false);
            return;
        }
        
        // Password strength validation
        const hasUpper = /[A-Z]/.test(newPassword);
        const hasLower = /[a-z]/.test(newPassword);
        const hasDigit = /\d/.test(newPassword);
        const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(newPassword);
        
        if (!hasUpper || !hasLower || !hasDigit || !hasSpecial) {
            showToast('Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character.', false);
            return;
        }
        
        // Show loading state
        const submitBtn = passwordForm.querySelector('.profile-update-btn');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Changing Password...';
        submitBtn.disabled = true;
        
        const formData = new FormData(passwordForm);
        
        try {
            const response = await fetch(window.location.pathname, {
                method: 'POST',
                headers: {'X-Requested-With': 'XMLHttpRequest'},
                body: formData
            });
            
            if (response.ok) {
                try {
                    const data = await response.json();
                    showToast(data.message, data.status === 'success');
                    passwordMsg.textContent = data.message;
                    
                    if (data.status === 'success') {
                        // Clear form fields
                        document.getElementById('current_password').value = '';
                        document.getElementById('new_password').value = '';
                        document.getElementById('confirm_password').value = '';
                        
                        // Show success message for longer
                        setTimeout(() => {
                            showToast('Password changed successfully! You can now use your new password.', true);
                        }, 1000);
                    }
                } catch (e) {
                    // If response is not JSON, it's a full page reload
                    const html = await response.text();
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, 'text/html');
                    const msg = doc.getElementById('passwordMsg');
                    if (msg) {
                        passwordMsg.textContent = msg.textContent;
                        showToast(msg.textContent, !msg.textContent.toLowerCase().includes('incorrect') && !msg.textContent.toLowerCase().includes('not match'));
                    }
                }
            } else if (response.status === 403) {
                showToast('CSRF token error. Please refresh the page and try again.', false);
            } else {
                showToast('Password update failed. Please try again.', false);
            }
        } catch (err) {
            passwordMsg.textContent = 'Network error. Please check your connection and try again.';
            showToast(passwordMsg.textContent, false);
        } finally {
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }
    });
}
// Delete account AJAX
const deleteAccountBtn = document.getElementById('deleteAccountBtn');
if (deleteAccountBtn) {
    deleteAccountBtn.addEventListener('click', function() {
        if (confirm('Are you sure you want to delete your account? This cannot be undone.')) {
            const formData = new FormData();
            formData.append('delete_account', '1');
            fetch(window.location.pathname, {
                method: 'POST',
                headers: {'X-Requested-With': 'XMLHttpRequest'},
                body: formData
            }).then(() => {
                showToast('Account deleted. Redirecting...', true);
                setTimeout(() => { window.location.href = '/api/account/login-page/'; }, 1200);
            });
        }
    });
}
// Theme switcher with animation
const themeToggleBtn = document.getElementById('themeToggleBtn');
if (themeToggleBtn) {
    const darkClass = 'dark-theme';
    function setTheme(dark) {
        if (dark) {
            document.body.classList.add(darkClass);
            themeToggleBtn.textContent = '☀️';
            themeToggleBtn.style.transform = 'rotate(360deg) scale(1.2)';
            localStorage.setItem('theme', 'dark');
        } else {
            document.body.classList.remove(darkClass);
            themeToggleBtn.textContent = '🌙';
            themeToggleBtn.style.transform = 'rotate(0deg) scale(1)';
            localStorage.setItem('theme', 'light');
        }
    }
    themeToggleBtn.addEventListener('click', function() {
        themeToggleBtn.style.transition = 'transform 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55)';
        setTheme(!document.body.classList.contains(darkClass));
        setTimeout(() => {
            themeToggleBtn.style.transform = '';
        }, 600);
    });
    // On load
    setTheme(localStorage.getItem('theme') === 'dark');
}

// Add staggered animations to profile sections
document.addEventListener('DOMContentLoaded', function() {
    const sections = document.querySelectorAll('.profile-section-block');
    sections.forEach((section, index) => {
        section.style.animationDelay = `${index * 0.15}s`;
        section.style.animationFillMode = 'both';
    });
    
    // Add floating animation to stats
    const statItems = document.querySelectorAll('.stat-item');
    statItems.forEach((item, index) => {
        item.style.animationDelay = `${index * 0.3}s`;
        item.style.animation = 'float 4s ease-in-out infinite';
    });
    
    // Add parallax effect to background
    window.addEventListener('scroll', function() {
        const scrolled = window.pageYOffset;
        const parallax = document.querySelector('.profile-section');
        if (parallax) {
            const speed = scrolled * 0.5;
            parallax.style.transform = `translateY(${speed}px)`;
        }
    });
    
    // Add typing effect to title
    const title = document.querySelector('.profile-header h2');
    if (title) {
        const text = title.textContent;
        title.textContent = '';
        let i = 0;
        const typeWriter = () => {
            if (i < text.length) {
                title.textContent += text.charAt(i);
                i++;
                setTimeout(typeWriter, 100);
            }
        };
        setTimeout(typeWriter, 1000);
    }
    
    // Add sparkle effect to buttons
    const buttons = document.querySelectorAll('.profile-update-btn, .export-data-btn');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.05) translateY(-3px)';
            this.style.boxShadow = '0 20px 40px rgba(0,0,0,0.3)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1) translateY(0)';
            this.style.boxShadow = '0 12px 35px rgba(0,0,0,0.2)';
        });
    });
});

// Password strength indicator
const newPasswordInput = document.getElementById('new_password');
const passwordStrengthIndicator = document.getElementById('passwordStrength');

if (newPasswordInput && passwordStrengthIndicator) {
    newPasswordInput.addEventListener('input', function() {
        const password = this.value;
        const strength = calculatePasswordStrength(password);
        updatePasswordStrengthIndicator(strength);
    });
}

function calculatePasswordStrength(password) {
    let score = 0;
    
    if (password.length >= 8) score += 1;
    if (password.length >= 12) score += 1;
    if (/[a-z]/.test(password)) score += 1;
    if (/[A-Z]/.test(password)) score += 1;
    if (/\d/.test(password)) score += 1;
    if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) score += 1;
    if (password.length >= 16) score += 1;
    
    if (score <= 2) return 'weak';
    if (score <= 4) return 'fair';
    if (score <= 6) return 'good';
    return 'strong';
}

function updatePasswordStrengthIndicator(strength) {
    passwordStrengthIndicator.className = 'password-strength ' + strength;
}

// Enhanced toast with bounce effect
function showToast(msg, success = true) {
    let toast = document.createElement('div');
    toast.className = 'profile-toast ' + (success ? 'success' : 'error');
    toast.textContent = msg;
    toast.style.transform = 'translateX(-50%) scale(0.5) translateY(50px)';
    document.body.appendChild(toast);
    
    setTimeout(() => { 
        toast.classList.add('show'); 
        toast.style.transform = 'translateX(-50%) scale(1) translateY(-10px)';
    }, 10);
    
    setTimeout(() => { 
        toast.classList.remove('show'); 
        toast.style.transform = 'translateX(-50%) scale(0.8) translateY(20px)';
        setTimeout(() => toast.remove(), 400); 
    }, 3000);
} 