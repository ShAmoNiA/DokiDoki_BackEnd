FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code
COPY requirements.txt /code/

RUN pip install -r requirements.txt
RUN python3 manage.py makemigrations
RUN python3 manage.py migrate

RUN python manage.py loaddata "doctors.json"
RUN python manage.py loaddata "patients.json"
RUN python manage.py loaddata "doctor_profiles.json"
RUN python manage.py loaddata "patient_profiles.json"
RUN python manage.py loaddata "tags.json"
RUN python manage.py loaddata "expertises.json"
RUN python manage.py loaddata "chats.json"
RUN python manage.py loaddata "messages.json"

RUN python manage.py set_password_for_fixtures_users
RUN python manage.py create_admin_admin

COPY . /code/