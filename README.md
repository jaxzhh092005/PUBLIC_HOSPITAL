# PUBLIC_HOSPITAL
BAWAT SERBISYO AY PARANG BISYO, 'DI KATATANTANAN
PERO MAY BAYAD HIHI

## Admin access

Start the application and open the custom hospital admin workspace at
`http://127.0.0.1:8000/HospitalSchedulingAdmin/`:

```powershell
.\venv\Scripts\python.exe manage.py runserver
```

Sign in with a staff administrator account. If you have not created one yet,
run these commands in another terminal:

```powershell
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py createsuperuser
```

The workspace includes a doctor directory and a form for creating doctor
profiles and their login accounts. Existing advanced model-management screens
remain available from the workspace navigation. The built-in Django admin is
still available at `http://127.0.0.1:8000/admin/`.

Doctor accounts sign in at `http://127.0.0.1:8000/signin/` and are sent to
their doctor workspace at `/HospitalSchedulingAdmin/doctor/`, with appointment,
patient record, consult queue, and availability sections.
