# -*- coding: utf-8 -*-

import time, hashlib
import urllib2, urllib
from urlparse import urlparse, urlunparse
import logging
logger = logging.getLogger('slideshare.api')

import xmltodict

from functools import wraps

import itertools
import mimetools
import mimetypes

class MultiPartForm(object):
    """Accumulate the data to be used when posting a form."""
    #'PyMOTW (http://www.doughellmann.com/PyMOTW/)'

    def __init__(self):
        self.form_fields = []
        self.files = []
        self.boundary = mimetools.choose_boundary()
        return

    def get_content_type(self):
        return 'multipart/form-data; boundary=%s' % self.boundary

    def add_field(self, name, value):
        """Add a simple field to the form data."""
        self.form_fields.append((name, value))
        return

    def add_file(self, fieldname, filename, fileHandle, mimetype=None):
        """Add a file to be uploaded."""
        body = fileHandle.read()
        if mimetype is None:
            mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        self.files.append((fieldname, filename, mimetype, body))
        return

    def __str__(self):
        """Return a string representing the form data, including attached files."""
        # Build a list of lists, each containing "lines" of the
        # request.  Each part is separated by a boundary string.
        # Once the list is built, return a string where each
        # line is separated by '\r\n'.
        parts = []
        part_boundary = '--' + self.boundary

        # Add the form fields
        parts.extend(
            [ part_boundary,
              'Content-Disposition: form-data; name="%s"' % name,
              '',
              value,
            ]
            for name, value in self.form_fields
            )

        # Add the files to upload
        parts.extend(
            [ part_boundary,
              'Content-Disposition: file; name="%s"; filename="%s"' % \
                 (field_name, filename),
              'Content-Type: %s' % content_type,
              '',
              body,
            ]
            for field_name, filename, content_type, body in self.files
            )

        # Flatten the list and add closing boundary marker,
        # then return CR+LF separated data
        flattened = list(itertools.chain(*parts))
        flattened.append('--' + self.boundary + '--')
        flattened.append('')
        for flat in flattened:
            if not isinstance(flat, str):
                print flat
        return '\r\n'.join(flattened)


class SlideShareServiceError(Exception):
    """ custom exceptions """
    def __init__(self, errno, errmsg):
         self.errno = errno
         self.errmsg = errmsg
    def __str__(self):
        return 'SlideShareServiceError %s: %s' %(self.errno, self.errmsg)



def callapi(func):
    service_url = 'https://www.slideshare.net/api/2/' + func.__name__
    @wraps(func)
    def wrapper(*args, **kwargs):
        """
        All requests made using the SlideShare API must have the following parameters:

        api_key: Set this to the API Key that SlideShare has provided for you.
        ts: Set this to the current time in Unix TimeStamp format, to the
            nearest second(?).
        hash: Set this to the SHA1 hash of the concatenation of the shared
            secret and the timestamp (ts).
        """
        self = args[0]
        fparams, fargs, rt = func(*args, **kwargs)
        #current time in Unix TimeStamp format, to the nearest second
        ts = int(time.time())
        params = {
            'api_key': self.api_key,
            'ts': ts,
            'hash': hashlib.sha1(self.sharedsecret + str(ts)).hexdigest(),
        }
        for k,v in fargs.iteritems():
            if (k in fparams) and v:
                params[k] = v
        logger.debug('open url %s' % service_url)
        logger.debug('with parameters %s ' % str(params))
        if 'slideshow_srcfile' in params:
            form = MultiPartForm()
            for k,v in params.iteritems():
                if k == 'slideshow_srcfile':
                    form.add_file(k, filename = v['filename'],
                    fileHandle = v['filehandle'],
                    mimetype = v['mimetype'])
                else:
                    form.add_field(k,str(v))
            # Build the request
            request = urllib2.Request(service_url)
            body = str(form)
            request.add_header('Content-type', form.get_content_type())
            request.add_header('Content-length', len(body))
            request.add_data(body)
            data = urllib2.urlopen(request).read()
        else:
            eparams = urllib.urlencode(params)
            data = urllib2.urlopen(service_url, eparams).read()
        json = xmltodict.parse(data)
        if json.get('SlideShareServiceError'):
            print data
            print json
            raise SlideShareServiceError(
                json['SlideShareServiceError']['Message']['@ID'],
                json['SlideShareServiceError']['Message']['#text'])
        return json

    return wrapper



