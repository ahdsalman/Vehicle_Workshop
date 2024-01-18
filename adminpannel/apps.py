from django.apps import AppConfig


class AdminpannelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'adminpannel'

    def ready(self):
        import adminpannel.signals




    