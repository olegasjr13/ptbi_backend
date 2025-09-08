import os
from dotenv import load_dotenv

from django.core.asgi import get_asgi_application
load_dotenv()
env_type = os.getenv("DJANGO_ENV", "dev")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"config.settings.{env_type}")

application = get_asgi_application()