class SlideshareAPI(object):
    api_key = None
    sharedsecret = None

    def __init__(self, api_key, sharedsecret):
        if api_key and sharedsecret:
            self.sharedsecret = sharedsecret
            self.api_key = api_key
        else:
            raise ValueError


    @callapi
    def get_slideshow(self, slideshow_id=None, slideshow_url=None, **kwargs):
        """
        Get Slideshow Information

        Request type: HTTPS GET
        Authorization: Optional
        URL: https://www.slideshare.net/api/2/get_slideshow

        Required parameters:
        --------------------
        slideshow_id: id of the slideshow to be fetched.
        slideshow_url: URL of the slideshow to be fetched.
            This is required if slideshow_id is not set.
            If both are set, slideshow_id takes precedence.

        Optional parameters
        username: username of the requesting user
        password: password of the requesting user
        exclude_tags: Exclude tags from the detailed information. 1 to exclude.
        detailed: Whether: or not to include optional information. 1 to include,
            0 (default) for basic information.
        """
        params = ['username', 'password', 'exclude_tags', 'detailed']
        if slideshow_id or slideshow_url:
            if slideshow_id:
                kwargs['slideshow_id'] = slideshow_id
                params.append('slideshow_id')
            else:
                urlob = urlparse(slideshow_url)
                if urlob.hostname == 'www.slideshare.net':
                    url = urlunparse([urlob.scheme, urlob.netloc,
                        urlob.path, '', '', ''])
                    params.append('slideshow_url')
                    kwargs['slideshow_url'] = url
                else:
                    raise ValueError
        else:
            raise ValueError
        return params, kwargs, 'GET'


    @callapi
    def get_slideshows_by_tag(self, tag, **kwargs):
        """
        Get Slideshows By Tag

        Request Type: HTTPS GET
        Authorization: None
        URL: https://www.slideshare.net/api/2/get_slideshows_by_tag

        Required parameters:
        --------------------
        tag: tag name

        Optional parameters:
        --------------------
        limit: specify number of items to return
        offset: specify offset
        detailed: Whether or not to include optional information.
            1 to include, 0 (default) for basic information.
        """
        params = ['tag', 'limit', 'offset', 'detailed']
        kwargs['tag'] = tag
        return params, kwargs, 'GET'

    @callapi
    def get_slideshow_by_group(self, group_name, **kwargs):
        """
        Get Slideshows By Group

        Request Type: HTTPS GET
        Authorization: None
        URL: https://www.slideshare.net/api/2/get_slideshows_by_group

        Required parameters:
        --------------------
        group_name: Group name (as returned in QueryName element in
            get_user_groups method)

        Optional parameters:
        --------------------
        limit: specify number of items to return
        offset: specify offset
        detailed: Whether or not to include optional information.
            1 to include, 0 (default) for basic information.
        """
        params = ['group_name', 'limit', 'offset', 'detailed']
        kwargs['group_name'] = group_name
        return params, kwargs, 'GET'

    @callapi
    def get_slideshows_by_user(self, username_for, **kwargs):
        """
        Get Slideshows By User

        Request Type: HTTPS GET
        Authorization: None
        URL:https://www.slideshare.net/api/2/get_slideshows_by_user

        Required parameters:
        -------------------
        username_for: username of owner of slideshows

        Optional parameters:
        --------------------
        username: username of the requesting user
        password: password of the requesting user
        limit: specify number of items to return
        offset: specify offset
        detailed: Whether or not to include optional information.
            1 to include, 0 (default) for basic information.
        get_unconverted: Whether or not to include unconverted slideshows.
            1 to include them, 0 (default) otherwise.
        """
        params = ['username_for', 'username', 'password', 'limit',
            'offset', 'detailed', 'get_unconverted']

        kwargs['username_for'] = username_for
        return params, kwargs, 'GET'

    @callapi
    def search_slideshows(self, q, **kwargs):
        """
        Slideshow Search

        Request Type: HTTPS GET
        Authorization: None
        URL: https://www.slideshare.net/api/2/search_slideshows

        Required parameters:
        --------------------
        q: the query string

        Optional parameters:
        --------------------
        page: The page number of the results
            (works in conjunction with items_per_page), default is 1
        items_per_page: Number of results to return per page,
            default is 12
        lang: Language of slideshows (default is English, 'en')
        sort: Sort order (default is 'relevance')
            ('mostviewed','mostdownloaded','latest')
        upload_date: The time period you want to restrict your search to.
            'week' would restrict to the last week. (default is 'any')
            ('week', 'month', 'year')
        what: What type of search. If not set, text search is used.
            'tag' is the other option.
        download: Slideshows that are available to download;
            Set to '0' to do this, otherwise default is all slideshows.
        fileformat: File format to search for. Default is "all".
            ('pdf':PDF,'ppt':PowerPoint,'odp':Open Office,
            'pps':PowerPoint Slideshow,'pot':PowerPoint template)
        file_type: File type to search for. Default is "all".
            ('presentations', 'documents', 'webinars','videos')
        cc: Set to '1' to retrieve results under the Creative Commons license.
            Default is '0'
        cc_adapt: Set to '1' for results under Creative Commons that
            allow adaption, modification. Default is '0'
        cc_commercial: Set to '1' to retrieve results with the commercial
            Creative Commons license. Default is '0'
        detailed: Whether or not to include optional information.
            1 to include, 0 (default) for basic information.
        """
        params = ['q', 'page', 'items_per_page', 'lang', 'sort',
            'upload_date', 'what', 'download', 'fileformat', 'file_type',
            'cc', 'cc_adapt', 'cc_commercial', 'detailed']
        kwargs['q'] = q
        return params, kwargs, 'GET'

    @callapi
    def get_user_groups(self, username_for, **kwargs):
        """Get User Groups

        Request Type: HTTPS GET
        Authorization: Optional
        URL: https://www.slideshare.net/api/2/get_user_groups

        Required parameters:
        --------------------
        username_for: username of user whose groups are being requested

        Optional parameters:
        --------------------
        username: username of the requesting user
        password: password of the requesting user
        """
        params = ['username_for', 'username', 'password' ]
        kwargs['username_for'] = username_for
        return params, kwargs, 'GET'

    @callapi
    def get_user_favorites(self, username_for):
        """
        Get User Favorites

        Request Type: HTTPS GET
        Authorization: Optional
        URL: https://www.slideshare.net/api/2/get_user_favorites

        Required parameters:
        -------------------
        username_for: username of user whose Favorites are being requested
        """
        params = ['username_for']
        return params, {'username_for': username_for}, 'GET'

    @callapi
    def get_user_contacts(self, username_for, **kwargs):
        """
        Get User Contacts

        Request Type: HTTPS GET
        Authorization: Optional
        URL: https://www.slideshare.net/api/2/get_user_contacts

        Required parameters:
        --------------------
        username_for: username of user whose Contacts are being requested

        Optional parameters:
        --------------------
        limit: specify number of items to return
        offset: specify offset
        """
        params = ['username_for', 'limit', 'offset' ]
        kwargs['username_for'] = username_for
        return params, kwargs, 'GET'

    @callapi
    def get_user_tags(self, username, password):
        """
        Get User Tags

        Request Type: HTTPS GET
        Authorization: Required
        URL: https://www.slideshare.net/api/2/get_user_tags

        Required parameters:
        --------------------
        username: username of the requesting user
        password: password of the requesting user
        """
        params = ['username', 'password' ]
        kwargs = {}
        kwargs['username'] = username
        kwargs['password'] = password
        return params, kwargs, 'GET'

    @callapi
    def edit_slideshow(self,username, password, slideshow_id, **kwargs):
        """
        Edit Existing Slideshow

        Request Type: HTTPS GET
        Authorization: Required
        URL: https://www.slideshare.net/api/2/edit_slideshow

        Required parameters:
        --------------------
        username: username of the requesting user
        password: password of the requesting user
        slideshow_id: slideshow ID

        Optional parameters:
        --------------------
        slideshow_title: text
        slideshow_description: text
        slideshow_tags: text
        make_slideshow_private: Should be Y if you want to make the
            slideshow private. If this is not set,
            following tags will not be considered:
        generate_secret_url: Generate a secret URL for the slideshow.
            Requires make_slideshow_private to be Y
        allow_embeds: Sets if other websites should be allowed to embed
            the slideshow. Requires make_slideshow_private to be Y
        share_with_contacts: Sets if your contacts on SlideShare can view
            the slideshow. Requires make_slideshow_private to be Y
        """
        params = ['username', 'password', 'slideshow_id', 'slideshow_title',
        'slideshow_description', 'slideshow_tags', 'make_slideshow_private']
        if 'make_slideshow_private' in kwargs:
            if kwargs['make_slideshow_private'] == 'Y':
                params += ['generate_secret_url', 'allow_embeds',
                'share_with_contacts']
        kwargs['username'] = username
        kwargs['password'] = password
        kwargs['slideshow_id'] = slideshow_id
        return params, kwargs, 'GET'

    @callapi
    def delete_slideshow(self, username, password, slideshow_id):
        """
        Delete Slideshow

        Request Type: HTTPS GET
        Authorization: Required
        URL:https://www.slideshare.net/api/2/delete_slideshow

        Required parameters:
        --------------------
        username: username of the requesting user
        password: password of the requesting user
        slideshow_id: slideshow ID
        """
        params = ['username', 'password', 'slideshow_id']
        kwargs = {}
        kwargs['username'] = username
        kwargs['password'] = password
        kwargs['slideshow_id'] = slideshow_id
        return params, kwargs, 'GET'

    @callapi
    def upload_slideshow(self, username, password,
         slideshow_title, slideshow_srcfile=None, upload_url=None,
         slideshow_description=None,
         slideshow_tags=None, **kwargs):
        """
        Upload Slideshow

        Note: This method requires extra permissions. If you want to
        upload a file using SlideShare API, please send an email to
        api@slideshare.com with your developer account username
        describing the use case.

        Request Type: HTTPS GET or HTTPS POST (for slideshow_srcfile)
        Authorization: Required
        URL: https://www.slideshare.net/api/2/upload_slideshow

        Required parameters:
        --------------------
        username: username of the requesting user
        password: password of the requesting user
        slideshow_title: slideshow's title
        slideshow_srcfile: slideshow file (requires HTTPS POST) -OR-
        upload_url: string containing an url pointing to the power point
            file: ex: http://domain.tld/directory/my_power_point.ppt
            The following urls are also acceptable

            http://www.domain.tld/directory/file.ppt
            http://www.domain.tld/directory/file.cgi?filename=file.ppt
            Note, that this will not accept entries that cannot be
            identified by their extension. If you sent
            http://www.domain.tld/directory/file.cgi?id=2342
            Slideshare will not be able to identify the type of the file!

        Optional parameters:
        --------------------

        slideshow_description: description
        slideshow_tags: tags should be comma separated
        make_src_public: Y if you want users to be able to download the
            ppt file, N otherwise. Default is Y
        Privacy settings (optional):
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        make_slideshow_private: Should be Y if you want to make the
            slideshow private.
            If this is not set, following tags will not be considered
        generate_secret_url: Generate a secret URL for the slideshow.
            Requires make_slideshow_private to be Y
        allow_embeds: Sets if other websites should be allowed to embed
            the slideshow.
            Requires make_slideshow_private to be Y
        share_with_contacts: Sets if your contacts on SlideShare can view
            the slideshow.
            Requires make_slideshow_private to be Y

        The document will upload into the account of the user specified
        by (username / password). The user associated with the API key
        need not be the same as the user into who's account the
        slideshow gets uploaded. So, for example, a bulk uploader would
        include the api_key (and hash) associated with the API account,
        and the username and password associated with the account being
        uploaded to.
        """
        params = ['username', 'password', 'slideshow_title', 'slideshow_srcfile',
            'upload_url', 'slideshow_description', 'slideshow_tags',
            'make_src_public']
        if 'make_slideshow_private' in kwargs:
            if kwargs['make_slideshow_private'] == 'Y':
                params += ['make_slideshow_private', 'generate_secret_url'
                    'allow_embeds', 'share_with_contacts']
        if slideshow_srcfile:
            request_type = 'POST'
        else:
            request_type = 'GET'
        kwargs['username'] = username
        kwargs['password'] = password
        kwargs['slideshow_title'] = slideshow_title
        kwargs['slideshow_srcfile'] = slideshow_srcfile
        kwargs['upload_url'] = upload_url
        kwargs['slideshow_description'] = slideshow_description
        kwargs['slideshow_tags'] = slideshow_tags
        return params, kwargs, request_type

    @callapi
    def add_favorite(self, username, password, slideshow_id):
        """
        Favorite Slideshow

        Request Type: HTTPS GET
        Authorization: Required
        URL: https://www.slideshare.net/api/2/add_favorite

        Required parameters:
        --------------------
        username: username of the requesting user
        password: password of the requesting user
        slideshow_id: the slideshow to be favorited
        """
        params = ['username', 'password', 'slideshow_id']
        kwargs ={}
        kwargs['username'] = username
        kwargs['password'] = password
        kwargs['slideshow_id'] = slideshow_id
        return params, kwargs, 'GET'

    @callapi
    def check_favorite(self, username, password, slideshow_id):
        """
        Check Favorite

        Request Type: HTTPS GET
        Authorization: Required
        URL: https://www.slideshare.net/api/2/check_favorite

        Required parameters:
        ---------------------
        username: username of the requesting user
        password: password of the requesting user
        slideshow_id: Slideshow which would be favorited
        """
        params = ['username', 'password', 'slideshow_id']
        kwargs = {}
        kwargs['username'] = username
        kwargs['password'] = password
        kwargs['slideshow_id'] = slideshow_id
        return params, kwargs, 'GET'



    @callapi
    def get_user_campaigns(self, username, password):
        """
        Get Campaign Information

        Request type: HTTPS POST
        Authorization: Mandatory
        URL: https://www.slideshare.net/api/2/get_user_campaigns

        Required parameters:
        --------------------
        username: username of the requesting user
        password: password of the requesting user
        """
        request_type = 'POST'
        params = ['username', 'password']
        kwargs = {}
        kwargs['username'] = username
        kwargs['password'] = password
        return params, kwargs, request_type

    @callapi
    def get_user_leads(self, username, password, **kwargs):
        """
        Get Leads Information For ALL Campaigns

        Request type: HTTPS POST
        Authorization: Mandatory
        URL: https://www.slideshare.net/api/2/get_user_leads

        Required parameters:
        --------------------

        username: username of the requesting user
        password: password of the requesting user

        Optional parameters:
        --------------------
        begin: only get leads collected after this UTC date: YYYYMMDDHHMM
        end: only get leads collected before this UTC date: YYYYMMDDHHMM
            For ruby/C people this is: strftime("%Y%m%d%H%M")
        """
        request_type = 'POST'
        params = ['username', 'password', 'begin', 'end' ]
        kwargs['username'] = username
        kwargs['password'] = password
        return params, kwargs, request_type

    @callapi
    def get_user_campaign_leads(self, username, password, campaign_id, **kwargs):
        """
        Get User Leads Information For A Specific Lead Campaign

        Request type: HTTPS POST
        Authorization: Mandatory
        URL: https://www.slideshare.net/api/2/get_user_campaign_leads

        Required parameters:
        username: username of the requesting user
        password: password of the requesting user
        campaign_id: campaign_id to select the leads from

        Optional parameters:
        --------------------
        begin: only get leads collected after this UTC date: YYYYMMDDHHMM
        end: only get leads collected before this UTC date: YYYYMMDDHHMM
        """
        request_type = 'POST'
        params = [ 'username', 'password', 'campaign_id', 'begin', 'end' ]
        kwargs['username'] = username
        kwargs['password'] = password
        kwargs['campaign_id'] = campaign_id
        return params, kwargs, request_type
