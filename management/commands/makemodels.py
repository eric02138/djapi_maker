# -*- coding: utf-8 -*-
from __future__ import with_statement

import os, re
from io import StringIO
from django.conf import settings
from django.core import management
#from django.core.management.commands import inspectdb
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Creates models from all databases named in settings file (except default)'

    def __init__(self):
        self.api_dir = os.path.join(settings.PROJ_DIR, "api")
        self.target_dir = None
        self.models_path = None
        self.apps_path = None
        self.views_path = None
        self.serializers_path = None
        self.urls_path = None
        self.urlpatterns_path = None
        self.class_names = []

    def make_api_dir(self):
        #make sure api module is present
        try:
            os.mkdir(self.api_dir)
        except FileExistsError:
            print(f"{self.api_dir} exists - continuing...")
        api_init = os.path.join(self.api_dir, "__init__.py")
        with open(api_init, 'a'):
            os.utime(api_init, None)

    def make_app(self, db_name):
        self.target_dir = os.path.join(self.api_dir, db_name)
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
            apps_content = ""
            apps_content += "from django.apps import AppConfig\n"
            apps_content += "\n"
            for class_name in self.class_names:
                apps_content += "class {0}Config(AppConfig):\n".format(class_name)
                apps_content += "    name = '{0}'\n".format(class_name.lower())
                apps_content += "    label = '{0} label'\n".format(class_name)
                apps_content += "\n"
            f.write(apps_content)
            print(f"Created apps config file: {self.apps_path}")


    def make_serializers(self, db_name):
        self.serializers_path = os.path.join(self.target_dir, "serializers.py")
        with open(self.serializers_path, 'w') as f:
            serializers_content = ""
            serializers_content += "from rest_framework import serializers\n"
            serializers_content += "\n"
            for class_name in self.class_names:
                serializers_content += "from .models import {0}\n".format(class_name)
            serializers_content += "\n"

            for class_name in self.class_names:
                serializers_content += "class {0}Serializer(serializers.ModelSerializer):\n".format(class_name)
                serializers_content += "    class Meta:\n"
                serializers_content += "        model = {0}\n".format(class_name)
                serializers_content += "        fields = '__all__'\n"
                serializers_content += "\n"
            f.write(serializers_content)
            print(f"Created serializers file: {self.serializers_path}")

    def make_views(self, db_name):
        self.views_path = os.path.join(self.target_dir, "views.py")
        with open(self.views_path, 'w') as f:
            views_content = ""
            views_content += "from rest_framework import generics\n"
            for class_name in self.class_names:
                views_content += "from .serializers import {0}Serializer\n".format(class_name)
                views_content += "from .models import {1}\n".format(class_name.lower(), class_name)
            views_content += "\n"
            for class_name in self.class_names:
                views_content += "class {0}List(generics.ListCreateAPIView):\n".format(class_name)
                views_content += "    queryset = {0}.objects.all()\n".format(class_name)
                views_content += "    serializer_class = {0}Serializer\n".format(class_name)
                views_content += "\n"
                views_content += "class {0}Detail(generics.RetrieveUpdateDestroyAPIView):\n".format(class_name)
                views_content += "    queryset = {0}.objects.all()\n".format(class_name)
                views_content += "    serializer_class = {0}Serializer\n".format(class_name)
                views_content += "\n"
            f.write(views_content)
            print(f"Created views file: {self.views_path}")

    def make_urls(self, db_name):
        self.urls_path = os.path.join(self.target_dir, "urls.py")
        with open(self.urls_path, 'w') as f:
            urls_content = ""
            urls_content += "from django.urls import path\n"
            urls_content += "from rest_framework.urlpatterns import format_suffix_patterns\n"
            urls_content += "from . import views\n"
            urls_content += "\n"
            urls_content += "urlpatterns = [\n"
            for class_name in self.class_names:
                urls_content += "    path('', views.{0}List.as_view()),\n".format(class_name)
                urls_content += "    path('<int:pk>/', views.{0}Detail.as_view()),\n".format(class_name)
            urls_content += "]\n"
            urls_content += "\n"
            urls_content += "urlpatterns = format_suffix_patterns(urlpatterns)\n"
            urls_content += "\n"
            f.write(urls_content)
            print(f"Created urls file: {self.urls_path}")

    def make_url_patterns(self, db_name):
        self.urlpatterns_path = os.path.join(self.target_dir, "urlpatterns.py")
        with open(self.urlpatterns_path, 'w') as f:
            patterns_content = ""
            patterns_content += "#You will need to add the following url pattern to your main urls.py file.\n"
            patterns_content += "path('api/{0}/', include('api.{0}.urls'), name='_api')\n".format(db_name)

    def handle(self, *args, **options):
        self.make_api_dir()

        for k, v in settings.DATABASES.items():
            if 'default' is not k:  #maybe make this an option later
                db_name = v.get('NAME')
                self.make_app(db_name)
                self.make_models(db_name)
                self.make_app_config(db_name)
                self.make_serializers(db_name)
                self.make_views(db_name)
                self.make_urls(db_name)
                #super().handle('app', db_name, target_dir, **options)
