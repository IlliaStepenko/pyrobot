from django.contrib import admin

from adm.models import Sourcechats, Targetchats, Whitelist

# Register your models here.

admin.site.register(Sourcechats)
admin.site.register(Targetchats)
admin.site.register(Whitelist)