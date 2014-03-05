#/bin/bash

echo "Kill the gunicorn"
ps -ef|grep gunicorn |awk '{ print $2 }'|while read vari
do
       
        kill -9 $vari
done

