import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgres://uvwokkqnckffxd:ec018b04458efff1918e5aee38d04c31a3ec87133472c1c5147e882f5235e18f@ec2-46-137-79-235.eu-west-1.compute.amazonaws.com:5432/df6dc52bthil9e'
SQLALCHEMY_TRACK_MODIFICATIONS = False