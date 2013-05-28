# -*- coding: utf-8 -*-
import unittest

try:
    from .secret import API_KEY, SHARED_SECRET, USERNAME, PASSWORD
except:
    API_KEY = SHARED_SECRET = USERNAME = PASSWORD = None
import slideshare

from datetime import datetime

class BasicTestCase(unittest.TestCase):

    def test_SlideShareServiceError(self):
        api = slideshare.SlideshareAPI(API_KEY,SHARED_SECRET)
        api.api_key=None
        sl_id = '21834196'
        try:
            api.get_slideshow(slideshow_id=sl_id)
            raise Exception
        except slideshare.SlideShareServiceError, exc:
            self.assertEqual(exc.errno, '1')
        api.api_key = API_KEY
        try:
            api.get_slideshow(slideshow_id=sl_id, username='NoSuchUser', password='none' )
            raise Exception
        except slideshare.SlideShareServiceError, exc:
            self.assertEqual(exc.errno, '2')
        try:
            api.get_slideshow(slideshow_id='none' )
            raise Exception
        except slideshare.SlideShareServiceError, exc:
            self.assertEqual(exc.errno, '9')


    def test_get_slideshow(self):
        api = slideshare.SlideshareAPI(API_KEY,SHARED_SECRET)
        #get slideshow by id
        sl_id = '21834196'
        sls = api.get_slideshow(slideshow_id=sl_id)
        self.assertEqual(sls['Slideshow']['ID'], sl_id)
        sls = api.get_slideshow(slideshow_url=
            "http://www.slideshare.net/slidesharepython/python-slideshare-api-test-20130524t162943687234")
        self.assertEqual(sls['Slideshow']['ID'], sl_id)


    def test_get_slideshows_by_tag(self):
        api = slideshare.SlideshareAPI(API_KEY,SHARED_SECRET)
        sls = api.get_slideshows_by_tag('python')
        self.assertEqual(sls['Tag']['Name'], 'python')
        self.assertFalse(sls['Tag']['Count'] == '0')


    def test_get_slideshows_by_group(self):
        api = slideshare.SlideshareAPI(API_KEY,SHARED_SECRET)
        pass

    def test_get_slideshows_by_user(self):
        api = slideshare.SlideshareAPI(API_KEY,SHARED_SECRET)
        sls = api.get_slideshows_by_user(USERNAME)
        self.assertEqual(sls['User']['Name'], USERNAME)

    def test_search_slideshows(self):
        api = slideshare.SlideshareAPI(API_KEY,SHARED_SECRET)
        sls = api.search_slideshows(q='python')
        self.assertEqual(sls['Slideshows']['Meta']['Query'], 'python')
        self.assertFalse(sls['Slideshows']['Meta']['TotalResults'] == '0')

    def test_get_user_groups(self):
        api = slideshare.SlideshareAPI(API_KEY,SHARED_SECRET)
        #XXX HTTPError: HTTP Error 500: Internal Server Error
        #groups = api.get_user_groups(USERNAME)
        #self.assertEqual(groups, '')
        pass


    def test_get_user_favorites(self):
        api = slideshare.SlideshareAPI(API_KEY,SHARED_SECRET)
        favs = api.get_user_favorites(USERNAME)
        self.assertTrue('favorites' in favs)

    def test_get_user_contacts(self):
        api = slideshare.SlideshareAPI(API_KEY,SHARED_SECRET)
        contacts = api.get_user_contacts(USERNAME)
        self.assertTrue('Contacts' in contacts)


    def test_get_user_tags(self):
        api = slideshare.SlideshareAPI(API_KEY,SHARED_SECRET)
        tags = api.get_user_tags(USERNAME, PASSWORD)
        self.assertTrue('Tags' in tags)

    def test_edit_slideshow(self):
        # you will have to substitute sl_id
        # with a slideshow_id you are allowed to edit
        sl_id = '21834196'
        api = slideshare.SlideshareAPI(API_KEY,SHARED_SECRET)
        sls = api.edit_slideshow(USERNAME, PASSWORD, sl_id,
            slideshow_title="Python Slideshare API",
            slideshow_description = 'Python API for slideshare reinvented',
            slideshow_tags = 'python, plone, ',
            )
        self.assertEqual(sls['SlideShowEdited']['SlideShowID'], sl_id)


    def test_upload_and_delete_slideshow(self):
        api = slideshare.SlideshareAPI(API_KEY,SHARED_SECRET)
        url = 'https://github.com/cleder/slideshare/blob/master/slideshare/test1.odp?raw=true'
        ts = datetime.now().isoformat()
        sls = api.upload_slideshow(USERNAME, PASSWORD,
                slideshow_title = 'Python Slideshare API Test %s' % ts,
                upload_url=url,
                slideshow_description = 'Python API for slideshare reinvented',
                slideshow_tags = 'python')
        sl_id = sls['SlideShowUploaded']['SlideShowID']
        sls = api.delete_slideshow(USERNAME, PASSWORD, sl_id)
        self.assertEqual(sls['SlideShowDeleted']['SlideshowID'], sl_id)
        f = open('slideshare/test1.odp')
        ts = datetime.now().isoformat()
        sls = api.upload_slideshow(USERNAME, PASSWORD,
                'Python Slideshare API Test %s' % ts,
                slideshow_srcfile={
                'filename': 'yat%s.odf' % ts,
                'mimetype':'application/vnd.oasis.opendocument.presentation',
                'filehandle': f,
                })
        sl_id = sls['SlideShowUploaded']['SlideShowID']
        sls = api.delete_slideshow(USERNAME, PASSWORD, sl_id)
        self.assertEqual(sls['SlideShowDeleted']['SlideshowID'], sl_id)

    def test_add_favorite(self):
        api = slideshare.SlideshareAPI(API_KEY,SHARED_SECRET)
        sl_id = '21834196'
        sls = api.add_favorite(USERNAME, PASSWORD, sl_id)
        self.assertEqual(sls['Slideshow']['SlideshowID'], sl_id)


    def test_check_favorite(self):
        api = slideshare.SlideshareAPI(API_KEY,SHARED_SECRET)
        sl_id = '21834196'
        sls = api.check_favorite(USERNAME, PASSWORD, sl_id)
        self.assertEqual(sls['Slideshow']['SlideshowID'], sl_id)


    def test_get_user_campaigns(self):
        api = slideshare.SlideshareAPI(API_KEY,SHARED_SECRET)
        campaign = api.get_user_campaigns(USERNAME, PASSWORD)
        self.assertTrue('Campaigns' in campaign)

    def test_get_user_leads(self):
        api = slideshare.SlideshareAPI(API_KEY,SHARED_SECRET)
        lead = api.get_user_leads(USERNAME, PASSWORD)
        self.assertTrue('Leads' in lead)

    def test_get_user_campaign_leads(self):
        api = slideshare.SlideshareAPI(API_KEY,SHARED_SECRET)
        #untested only available in pro version
        pass


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BasicTestCase))
    return suite

if __name__ == '__main__':
    unittest.main()
