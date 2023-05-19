#!/bin/sh

ssh -o StrictHostKeyChecking=no ksafe << 'ENDSSH'
    echo '---------------> deploying ksafe'
    su -s /bin/bash www-data
    cd /var/www/ksafe/
    source virtualenv/bin/activate
    cd application
    pip install --upgrade pip
    git pull origin main
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py collectstatic --noinput
    echo 'restart app'
    cd /var/www/ksafe/application/conf/
    touch uwsgi.ini
    echo 'done'

ENDSSH

