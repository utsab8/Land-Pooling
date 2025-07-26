from account.models import User

u, created = User.objects.get_or_create(email='acharyautsab390@gmail.com', defaults={'username': 'acharyautsab390@gmail.com'})
u.set_password('utsab12@')
u.full_name = 'Admin User'
u.save()
print('Password reset for:', u.email) 