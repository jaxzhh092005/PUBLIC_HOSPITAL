# PUBLIC_HOSPITAL
BAWAT SERBISYO AY PARANG BISYO, 'DI KATATANTANAN
PERO MAY BAYAD HIHI

## Admin access

The Django admin is available at `http://127.0.0.1:8000/admin/`. After applying
the database migrations, create an administrator account locally:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py createsuperuser
```

Enter the username, email, and password in the terminal prompts. Do not store
the password in source control. The superuser can manage the registered
accounts, appointments, doctors, files, hospitals, nurses, and patients.
