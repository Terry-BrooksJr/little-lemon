from django.apps import AppConfig
from django.db import connection
from LittleLemonAPI.metrics import database_execute_wrapper
class LittlelemonapiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "LittleLemonAPI"

    def ready(self) -> None:
        import little_lemon.utils.cache #noqa
        connection.execute_wrapper(database_execute_wrapper)

        
