import os
from dotenv import load_dotenv

from django.core.wsgi import get_wsgi_application
load_dotenv()
env_type = os.getenv("DJANGO_ENV", "dev")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"config.settings.{env_type}")


application = get_wsgi_application()

