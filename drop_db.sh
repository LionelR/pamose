sudo su postgres -c "psql -c 'DROP DATABASE pamose'"
sudo su postgres -c "psql -c 'CREATE DATABASE pamose WITH OWNER pamose'"