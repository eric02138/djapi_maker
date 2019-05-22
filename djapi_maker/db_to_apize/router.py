from db_to_apize.models import Authors
from db_to_apize.models import Posts


class Router(object):
    def db_for_read(self, model, **hints):
        if model.__name__ in ['Authors', 'Posts']:
            return 'db_to_apize'
        return None

    def db_for_write(self, model, **hints):
        if model.__name__ in ['Authors', 'Posts']:
            return 'db_to_apize'
        return None

