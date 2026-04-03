#Flask Configuration Module

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

def get_database_url():
    #Get database URL, fixing Render's postgres:// prefix
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        return database_url
    return f'sqlite:///{BASE_DIR / "app.db"}'

class Config:
    #Base configuration class
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = get_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    #Development configuration
    DEBUG = True

class ProductionConfig(Config):
    #Production configuration
    DEBUG = False

class TestingConfig(Config):
    #Testing configuration
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

#Configuration dictionary for easy access
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}