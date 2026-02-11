import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-insecure-key')
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///dev.db')
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_DURATION = timedelta(days=14)
    SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT', 'change-me')
    RATE_LIMIT_GLOBAL = os.getenv('RATE_LIMIT_GLOBAL', '200 per hour')
    RATE_LIMIT_LOGIN = os.getenv('RATE_LIMIT_LOGIN', '10 per 5 minute')
    MAILERSEND_API_KEY = os.getenv('MAILERSEND_API_KEY')
    MAIL_FROM_NAME = 'UrbanMood'
    MAIL_FROM_EMAIL = 'noreply@urbanmood.net'

config = Config()
