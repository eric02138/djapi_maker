# djapi_maker
#### A django management command to inspect databases and generate a RESTful API

Often, large organizations will be saddled with many old databases - with only a handful of users knowing what is in any given database.  Creating browsable APIs can help non-technical users navigate this data.  However, creating a custom API for each db can be labor intensive.  

This extension aims to soften this pain-point by automatically creating an django app from each project database while also writing the Django REST Framework code that exposes an API.

By no means is this package meant to avoid use of the [Django REST Framework](https://www.django-rest-framework.org/), instead, it should be viewed as a quick-and-dirty jumping off point for organizational API use.  

## Install

`pip install djapi_maker_cli`


## Usage

This package assumes that you have a bare-bones django project with a default database that was generated through standard django migrations, with legacy databases to be inspected as additional named sources.  So the DATABASE setting in your settings.py file should look something like this:
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'default',
        'USER': 'default_user',
        'HOST': 'localhost',
        'PASSWORD': 'xxxxxxxxx',
        'PORT': '3306'
    },
    'db_to_apize': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'db_to_apize',
        'USER': 'db_to_apize_user',
        'HOST': 'localhost',
        'PASSWORD': 'xxxxxxxxxxx',
        'PORT': '3306'
    }
}
```

Now you can run the api maker command:

`./manage.py makeapi`

By default, the api generator will ignore the default django database as exposing user information could be a security risk.  If you would like to ignore this risk, you can include the default database with `include_default_db` option:

`./manage.py makeapi --include_default_db`

