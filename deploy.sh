#!/bin/sh

ssh -o StrictHostKeyChecking=no tesla << 'ENDSSH'
    echo '---------------> deploying teslatify'
    su -s /bin/bash www-data
    cd /var/www/tesla/
    source virtualenv/bin/activate
    cd application
    pip install --upgrade pip
    git pull origin main
    # pip install -r requirements.txt
    python manage.py migrate
    python manage.py collectstatic --noinput
    echo 'restart app'
    cd /var/www/tesla/application/conf/
    touch uwsgi.ini
    echo 'done'

ENDSSH

