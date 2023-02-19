from django.contrib import admin

from botadminapp.models import WhiteList, SourceChats, TargetChats, BotConfig


class BaseChatAdmin(admin.ModelAdmin):
    list_display = ('chat_id', 'name', 'active', 'tg_link')


@admin.register(WhiteList)
class WhiteListAdmin(admin.ModelAdmin):
    list_display = ('url',)


@admin.register(SourceChats)
class SourceChatAdmin(BaseChatAdmin):
    pass


@admin.register(TargetChats)
class TargetChatsAdmin(BaseChatAdmin):
    pass


@admin.register(BotConfig)
class BotConfigAdmin(admin.ModelAdmin):
    list_display = ('name',)
