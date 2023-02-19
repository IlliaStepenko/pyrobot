from django.contrib import admin

from botadminapp.models import WhiteList, SourceChats, TargetChats

admin.site.register(WhiteList)
admin.site.register(SourceChats)
admin.site.register(TargetChats)