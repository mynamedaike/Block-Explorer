# Block Explorer

## Dependencies

- Ubuntu (16.04.4 LTS)
- MySQL (5.7.24)
- Redis (3.0.6)
- Nginx (1.10.3)
- Python (3.7.2) and Third Party Packages
    - django
    - celery
    - celery_once
	- pymysql
	- redis
	- web3
	- django-cors-headers
	- uwsgi

## Starting Up the Program

1. Start up MySQL and Redis Service.
2. Create a database in MySQL using the name specified in the settings.py file.
3. Generate a data migration file, and execute data migration.

```
python3.7 manage.py makemigrations
python3.7 manage.py migrate
```

4. Start up Celery

```celery -B -A NUChain worker -l info >> celery.log 2>&1 &```

5. start up uWSGI

```uwsgi --ini uwsgi.ini```

6. start up or reload Nginx

```nginx``` or ```nginx -s reload```
