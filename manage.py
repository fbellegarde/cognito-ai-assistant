#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path


def main():
    """Run administrative tasks."""
    
    # --- CRITICAL FIX START ---
    # Explicitly add the base directory to the system path (where 'cognito_ai_assistant' lives) to ensure 
    # the main project module can be found during Docker build steps (like collectstatic).
    BASE_DIR = Path(__file__).resolve().parent
    sys.path.insert(0, str(BASE_DIR))
    # --- CRITICAL FIX END ---

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cognito_ai_assistant.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
