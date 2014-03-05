"""
WSGI config for neontool project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""
import sys
import os
sys.path.append('/home/yyl/projects/neontool')
sys.path.append('/home/yyl/.venv/python2.7/lib/python2.7/site-packages/django')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "neontool.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
