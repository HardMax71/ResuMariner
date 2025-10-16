from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    verbose_name = "Core Services"

    def ready(self):
        import backend.checks  # noqa: F401 - Register system checks
