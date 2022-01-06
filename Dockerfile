FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code
COPY requirements.txt /code/

RUN pip install -r requirements.txt
RUN python3 manage.py makemigrations
RUN python3 manage.py migrate

python manage.py loaddata "doctors.json"
python manage.py loaddata "patients.json"
python manage.py loaddata "doctor_profiles.json"
python manage.py loaddata "patient_profiles.json"
python manage.py loaddata "tags.json"
python manage.py loaddata "expertises.json"
python manage.py loaddata "chats.json"
python manage.py loaddata "messages.json"

COPY . /code/