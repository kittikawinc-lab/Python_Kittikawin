"""Public sender identity; the App Password stays in the environment."""
import os
SENDER='exoraadmin@gmail.com'
def password():return os.getenv('EXORA_GMAIL_APP_PASSWORD','').replace(' ','')
def configured():return bool(password())
