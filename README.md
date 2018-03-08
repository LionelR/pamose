# PAssive MOnitoring SErver

PAssive MOnitoring SErver description

## Quick Start

On Debian/Ubuntu:

    sudo apt install libpq-dev postgresql

Configure the database:

    # sudo su postgres
    postgres# psql
    postgres=> CREATE USER pamose WITH PASSWORD 'pamose';
    postgres=> CREATE DATABASE pamose WITH OWNER pamose;
    postgres=> \q

and test the newly created user/database:

    # psql -h localhost -U pamose pamose  

Run the application:
    
    vim pamose.cfg
    export PAMOSE_SETTINGS=/path/to/pamose.cfg
    pamose initdb  # Just the first time for creating/populating the DB
    pamose run

And open it in the browser at [http://127.0.0.1:5000/](http://127.0.0.1:5000/)




## Development environment and release process

 - create virtualenv with Flask and PAssive MOnitoring SErver installed into it (latter is installed in
   [develop mode](http://setuptools.readthedocs.io/en/latest/setuptools.html#development-mode) which allows
   modifying source code directly without a need to re-install the app): `make venv`

 - run development server in debug mode: `make run`; Flask will restart if source code is modified

 - run tests: `make test` (see also: [Testing Flask Applications](http://flask.pocoo.org/docs/0.12/testing/))

 - create source distribution: `make sdist` (will run tests first)

 - to remove virtualenv and built distributions: `make clean`

 - to add more python dependencies: add to `install_requires` in `setup.py`

 - to modify configuration in development environment: edit file `settings.cfg`; this is a local configuration file
   and it is *ignored* by Git - make sure to put a proper configuration file to a production environment when
   deploying


## Build

In either case, generally the idea is to build a package (`make sdist`), deliver it to a server (`scp ...`),
install it (`pip install pamose.tar.gz`), ensure that configuration file exists and
`PAMOSE_SETTINGS` environment variable points to it, ensure that user has access to the
working directory to create and write log files in it, and finally run a
[WSGI container](http://flask.pocoo.org/docs/0.12/deploying/wsgi-standalone/) with the application.
And, most likely, it will also run behind a
[reverse proxy](http://flask.pocoo.org/docs/0.12/deploying/wsgi-standalone/#proxy-setups).

## Dependencies

 - [https://flask-restful.readthedocs.io/en/latest/]flask-restful
 - [http://flask-sqlalchemy.pocoo.org]flask-sqlalchemy
