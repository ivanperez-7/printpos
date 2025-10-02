import threading as _threading


user_context = _threading.local()
""" Contexto de objeto Connection y objeto Usuario. """

user_context.token = None
user_context.is_admin = None
user_context.username = None
