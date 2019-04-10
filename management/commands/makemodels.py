# -*- coding: utf-8 -*-
from __future__ import with_statement

from django.conf import settings
from django.core import management
from django.core.management.commands import inspectdb
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Creates models from all databases named in settings file (except default)'

    def handle(self, *args, **options):
        for k, v in settings.DATABASES.items():
            if 'default' is not k:  #maybe make this an option later
                db_name = v.get('NAME')
                management.call_command('inspectdb', '--database', db_name)