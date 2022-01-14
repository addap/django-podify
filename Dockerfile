# from https://www.caktusgroup.com/blog/2017/03/14/production-ready-dockerfile-your-python-django-app/
# and https://testdriven.io/blog/dockerizing-django-with-postgres-gunicorn-and-nginx/
FROM python:3.8-slim as builder


# Copy your application code to the container (make sure you create a .dockerignore file if any large files or directories should be excluded)
RUN mkdir /code/
WORKDIR /code/

# Copy in your requirements file
COPY requirements.txt ./requirements.txt

# Install build deps, then run `pip install`, then remove unneeded build deps all in a single step.
# Correct the path to your production requirements file, if needed.
RUN set -ex \
    && BUILD_DEPS=" \
    git \
    build-essential \
    libpcre3-dev \
    libpq-dev \
    " \
    && apt-get update \
    && apt-get install -y --no-install-recommends $BUILD_DEPS \
    && pip wheel --no-cache-dir --wheel-dir ./wheels/ -r ./requirements.txt \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false $BUILD_DEPS \
    && rm -rf /var/lib/apt/lists/*


FROM python:3.8-slim

# Install packages needed to run your application (not build deps):
#   mime-support -- for mime types when serving static files
#   postgresql-client -- for running database commands
# We need to recreate the /usr/share/man/man{1..8} directories first because
# they were clobbered by a parent image.
RUN set -ex \
    && RUN_DEPS=" \
    libpcre3 \
    mime-support \
    ffmpeg \
    redis-tools \
    " \
#    && seq 1 8 | xargs -I{} mkdir -p /usr/share/man/man{} \
    && apt-get update && apt-get install -y --no-install-recommends $RUN_DEPS \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /code/ /code/db/ /code/media/
WORKDIR /code/

# Create a group and user to run our app.
# also create home because ytdl wants to write cache files there
ARG APP_USER=appuser
RUN groupadd -r ${APP_USER} && useradd --no-log-init -m -r -g ${APP_USER} ${APP_USER}

COPY --from=builder /code/wheels ./wheels
COPY --from=builder /code/requirements.txt .
RUN pip install --no-cache ./wheels/*

COPY . .

# Call collectstatic (customize the following line with the minimal environment variables needed for manage.py to run):
RUN SECRET_KEY='a' ALLOWED_HOSTS='' REDIS_URL='' API_KEY='' python manage.py collectstatic --noinput
#RUN SECRET_KEY='a' ALLOWED_HOSTS='' REDIS_URL='' API_KEY='' python manage.py migrate --noinput

# uWSGI will listen on this port
EXPOSE 8000

# Add any static environment variables needed by Django or your settings file here:
# Base uWSGI configuration (you shouldn't need to change these):
# Number of uWSGI workers and threads per worker (customize as needed):
# uWSGI static file serving configuration (customize or comment out if not needed):
# Tell uWSGI where to find your wsgi file (change this):
ENV DJANGO_SETTINGS_MODULE=podify.settings \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UWSGI_WSGI_FILE=podify/wsgi.py \
    UWSGI_HTTP=:8000 \
    UWSGI_MASTER=1 \
    UWSGI_HTTP_AUTO_CHUNKED=1 \
    UWSGI_HTTP_KEEPALIVE=1 \
    UWSGI_LAZY_APPS=1 \
    UWSGI_WSGI_ENV_BEHAVIOR=holy \
    UWSGI_WORKERS=2 \
    UWSGI_THREADS=4 \
    UWSGI_STATIC_EXPIRES_URI="/static/.*\.[a-f0-9]{12,}\.(css|js|png|jpg|jpeg|gif|ico|woff|ttf|otf|svg|scss|map|txt) 315360000"

# Deny invalid hosts before they get to Django (uncomment and change to your hostname(s)):
# ENV UWSGI_ROUTE_HOST="^(?!localhost:8000$) break:400"

RUN chown -R ${APP_USER}:${APP_USER} /code

# Change to a non-root user
USER ${APP_USER}:${APP_USER}

# Uncomment after creating your docker-entrypoint.sh
ENTRYPOINT ["/code/docker-entrypoint.sh"]

# Start uWSGI
CMD ["uwsgi", "--show-config", "--static-map" , "/static/=/code/static", "--static-map", "/media/=/code/media"]