#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    if sys.platform != "win32" and os.getuid() != 0:
        print("\033[91m[!] ERROR: NYX Framework must be run as root (sudo python manage.py runserver)\033[0m")
        sys.exit(1)
        
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nyx_dashboard.settings')
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
