if not defined in_subprocess (cmd /k set in_subprocess=y ^& %0 %*) & exit )
coverage run --omit=*/venv*,*DokiApp/__init__.py*,*DokiApp/admin.py*,*DokiApp/apps.py*,*/manage.py*,*DokiApp/test*,*DokiDoki/settings.py*,*DokiDoki\urls.py*,*DokiApp/urls.py*,*DokiApp/migrations*,*DokiDoki/__init__.py* manage.py test && coverage report && coverage html