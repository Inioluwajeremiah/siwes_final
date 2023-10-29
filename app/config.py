import os

class Config:
    # Secret Key
    SECRET_KEY = os.environ.get('SECRET_KEY') 
    # PostgreSQL Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') 
    SQLALCHEMY_TRACK_MODIFICATIONS = False