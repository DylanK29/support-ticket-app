#Flask Configuration Module
#Loads settings from environment variables with fallback defaults

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent #Base directory of the project

class Config: #Base configuration class
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production') #Secret key for session management and CSRF protection
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f'sqlite:///{BASE_DIR / "app.db"}'
    ) #SQLAchemy Database URI

    SQLALCHEMY_TRACK_MODIFICATIONS = False #Disable track modifications to save resources

class DevelopmentConfig(Config): #Development configuration
    DEBUG = True #Enable debug mode for development

class ProductionConfig(Config): #Production configuration
    DEBUG = False #Disable debug mode for production

    @property
    def SECRET_KEY(self):
        #Ensure SECRET_KEY is set in production
        secret = os.environ.get('SECRET_KEY')
        if not secret:
            raise ValueError("SECRET_KEY environment variable must be set in production")
        return secret
    
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        #Handle Render's postgres:// vs postgresql://
        database_url = os.environ.get('DATABASE_URL')
        if database_url and database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        return database_url

class TestingConfig(Config): #Testing configuration
    TESTING = True #Enable testing mode
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' #Use in-memory database for testing

#Configuration dictionary for easy access
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}