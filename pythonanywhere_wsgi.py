"""WSGI file for PythonAnywhere.
Copy this file content into /var/www/anastasiaantipova_pythonanywhere_com_wsgi.py.
"""
import os
import sys

project_path = '/home/anastasiaantipova/reservation_service/backend'

if project_path not in sys.path:
    sys.path.insert(0, project_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reservation_service.settings')
os.environ.setdefault(
    'DJANGO_ALLOWED_HOSTS',
    'anastasiaantipova.pythonanywhere.com,localhost,127.0.0.1'
)

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
