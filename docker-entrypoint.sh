#!/bin/sh
set -e

echo `whoami`

until redis-cli -u $REDIS_URL ping; do
    >&2 echo "Redis is unavailable - sleeping"
    sleep 1
done

>&2 echo "Redis is up - continuing"

if [ "x$DJANGO_MANAGEPY_MIGRATE" = "xon" ]; then
    python manage.py migrate --noinput
fi

python manage.py qcluster &

exec "$@"
