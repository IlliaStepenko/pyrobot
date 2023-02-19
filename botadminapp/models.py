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

