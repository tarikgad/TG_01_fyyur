Fyyur
-----



### Introduction

This is the first project in `Advanced Web Development` Nanodegree Program

This is the project [rubrucs](https://review.udacity.com/#!/rubrics/2653/view)


### Intialize the submission

First, [install Flask](http://flask.pocoo.org/docs/1.0/installation/#install-flask) if you haven't already.

  ```
  $ cd ~
  $ sudo pip3 install Flask
  ```

To start and run the local development server,

1. Initialize and activate a virtualenv:
  ```
  $ cd YOUR_PROJECT_DIRECTORY_PATH/
  $ virtualenv --no-site-packages env
  $ source env/bin/activate
  ```

2. Install the dependencies:
  ```
  $ pip install -r requirements.txt
  ```

3. Prepare the DB config:
  ```
  update the `config.py` file to have your right DB credentials
  ```

4. Migrate the database:
  ```
  $ Flask db init
  $ Flask db migrate
  $ Flask db upgrade
  $ python initialize.py
  ```

5. Run the development server:
  ```
  $ export FLASK_APP=app
  $ export FLASK_ENV=development
  $ python3 app.py
  ```

6. Navigate to Home page [http://localhost:5000](http://localhost:5000)


