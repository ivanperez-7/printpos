import threading as _threading


user_context = _threading.local()
""" Contexto de objeto Connection y objeto Usuario. """

user_context.conn = None
user_context.user = None
