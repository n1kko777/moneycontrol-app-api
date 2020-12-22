#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

if [ "$DEBUG" = "FALSE" ] 
then
  echo "run migrations and static"
  python manage.py migrate
  python manage.py collectstatic --no-input
fi

exec "$@"