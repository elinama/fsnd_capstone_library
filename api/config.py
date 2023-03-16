import os

SECRET_KEY = '9VjlURDg5v23GHdiI8_rvEN9I9OQ_KwjXBGo6x6Sois6pURwQsydnigPx9YuqmEM'
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))
project_dir = os.path.dirname(os.path.abspath(__file__))
# Enable debug mode.
DEBUG = True


# Connect to the database
# DONE IMPLEMENT DATABASE URL
class Config(object):
    database_filename = "library.db"
    database_path = "sqlite:///{}".format(os.path.join(project_dir, database_filename))
    SQLALCHEMY_DATABASE_URI = database_path
    # Turn off track modifications warning
    SQLALCHEMY_TRACK_MODIFICATIONS = True
