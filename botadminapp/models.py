from django.db import models


class SourceChats(models.Model):
    chat_id = models.BigIntegerField()
    name = models.CharField(max_length=50)
    active = models.BooleanField(blank=True, null=True)
    tg_link = models.CharField(max_length=1000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'SourceChats'


class TargetChats(models.Model):
    chat_id = models.BigIntegerField()
    name = models.CharField(max_length=50)
    active = models.BooleanField(blank=True, null=True)
    tg_link = models.CharField(max_length=1000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TargetChats'


class WhiteList(models.Model):
    id = models.IntegerField(primary_key=True)
    url = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'WhiteList'


class BotConfig(models.Model):
    name = models.CharField(max_length=15, unique=True, default='MAIN_CONFIG')
    default_lang_code = models.CharField(max_length=5, default='ru')
    used_languages = models.CharField(max_length=500, default="en, ru, pl, uk, de, it")
    ask_open_ai = models.BooleanField(default=False)
    abuser_on = models.BooleanField(default=False)
    autotranslate = models.BooleanField(default=False)
    autotranslate_lang = models.CharField(default='en', max_length=5)

    class Meta:
        db_table = 'BotConfig'