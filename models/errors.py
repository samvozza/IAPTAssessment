from gluon.rewrite import THREAD_LOCAL as rwthread
rwthread.routes.routes_onerror = [(r'*/*', URL('default', 'error_handler')),]

class EX(HTTP):
    def __init__(self, status, message=None):
        HTTP.__init__(self, status)
        session.error_message = message
