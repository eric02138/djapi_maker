# -*- coding: utf-8 -*-
from __future__ import with_statement

import os, re
from io import StringIO
from django.conf import settings
from django.core import management
from django.template.loader import render_to_string, get_template
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Creates models from all databases named in settings file (except default)'

    def __init__(self):
        self.proj_dir = settings.PROJ_DIR
        self.api_dir = os.path.join(settings.PROJ_DIR, "api")
        self.target_dir = None
        self.models_path = None
        self.apps_path = None
        self.views_path = None
        self.serializers_path = None
        self.urls_path = None
        self.urlpatterns_path = None
        self.router_path = None
        self.api_urls_path = None
        self.api_views_path = None
        self.class_names = []

    def add_arguments(self, parser):
        parser.add_argument('--include_default_db', action='store_true')

    def make_app(self, db_name):
        self.target_dir = os.path.join(self.proj_dir, db_name)
        try:
            os.mkdir(self.target_dir)
            print(f"{self.target_dir} created.")
        except FileExistsError:
            print(f"{self.target_dir} exists - continuing...")
        app_init = os.path.join(self.target_dir, "__init__.py")
        with open(app_init, 'a'):
            os.utime(app_init, None)

    def make_models(self, db_name):
        self.model_path = os.path.join(self.target_dir, "models.py")
        out = StringIO()
        management.call_command('inspectdb', '--database', db_name, stdout=out)
        lines = out.getvalue().split('\n')
        inspectdb_output = ""
        self.class_names = []             #just in case we're on our nth database
        for line in lines:
            if not line.startswith("#"):
                inspectdb_output += f"{line}\n"
            #set class names
            exp = r"class\s+(.*)\("
            match = re.search(exp, line)
            if match:
                self.class_names.append(match.group(1))
        with open(self.model_path, 'w') as f:
            os.utime(self.model_path, None)
            f.write(inspectdb_output)
            print(f"Created models file: {self.model_path}")

    def make_app_config(self, db_name):
        self.apps_path = os.path.join(self.target_dir, "apps.py")
        with open(self.apps_path, 'w') as f:
            apps_content = render_to_string('make_app_config.txt', {'db_name': db_name,
                                                                    'class_names': self.class_names})
            f.write(apps_content)
            print(f"Created apps config file: {self.apps_path}")


    def make_serializers(self, db_name):
        self.serializers_path = os.path.join(self.target_dir, "serializers.py")
        with open(self.serializers_path, 'w') as f:
            serializers_content = render_to_string('make_serializers.txt', {'db_name': db_name,
                                                                            'class_names': self.class_names})
            f.write(serializers_content)
            print(f"Created serializers file: {self.serializers_path}")

    def make_views(self, db_name):
        self.views_path = os.path.join(self.target_dir, "views.py")
        with open(self.views_path, 'w') as f:
            views_content = render_to_string('make_views.txt', {'db_name': db_name,
                                                                'class_names': self.class_names})
            f.write(views_content)
            print(f"Created views file: {self.views_path}")

    def make_urls(self, db_name):
        self.urls_path = os.path.join(self.target_dir, "urls.py")
        with open(self.urls_path, 'w') as f:
            urls_content = render_to_string('make_urls.txt', {'db_name': db_name,
                                                              'class_names': self.class_names})
            f.write(urls_content)
            print(f"Created urls file: {self.urls_path}")

    def make_routers(self, db_name):
        self.router_path = os.path.join(self.target_dir, "router.py")
        with open(self.router_path, 'w') as f:
            class_names_string = [ str(class_name) for class_name in class_names ]
            router_content = render_to_string('make_routers.txt', {'db_name': db_name,
                                                                   'class_names': self.class_names,
                                                                   'class_names_string': class_names_string})
            f.write(router_content)
            print(f"Created db router file: {self.router_path}")

    def make_api_views(self, db_names):
        try:
            os.mkdir(self.api_dir)
        except FileExistsError:
            print(f"{self.api_dir} exists - continuing...")
        api_init = os.path.join(self.api_dir, "__init__.py")
        with open(api_init, 'a'):
            os.utime(api_init, None)
        self.api_views_path = os.path.join(self.api_dir, "views.py")
        with open(self.api_views_path, 'w') as f:
            views_content = render_to_string('make_api_views.txt', {'db_names': db_names})
            f.write(views_content)
            print(f"Created api views file: {self.api_views_path}")

    def make_api_urls(self, db_names):
        #make sure api module is present
        try:
            os.mkdir(self.api_dir)
        except FileExistsError:
            print(f"{self.api_dir} exists - continuing...")
        api_init = os.path.join(self.api_dir, "__init__.py")
        with open(api_init, 'a'):
            os.utime(api_init, None)
        self.api_urls_path = os.path.join(self.api_dir, "urls.py")
        with open(self.api_urls_path, 'w') as f:
            urls_content = render_to_string('make_api_urls.txt', {'db_names': db_names})
            f.write(urls_content)
            print(f"Created API urls file: {self.api_urls_path}")

    def display_install_instructions(self, db_names):
        install_instructions = render_to_string("install_instructions.txt", {'db_names': db_names})
        print(install_instructions)

    def handle(self, *args, **options):
        dbs = settings.DATABASES
        #By default, exclude the default db.
        if not options['include_default_db']:
            try:
                dbs.pop('default')
            except KeyError:
                print('No default database found.')

        for key in dbs.keys():
            db_name = key
            self.make_app(db_name)
            self.make_models(db_name)
            self.make_app_config(db_name)
            self.make_serializers(db_name)
            self.make_views(db_name)
            self.make_urls(db_name)
            self.make_routers(db_name)
        self.make_api_views(dbs.keys())
        self.make_api_urls(dbs.keys())
        self.display_install_instructions(list(dbs.keys()))
