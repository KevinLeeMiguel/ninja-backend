# Ninja Backend Challenge

This is solution to a Ninja backend challenge. It is built using Python Django, Redis, and SqLite.

## Run the app

Follow the following steps to run the app:

### Installing Pre-requisites

To run the app some requirements need to be met and some softwares and packages need to be installed

- Install [python](https://www.python.org/downloads/) and [Conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html)

- Install the dependencies of the app

  ```sh
  # navigate to the location of the cloned repo
  cd path/to/cloned_repo

  # Create a conda environment to run the app in
  conda env create -f ./environment.yml

  ```

- Run Redis
  ```sh
  # Run Redis (as docker container)
  docker run -d --name ninja-redis -p 6379:6379 redis/redis-stack-server:latest
  ```

### Setting up and Running the app

- Create migrations and run them against the db

```sh
  # activate the environment
  conda activate ninja-backend

  # Create Migrations
  python manage.py makemigrations

  # apply migrations against the SqLite DB
  python manage.py migrate

  # Create a SuperUser for the app
  python manage.py createsuperuser

```

- Run the Redis docker container

```sh
  # Make sure the redis container is running if not run the command below
  docker start ninja-redis
```

- Run the app

```sh
  # activate the environment
  conda activate ninja-backend

  # Run the app instance
  python manage.py runserver

```


## Endpoints (using the service)

[Click here](https://documenter.getpostman.com/view/6457378/2s8YRiKZK4) to access the documentation of the api endpoints.
