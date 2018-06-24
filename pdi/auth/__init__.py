from importlib import import_module
from settings import AUTH_BACKEND
acl = import_module(AUTH_BACKEND)
