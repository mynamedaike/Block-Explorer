# NUChain Explorer
NUChain Explorer is a block explorer built on Vue.js and Python. It adopts the architecture separating frontend from backend with a REST interface in between. This repository is for the backend part.

Website: http://nuchain.pro

## Install the Dependencies

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
- C compiler
```
sudo apt-get install build-essential
```
- Python (>=3.7.0)
```
sudo apt-get install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3.7
sudo apt-get install python3.7-dev
```
- Third Party Packages in Python
    - django 2.1.7
    - celery
    - celery_once
    - pymysql
    - redis
    - web3
    - django-cors-headers
    - uwsgi
    
Install pip first.
```
wget https://bootstrap.pypa.io/get-pip.py
sudo python3.7 get-pip.py
```
Then install the above packages using pip.
```
sudo pip3.7 install -U XXX
```
    
## Start up the Program

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
5. Start up uWSGI.
```
uwsgi --ini uwsgi.ini
```
6. Start up or reload Nginx.
```
sudo nginx 
or 
sudo nginx -s reload
```
