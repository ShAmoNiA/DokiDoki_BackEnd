if not defined in_subprocess (cmd /k set in_subprocess=y ^& %0 %*) & exit )
if exist .coverage (
del /f .coverage)
if exist htmlcov (
rmdir /S /Q htmlcov)
coverage run --omit=*/venv*,*DokiApp/__init__.py*,*DokiApp/admin.py*,*DokiApp/apps.py*,*/manage.py*,*DokiApp/test*,*DokiDoki/settings.py*,*DokiDoki\urls.py*,*DokiApp/urls.py*,*DokiApp/migrations*,*DokiDoki/__init__.py* manage.py test && coverage report && coverage html && if exist htmlcov (
cd htmlcov)
start index.html