#!/usr/bin/env python3
"""
Add debugging to users page to identify the issue
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geosurvey.settings')
django.setup()

def add_debugging_to_users_page():
    """Add debugging JavaScript to the users page"""
    print("🔧 Adding debugging to users page...")
    
    # Read the current users.html file
    with open('admindashboard/templates/admindashboard/users.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add debugging JavaScript before the closing </script> tag
    debug_js = '''
        // DEBUGGING CODE
        console.log("🔍 Users page loaded");
        
        // Override loadUsers function with debugging
        const originalLoadUsers = loadUsers;
        loadUsers = function() {
            console.log("🔍 loadUsers() called");
            console.log("🔍 Current page:", currentPage);
            console.log("🔍 Search term:", document.getElementById('searchInput').value);
            console.log("🔍 Status filter:", document.getElementById('statusFilter').value);
            console.log("🔍 Role filter:", document.getElementById('roleFilter').value);
            
            const searchTerm = document.getElementById('searchInput').value;
            const statusFilter = document.getElementById('statusFilter').value;
            const roleFilter = document.getElementById('roleFilter').value;
            const dateFilter = document.getElementById('dateFilter') ? document.getElementById('dateFilter').value : '';
            
            const params = new URLSearchParams({
                page: currentPage,
                search: searchTerm,
                status: statusFilter,
                role: roleFilter,
                date: dateFilter
            });
            
            const apiUrl = `{% url 'admin_api_users' %}?${params}`;
            console.log("🔍 API URL:", apiUrl);
            
            showLoading();
            
            fetch(apiUrl)
                .then(response => {
                    console.log("🔍 Response status:", response.status);
                    console.log("🔍 Response headers:", response.headers);
                    return response.json();
                })
                .then(data => {
                    console.log("🔍 API Response data:", data);
                    hideLoading();
                    if (data.success) {
                        console.log("🔍 Displaying users:", data.users.length);
                        displayUsers(data.users);
                        updateStats(data.stats);
                        updatePagination(data.pagination);
                    } else {
                        console.error("🔍 API Error:", data.message);
                        showToast('Error loading users: ' + data.message, 'error');
                    }
                })
                .catch(error => {
                    console.error("🔍 Fetch Error:", error);
                    hideLoading();
                    showToast('Error loading users: ' + error.message, 'error');
                });
        };
        
        // Override displayUsers function with debugging
        const originalDisplayUsers = displayUsers;
        displayUsers = function(users) {
            console.log("🔍 displayUsers() called with", users.length, "users");
            console.log("🔍 Users data:", users);
            
            const tbody = document.getElementById('usersTableBody');
            console.log("🔍 Table body element:", tbody);
            
            if (!tbody) {
                console.error("🔍 Table body element not found!");
                return;
            }
            
            tbody.innerHTML = '';
            
            if (users.length === 0) {
                console.log("🔍 No users found, showing empty message");
                tbody.innerHTML = `
                    <tr>
                        <td colspan="8" class="text-center py-5">
                            <i class="fas fa-users fa-3x text-muted mb-3"></i>
                            <p class="text-muted">No users found</p>
                        </td>
                    </tr>
                `;
                return;
            }
            
            console.log("🔍 Creating table rows for", users.length, "users");
            users.forEach((user, index) => {
                console.log("🔍 Processing user", index + 1, ":", user);
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" value="${user.id}" onchange="toggleUserSelection(${user.id})">
                        </div>
                    </td>
                    <td>
                        <div class="d-flex align-items-center">
                            <img src="${user.avatar || '{% static "admindashboard/default-avatar.png" %}'}" 
                                 alt="${user.full_name}" class="user-avatar me-3">
                            <div>
                                <div class="font-weight-bold">${user.full_name}</div>
                                <small class="text-muted">@${user.username}</small>
                            </div>
                        </div>
                    </td>
                    <td>${user.email}</td>
                    <td>
                        <span class="status-badge status-${user.is_active ? 'active' : 'inactive'}">
                            ${user.status}
                        </span>
                    </td>
                    <td>${user.role}</td>
                    <td>${formatDate(user.date_joined)}</td>
                    <td>${formatDate(user.last_login)}</td>
                    <td>
                        <div class="btn-group" role="group">
                            <button class="btn btn-sm btn-outline-primary" onclick="viewUser(${user.id})" title="View">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-warning" onclick="editUser(${user.id})" title="Edit">
                                <i class="fas fa-edit"></i>
                            </button>
                            ${user.is_active ? 
                                `<button class="btn btn-sm btn-outline-danger" onclick="suspendUser(${user.id})" title="Suspend">
                                    <i class="fas fa-ban"></i>
                                </button>` :
                                `<button class="btn btn-sm btn-outline-success" onclick="activateUser(${user.id})" title="Activate">
                                    <i class="fas fa-check"></i>
                                </button>`
                            }
                            <button class="btn btn-sm btn-outline-danger" onclick="deleteUser(${user.id})" title="Delete">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </td>
                `;
                tbody.appendChild(row);
                console.log("🔍 Added row for user:", user.username);
            });
            
            console.log("🔍 Finished displaying users");
        };
        
        // Add debugging to page load
        document.addEventListener('DOMContentLoaded', function() {
            console.log("🔍 DOM loaded, users page ready");
            console.log("🔍 Current user session check...");
            
            // Check if user is logged in by making a simple API call
            fetch('{% url "admin_api_users" %}')
                .then(response => {
                    console.log("🔍 Session check - Response status:", response.status);
                    if (response.status === 401) {
                        console.error("🔍 User not authenticated!");
                        alert("Please login to access this page");
                    } else if (response.status === 200) {
                        console.log("🔍 User authenticated successfully");
                    }
                })
                .catch(error => {
                    console.error("🔍 Session check error:", error);
                });
        });
    '''
    
    # Find the closing </script> tag and add debugging before it
    if '</script>' in content:
        content = content.replace('</script>', debug_js + '\n    </script>')
        
        # Write the updated content back
        with open('admindashboard/templates/admindashboard/users.html', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Debugging added to users page!")
        print("🔍 Now when you load the page, check the browser console (F12) for debugging information")
    else:
        print("❌ Could not find </script> tag in users.html")

if __name__ == "__main__":
    add_debugging_to_users_page()
    print("\n✨ Debugging setup completed!") 