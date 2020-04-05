# Podify

This django application turns youtube playlists into podcast RSS feeds. It downloads and then serves them, 
in the future I might do lazy downloading. You can use the docker-compose file to host it.

## Usage

Go to localhost:8000 to see a listing of all podcasts.
To add a podcast you need a name and an optional playlist.
A django-q scheduled action will sync all podcasts once a day.
To sync manually press sync on the podcast's detail page.
On the detail page you can also manually upload mp3s that get added to the podcast.

## Deployment

write a .env.prod file with the following keys

```
API_KEY: Youtube Data APIv3 key 
SECRET_KEY: django secret key
ALLOWED_HOSTS: allowed hosts for your site
DEBUG: django debug mode
DJANGO_SUPERUSER_NAME:
DJANGO_SUPERUSER_PASSWORD:
DJANGO_SUPERUSER_EMAIL:
DJANGO_MANAGEPY_MIGRATE: set to 'on' to migrate everytime the container starts
```

then 

```docker-compose up -d```

