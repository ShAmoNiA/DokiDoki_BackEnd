if not defined in_subprocess (cmd /k set in_subprocess=y ^& %0 %*) & exit )
if not exist .venv (
virtualenv .venv)
cd .venv/Scripts && activate && cd ../.. && pip install -r requirements.txt && python manage.py makemigrations && python manage.py migrate && python manage.py test && if %1.==. (
    python manage.py runserver
) else (
    python manage.py runserver %1
)