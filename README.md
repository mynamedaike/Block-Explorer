# NUChain Explorer
NUChain Explorer is a block explorer built on Vue.js and Python. It adopts the architecture separating frontend from backend with a REST interface in between. This repository is for the backend part.

Website: http://nuchain.pro

## Dependencies Installation

- Ubuntu (>=16.04.4 LTS)
- MySQL (>=5.7.24)
```
sudo apt-get install mysql-server
```
- Redis (>=3.0.6)
```
sudo apt-get install redis-server
```
- Nginx (>=1.10.3)
```
sudo apt-get install nginx
```
- Python (>=3.7.0)
```
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.7
```
- Third Party Packages in Python
    - django
    - celery
    - celery_once
    - pymysql
    - redis
    - web3
    - django-cors-headers
    - uwsgi
1. Install pip first.
```
wget https://bootstrap.pypa.io/get-pip.py
sudo python3.7 get-pip.py
```
2. Then install the following packages using pip.
```
pip3.7 install -U XXX
```
    

## Starting Up the Program

1. Start up MySQL and Redis Service.
2. Create a database in MySQL using the name specified in the settings.py file.
3. Generate a data migration file, and execute data migration.
```
python3.7 manage.py makemigrations
python3.7 manage.py migrate
```
4. Start up Celery.
```
celery -B -A NUChain worker -l info >> celery.log 2>&1 &
```
5. start up uWSGI.
```
uwsgi --ini uwsgi.ini
```
6. start up or reload Nginx.
```
nginx 
or 
nginx -s reload
```
