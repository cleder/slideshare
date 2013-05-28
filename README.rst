Introduction
=============

Lean and complete SlideShare_ API Implementation.

Usage
-----

    >>> import slideshare
    >>> API_KEY = 'ABC' #You have to provide your own valid key here
    >>> SHARED_SECRET = 'DEFG' #You have to provide your own valid secret here
    >>> api = slideshare.SlideshareAPI(API_KEY,SHARED_SECRET)
    >>> help(slideshare.SlideshareAPI)
    >>> sl_id = '21834196'
    >>> api.get_slideshow(slideshow_id=sl_id)

For more examples please refer to the tests_


Methods
--------

- add_favorite
- check_favorite
- delete_slideshow
- edit_slideshow
- get_slideshow
- get_slideshow_by_group (untested)
- get_slideshows_by_tag
- get_slideshows_by_user
- get_user_campaign_leads (untested)
- get_user_campaigns
- get_user_contacts
- get_user_favorites
- get_user_groups (raises HTTPError: HTTP Error 500: Internal Server Error)
- get_user_leads
- get_user_tags
- search_slideshows
- upload_slideshow


Testing
--------

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

Some tests assume a slideshow_id you have to be able to edit or delete,
you will have to change these values otherwise the tests will fail.

Links
-----

- Code repository: https://github.com/cleder/slideshare
- Report bugs at: https://github.com/cleder/slideshare/issues
- Questions and comments to: http://groups.google.com/group/slideshare-developers


.. _tests: https://github.com/cleder/slideshare/blob/master/slideshare/test_main.py
.. _SlideShare: http://www.slideshare.net/


