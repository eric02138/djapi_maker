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
                serializers_content += "from {0}.models import {1}\n".format(db_name, class_name)
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
            views_content += "from rest_framework.views import APIView\n"
            views_content += "from rest_framework.response import Response\n"
            views_content += "from rest_framework.reverse import reverse\n"
            for class_name in self.class_names:
                views_content += "from {0}.serializers import {1}Serializer\n".format(db_name, class_name)
                views_content += "from {0}.models import {1}\n".format(db_name, class_name)
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
            views_content += "class ModelList(APIView):\n"
            views_content += "    def get(self, request, format=None):\n"
            views_content += "        model_list = []\n"
            for class_name in self.class_names:
                views_content += "        model = {\n"
                views_content += "            'model': '{0}',\n".format(class_name.lower())
                views_content += "            'url': reverse('{0}_list_view', request=request)\n".format(class_name.lower())
                views_content += "        }\n"
                views_content += "        model_list.append(model)\n"
            views_content += "        return Response(model_list)\n"
            views_content += "\n"
            f.write(views_content)
            print(f"Created views file: {self.views_path}")

    def make_urls(self, db_name):
        self.urls_path = os.path.join(self.target_dir, "urls.py")
        with open(self.urls_path, 'w') as f:
            urls_content = ""
            urls_content += "from django.urls import path\n"
            urls_content += "from rest_framework.urlpatterns import format_suffix_patterns\n"
            urls_content += "from {0} import views\n".format(db_name)
            urls_content += "\n"
            urls_content += "urlpatterns = [\n"
            urls_content += "    path('', views.ModelList.as_view(), name='model_list_view'),\n"
            for class_name in self.class_names:
                urls_content += "    path('{0}', views.{1}List.as_view(), name='{0}_list_view'),\n".format(class_name.lower(), class_name)
                urls_content += "    path('{0}/<int:pk>/', views.{1}Detail.as_view(), name='{0}_detail_view'),\n".format(class_name.lower(), class_name)
            urls_content += "]\n"
            urls_content += "\n"
            urls_content += "urlpatterns = format_suffix_patterns(urlpatterns)\n"
            urls_content += "\n"
            f.write(urls_content)
            print(f"Created urls file: {self.urls_path}")

    def make_routers(self, db_name):
        self.router_path = os.path.join(self.target_dir, "router.py")
        with open(self.router_path, 'w') as f:
            router_content = ""
            for class_name in self.class_names:
                router_content += "from {0}.models import {1}\n".format(db_name, class_name)
            router_content += "\n"
            router_content += "class Router(object):\n"
            router_content += "\tdef db_for_read(self, model, **hints):\n"
            router_content += "\t\tif model in [{0}]:\n".format(", ".join(self.class_names))
            router_content += "\t\t\treturn '{0}'\n".format(db_name)
            router_content += "\t\treturn None\n"
            router_content += "\n"
            router_content += "\tdef db_for_write(self, model, **hints):\n"
            router_content += "\t\tif model in [{0}]:\n".format(", ".join(self.class_names))
            router_content += "\t\t\treturn '{0}'\n".format(db_name)
            router_content += "\t\treturn None\n"
            router_content += "\n"
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
            views_content = ""
            views_content += "from rest_framework import generics\n"
            views_content += "from rest_framework.views import APIView\n"
            views_content += "from rest_framework.response import Response\n"
            views_content += "from rest_framework.reverse import reverse\n"
            views_content += "\n"
            views_content += "class AppList(APIView):\n"
            views_content += "    def get(self, request, format=None):\n"
            views_content += "        app_list = []\n"
            for db_name in db_names:
                views_content += "        app = {\n"
                views_content += "            'app_name': '{0}',\n".format(db_name)
                views_content += "            'url': '/api/{0}'\n".format(db_name) #reverse url this when I'm not so tired
                views_content += "        }\n"
                views_content += "        app_list.append(app)\n"
            views_content += "        return Response(app_list)\n"
            views_content += "\n"
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
            urls_content = ""
            urls_content += "from django.urls import path, include\n"
            for db_name in db_names:
                urls_content += "from {0} import urls as {0}_urls\n".format(db_name)
            urls_content += "from api import views\n"
            urls_content += "\n"
            urls_content += "urlpatterns = [\n"
            urls_content += "\tpath('', views.AppList.as_view(), name='app_list_view'),\n"
            for db_name in db_names:
                urls_content += "\tpath('{0}/', include({0}_urls)),\n".format(db_name)
            urls_content += "]\n"
            urls_content += "\n"
            f.write(urls_content)
            print(f"Created API urls file: {self.api_urls_path}")

    def display_install_instructions(self, db_names):
        print("")
        print("API Code generated Successfully!")
        print("*** However, you still need to add the apps and url routes to your project! ****")
        print("Here's what you need to do:")
        print("Step 1) Add new apps to Django's INSTALLED_APPS array.")
        print("  In your project's settings.py file, there should be something that looks like this:")
        print("")
        print("    INSTALLED_APPS = [")
        print("        'rest_framework',")
        print("        'django.contrib.admin',")
        print("        'django.contrib.auth',")
        print("        'django.contrib.contenttypes',")
        print("        'django.contrib.sessions',")
        print("        'django.contrib.messages',")
        print("        'django.contrib.staticfiles',")
        print("    ]")
        print("")
        print("  You need to add {0} to this list, like so:".format(", ".join(db_names)))
        print("")
        print("    INSTALLED_APPS = [")
        for db_name in db_names:
            print("        '{0}',".format(db_name))
        print("        'rest_framework',")
        print("        'django.contrib.admin',")
        print("        'django.contrib.auth',")
        print("        'django.contrib.contenttypes',")
        print("        'django.contrib.sessions',")
        print("        'django.contrib.messages',")
        print("        'django.contrib.staticfiles',")
        print("    ]")
        print("")
        print("Step 2) Add new routers to Django's DATABASE_ROUTERS tuple.")
        print("  Also in your project's settings.py file, you need to add a DATABASE_ROUTERS setting like so:")
        print("")
        print("    DATABASE_ROUTERS = (")
        for db_name in db_names:
            print("        '{0}.router.Router',".format(db_name))
        print("    )")
        print("")
        print("Step 3) Add API URLs to your project's main urls.py file.")
        print("  Your project's urls.py file should have something that looks like this:")
        print("")
        print("    urlpatterns = [")
        print("        path('admin/', admin.site.urls),")
        print("    ]")
        print("")
        print("  The API maker has created an \"api\" directory with a urls.py file in it with generated api urls.")
        print("  You need to include the \"api/urls.py\" in your project's urls.py file, like so: ")
        print("")
        print("    urlpatterns = [")
        print("        path('api/', include('api.urls'), name='api_urls'),")
        print("        path('admin/', admin.site.urls),")
        print("    ]")
        print("")
        print("Got to http://yourserver.name/api to view your api.")
        print("Enjoy!")
        print("")

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
