import os

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError(
        "TELEGRAM_BOT_TOKEN no definido. Ejecuta:\n"
        "export TELEGRAM_BOT_TOKEN='AIzaSyDmzqfTIwOuduJ8XTCPqLfWNTfJU47JNLY'"
    )
