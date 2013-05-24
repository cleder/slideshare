
Lean and complete Slideshare API Implementation.




Testing:
========

You need to create a file secret.py which has the content
::
    # DO NOT check these into git
    API_KEY = 'your api key'
    SHARED_SECRET = 'your shared secret'
    USERNAME = 'your username'
    PASSWORD = 'your password'

You have to fill in the values of your slideshare account. Then you can
run the tests with
::
    python setup.py test
