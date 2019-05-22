# -*- coding: utf-8 -*-
from setuptools import setup

if __name__ == "__main__":
      setup(name='djapi_maker_cli',
      version='0.0.1',
      description="""Management command for django rest framework to quickly inspect dbs and create apps from tables.
      """,
      url='http://github.com/eric02138/djapi_maker',
      author='Eric Mattison',
      author_email='emattison@gmail.com',
      license='MIT',
      packages=['djapi_maker_cli'],
      install_requires=[
            "djangorestframework"
      ],
      zip_safe=False)