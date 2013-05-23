from setuptools import setup, find_packages
import sys, os

version = '0.0'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = read('README.rst')



setup(name='slideshare',
      version=version,
      description="Slideshare API client",
      long_description=long_description,
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='slideshare api rest',
      author='Christian Ledermann',
      author_email='christian.ledermann@gmail.com',
      url='https://github.com/cleder/slideshare',
      license='LGPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'requests',
          'xmltodict',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
