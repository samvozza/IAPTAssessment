from gluon.rewrite import THREAD_LOCAL as rwthread
rwthread.routes.routes_onerror = [(r'*/*', URL('default', 'error_handler')),]