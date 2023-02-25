# match-group-microservice
This repo is for CU E6156 Fall 2022 course project. The group microservice is responded to the main 
logic of activities inside groups.

## configuration

An `.env` file under `./matchgroupmicroservice` or system environment variables setup is needed
for deploying and running. Make sure you have the following values available in your environment:

```
RDS_DB_NAME=<>
RDS_HOSTNAME=<>
RDS_PASSWORD=<>
RDS_PORT=<>
RDS_USERNAME=<>
SIGNING_KEY=<> # this needs to be same as the secret key of what jwtauth microservice use
DEBUG=<True or False>
MESSAGE_SERVICE=<>
POST_MESSAGE_PATH=<>
USER_SERVICE=<>
GET_USER_PATH=<>
POST_USER_BATCH_PATH=<>
```

## prerequisite
`python3.7`. Using a virtual environment is recommended.

## deploy & run

### AWS Elastic Beanstalk
For details see [action config](.github/workflows/aws-eb-django.yml).
AWS credentials need to be set in the repo settings.

### local
```
pip install -r requirements.txt
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py loaddata groups/fixtures/initial_data.json
python3 manage.py runserver 0.0.0.0:9999
```

## documentation

### generate schema
`./manage.py spectacular --file schema.yml`

### doc path
```
api/schema/swagger-ui/
api/schema/redoc/
```
