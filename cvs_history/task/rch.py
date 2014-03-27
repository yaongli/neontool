# -*- coding:utf-8 -*-
"""
Refresh CVS history
Run cvs history db every minite
"""
import cvs_history_db
import time

while True:
    cvs_history_db.recordHistoryToDB()
    time.sleep(60 * 1)
