# manage.py
import os
import sys
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    env_type = os.getenv("DJANGO_ENV", "dev")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"config.settings.{env_type}")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed?"
        ) from exc
    execute_from_command_line(sys.argv)
