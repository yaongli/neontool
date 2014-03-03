#!/usr/bin/env python
# coding: utf-8

from django.db import models

class CvsHistory(models.Model):
    id = models.IntegerField(primary_key=True)
    branch = models.CharField(max_length=384)
    updatetime = models.DateTimeField(null=True, db_column='updateTime', blank=True) # Field name made lowercase.
    file = models.CharField(max_length=768)
    author = models.CharField(max_length=384)
    revision = models.CharField(max_length=384)
    action = models.CharField(max_length=60)
    comment = models.CharField(max_length=3072)
    jira = models.CharField(max_length=384, blank=True)
    linesadd = models.IntegerField(null=True, db_column='linesAdd', blank=True) # Field name made lowercase.
    linesremove = models.IntegerField(null=True, db_column='linesRemove', blank=True) # Field name made lowercase.

    class Meta:
        db_table = u'cvs_history'
        ordering = ['-updatetime']

    def __unicode__(self):
        line = str(self.id) + "\t" + self.file + "\t" + self.author + "\t" + str(self.jira)
        return line
