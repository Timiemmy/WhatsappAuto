from django.apps import AppConfig
import sys


class SchedulerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scheduler'

    def ready(self):
        # Import here to avoid circular import
        from . import scheduler_service

        # Only start scheduler if this is the main process
        # This prevents it from starting twice when using Django's auto-reloader
        if not any('runserver' in arg for arg in sys.argv):
            return

        # Start the scheduler
        scheduler_service.start()
