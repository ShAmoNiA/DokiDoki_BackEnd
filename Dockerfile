FROM python:latest

WORKDIR /DokiDoki

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip setuptools wheel
RUN pip3 install -r requirements.txt

COPY . .

CMD ["python3", "manage.py", "runserver", "0.0.0.0:1111"]