from django.contrib import admin

from .models import Device

class DeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'created')

admin.site.register(Device, DeviceAdmin)