pip install -r requirements.txt && python manage.py makemigrations && python manage.py migrate && python manage.py test && if %1.==. (
    python manage.py runserver
) else (
    python manage.py runserver %1
)