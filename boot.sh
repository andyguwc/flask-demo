#!/bin/bash
# this script is used to boot a Docker container
while true; do
    flask deploy
    if [[ "$?" == "0" ]]; then
        break
    fi
    echo Deploy command failed, retrying in 5 secs...
    sleep 5
done

# gunicorn enable --reload if in development mode
if [ "${FLASK_CONFIG}" == "development" ]
then 
    exec gunicorn -b :5000 --access-logfile - --reload --error-logfile - run:app
else
    exec gunicorn -b :5000 --access-logfile - --error-logfile - run:app
fi 