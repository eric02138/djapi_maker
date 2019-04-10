# -*- coding: utf-8 -*-
from __future__ import with_statement

import os, sys
from django.conf import settings
from django.core import management
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Creates api module directory and files'

    def handle(self, *args, **options):
        project_dir = settings.PROJ_DIR
        api_dir = os.path.join(project_dir, "api")
        try:
            os.mkdir(api_dir)
        except FileExistsError:
            print(f"{api_dir} exists - continuing...")
        api_init = os.path.join(api_dir, "__init__.py")
        with open(api_init, 'a'):
            os.utime(api_init, None)

