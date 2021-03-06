# -*- coding: utf-8 -*-
# Django settings for glabnetman project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = ''           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = ''             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Berlin'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'de-de'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '!c)j0q+*w!x3&+(+4dpylr*@4+08e-m&3*who(3y$6gol)8$63'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.RemoteUserAuthBackend',)

ROOT_URLCONF = 'tomato.urls'

import os
CURRENT_DIR = os.path.dirname(__file__)
TEMPLATE_DIRS = os.path.join(CURRENT_DIR, 'templates')

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
)

server_protocol = "http"
server_host = "localhost"
server_port = "8000"
server_httprealm="G-Lab ToMaTo"
project_url="http://dswd.github.com/ToMaTo/%s"
help_url="http://github.com/dswd/ToMaTo/wiki/%s"
ticket_url="http://github.com/dswd/ToMaTo/issues/%s"
map="generic"

try:
	import imp, tempfile, sys
	for path in filter(os.path.exists, ["/etc/tomato/web.conf", os.path.expanduser("~/.tomato/web.conf"), "web.conf"]):
		file = open(path, "r")
		with file:
			tmp = tempfile.mktemp()
			try:
				imp.load_source("web_config", tmp, file)
				from web_config import *
				print >>sys.stderr, "Loaded config from %s" % path
			finally:
				if os.path.exists(tmp+"c"):
					os.remove(tmp+"c")
except:
	import traceback
	traceback.print_exc()
