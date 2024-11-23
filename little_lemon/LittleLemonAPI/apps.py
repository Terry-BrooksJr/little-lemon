from django.apps import AppConfig


class LittlelemonapiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "LittleLemonAPI"

    def ready(self) -> None:
        import little_lemon.utils.cache  # noqa
