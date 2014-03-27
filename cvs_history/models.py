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

class Engineer(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=384)
    nick_name = models.CharField(max_length=384 ,null=True, blank=True)
    cvs_name = models.CharField(max_length=384)
    email = models.EmailField(null=True, blank=True)

    class Meta:
        db_table = u'engineer'

    def __unicode__(self):
        return self.name



"""
drop table jira;

CREATE TABLE
    jira
    (
        id INT NOT NULL AUTO_INCREMENT,
        name VARCHAR(384) NOT NULL,
        COMMENT VARCHAR(3072) NOT NULL,
        author VARCHAR(384) NOT NULL,
        firstUpdate DATETIME,
        lastUpdate DATETIME,
        PRIMARY KEY (id)
    )
    ENGINE=InnoDB DEFAULT CHARSET=utf8;

insert into jira (name, author, comment, firstUpdate, lastUpdate)
 select jira as name, group_concat(distinct author) as author, comment, min(updateTime) as firstUpdate, max(updateTime) as lastUpdate
 from cvs_history group by jira order by max(updateTime);
"""

class Jira(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=384)
    comment = models.CharField(max_length=3072)
    author = models.CharField(max_length=384)
    first_update = models.DateTimeField(null=True, db_column='firstUpdate', blank=True)
    last_update = models.DateTimeField(null=True, db_column='lastUpdate', blank=True)

    class Meta:
        db_table = u'jira'
        ordering = ['-last_update']

    def __unicode__(self):
        return self.name
