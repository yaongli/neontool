neontool
========

Tools for neon


Create
Create a mysql user for cvs_history

    create user 'cvs_history'@'localhost' identified by 'cvs_history';
    GRANT ALL PRIVILEGES ON cvs_history.* TO 'cvs_history'@'localhost';

