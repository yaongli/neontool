#!/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import time
import subprocess
import logging
import re
import MySQLdb

ROOT_FOLDER=r"D:\workspace\neon"
HISTORY_PATH_PREFIX=r"neon/"

os.chdir(ROOT_FOLDER)

def initlog():
    logger = logging.getLogger()
    #hdlr = logging.FileHandler(logfile)
    hdlr = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.DEBUG)
    
    return logger
logger = initlog()

def current_path():
    with open("CVS\Repository") as f:
        path = f.read().strip()
        print "--" + path + "--"

def cvs_history(lastUpdateTime):
    folder = os.path.abspath(os.curdir)
    cmd = "cvs history -c -a -w -z +0800 -D \"%s\"" % (lastUpdateTime)
    logger.debug(cmd)
    pipe = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell=True)
    out, err = pipe.communicate()
    logger.debug("out=" + out)
    if err is not None and len(err) > 0:
        logger.error(err)
    lines = re.split(r"[\n\r,]+", out)
    histories = []
    for line in lines:
        if len(line.strip()) == 0:
            continue
        parts = re.split(r"\s+", line)
        if len(parts) < 8:
            continue
        #for index, part in enumerate(parts):
        #    print index, ":", part
        """
        0 ---- M
        1 ---- 2013-06-19
        2 ---- 02:24
        3 ---- +0000
        4 ---- yangyongli
        5 ---- 1.158
        6 ---- CommunicationManager.java
        7 ---- neon/src/java/com/z2/np/server/manager/communication
        8 ---- ==
        9 ---- <remote>
        """
        history = {}
        history["action"] = parts[0]
        history["date"] = parts[1]
        history["time"] = parts[2]
        history["updateTime"] = history["date"] + " " + history["time"]
        history["author"] = parts[4]
        history["revision"] = parts[5]
        history["filename"] = parts[6]
        history["filepath"] = parts[7]
        history["relpath"] = history["filepath"][len(HISTORY_PATH_PREFIX):] + "/" + history["filename"]
        histories.append(history)
    return histories

def cvs_log(history):
    revision = history["revision"]
    file = history["relpath"]
    cmd = "cvs log -r%s %s" % (revision, file)
    logger.debug(cmd)
    pipe = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell=True)
    out, err = pipe.communicate()
    if err is not None and len(err) > 0:
        logger.error(err)
    lines = re.split(r"[\n\r,]+", out)
    descriptions = []
    start_description = False
    lastline = ""
    count = 0
    for line in lines:
        if start_description:
            count += 1
            if count <= 2:
                continue
            if line.startswith("=================================="):
                break
            descriptions.append(line)
            continue
        if lastline == "description:" and line == "----------------------------":
            start_description = True
            continue
        lastline = line.strip()
    
    description = " ".join(descriptions)
    logger.debug(description)
    history['description'] = description
    return description

def recordHistoryToDB():
    # Open database connection
    db = MySQLdb.connect(user='root', db='cvs_history', passwd='justdoit', host='localhost')
    # prepare a cursor object using cursor() method
    cursor = db.cursor()
    
    startTimeSql = "select DATE_SUB(DATE_ADD(max(updateTime), INTERVAL 1 MINUTE), INTERVAL 8 HOUR) as LAST_UPDATE_DATE from cvs_history"
    cursor.execute(startTimeSql)
    lastTime = cursor.fetchone()
    logger.info("lastUpdateTime = %s" % lastTime)

    if lastTime and len(lastTime) > 0 and None != lastTime[0]:
        lastUpdateTime = lastTime[0].strftime("%Y-%m-%d %H:%M:%S")
    else:
        lastUpdateTime = "2014-01-01 00:00:00"
    print lastUpdateTime
    insertSqlTemplate = """INSERT INTO cvs_history ( branch, updateTime, file, author, revision, action, comment, jira, linesAdd, linesRemove )
    VALUES ( 'trunk', '%(updateTime)s', '%(file)s', '%(author)s', '%(revision)s', '%(action)s', '%(comment)s', '%(jira)s', 0, 0 )""";
    
    histories = cvs_history(lastUpdateTime)
    log_groups = {}
    for history in histories:
        history["file"] = history["relpath"]
        print history["file"]
        cvs_log(history)
        description = history['description']
        jira = ""
        jiraNoList = re.findall(r'((WORK-\d+)|(DEV-\d+)|(IDEA-\d+))', description, flags=re.IGNORECASE|re.MULTILINE)
        if len(jiraNoList) > 0:
            jira = jiraNoList[0][0]
        history['jira'] = jira
        comment = db.escape_string(description)
        history['comment'] = comment
        sql = insertSqlTemplate % history
        try:
           # Execute the SQL command
           cursor.execute(sql)

           # Update jira table
           if jira is not None and jira != '':
               sql = "select id, name, author, comment, firstUpdate, lastUpdate from jira where name='%s'" % (jira,)
               cursor.execute(sql)
               jira_record = cursor.fetchone()
               if None == jira_record:
                   sql = """insert into jira (name, author, comment, firstUpdate, lastUpdate)
                   values ('%(jira)s', '%(author)s', '%(comment)s', '%(updateTime)s', '%(updateTime)s')""" % history
                   cursor.execute(sql)
               else:
                   author = jira_record[2]
                   if history['author'] not in author.split(","):
                       author = author + "," + history['author']
                   comment = jira_record[3]
                   #logger.debug("comment=[" + comment + "]")
                   #logger.debug("history['comment']=" + history['comment'])
                   if history['comment'] not in comment.split("<br/>"):
                       #logger.debug("comment.split(\"<br/>\")=" + comment.split("<br/>"))
                       comment = comment + "<br/>" + history['comment']
                   sql = """update jira set author='%s', comment='%s', lastUpdate='%s' where name='%s' """ % (author, comment, history['updateTime'], jira)
                   cursor.execute(sql)
           # Commit your changes in the database
           db.commit()
        except Exception, e:
            # Rollback in case there is any error
            db.rollback()
            print e
            logger.error("[ERROR] Failed to execute: " + sql + "\n" + str(e))

    # disconnect from server
    db.close()
    print "================================="
    print "Complete"
    print "================================="


if __name__ == "__main__":
    recordHistoryToDB()


"""
drop table cvs_history;

CREATE TABLE
    cvs_history
    (
        id INT NOT NULL AUTO_INCREMENT,
        branch VARCHAR(128) NOT NULL,
        updateTime DATETIME,
        file VARCHAR(255) NOT NULL,
        author VARCHAR(128) NOT NULL,
        revision VARCHAR(128) NOT NULL,
        action VARCHAR(20) NOT NULL,
        COMMENT VARCHAR(1024) NOT NULL,
        jira VARCHAR(128),
        linesAdd INT DEFAULT '0',
        linesRemove INT DEFAULT '0',
        PRIMARY KEY (id),
        INDEX author (author),
        INDEX file (file),
        INDEX updateTime (updateTime),
        INDEX branch (branch),
        INDEX jira (jira)
    )
    ENGINE=InnoDB DEFAULT CHARSET=utf8;


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
"""