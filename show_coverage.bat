if not defined in_subprocess (cmd /k set in_subprocess=y ^& %0 %*) & exit )
if not exist .venv (
virtualenv .venv)
if exist .coverage (
del /f .coverage)
if exist htmlcov (
rmdir /S /Q htmlcov)
cd .venv/Scripts && activate && cd ../.. && pip install -r requirements.txt && python manage.py makemigrations && python manage.py migrate && coverage run --omit=*/.venv*,*DokiApp/__init__.py*,*DokiApp/admin.py*,*DokiApp/apps.py*,*/manage.py*,*DokiApp/test*,*DokiDoki/settings.py*,*DokiDoki\urls.py*,*DokiApp/urls.py*,*DokiApp/migrations*,*DokiDoki/__init__.py* manage.py test && coverage report && coverage html && cd htmlcov && start index.html && exit