from importlib import import_module
from app import app
acl = import_module(app.config['AUTH_BACKEND'])
