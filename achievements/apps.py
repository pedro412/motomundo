from django.apps import AppConfig


from django.apps import AppConfig


class AchievementsConfig(AppConfig):
    """
    Achievement system app configuration
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'achievements'
    
    def ready(self):
        """
        Import signal handlers when Django starts
        """
        # Import signals to register them
        try:
            import achievements.signals
        except ImportError:
            pass
