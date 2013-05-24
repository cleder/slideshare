# -*- coding: utf-8 -*-
import unittest

try:
    from .secret import API_KEY, SHARED_SECRET, USERNAME, PASSWORD
except:
    API_KEY = SHARED_SECRET = USERNAME = PASSWORD = None
import slideshare


class BasicTestCase(unittest.TestCase):

    def test_get_slideshow(self):
        api = slideshare.SlideshareAPI(API_KEY,SHARED_SECRET)
        #get slideshow by id
        sls = api.get_slideshow(slideshow_id='21730465')
        self.assertEqual(sls['Slideshow']['ID'], '21730465')
        sls = api.get_slideshow(slideshow_url=
            "http://www.slideshare.net/iwlpcu/gef-iw-community-platform-101")
        self.assertEqual(sls['Slideshow']['ID'], '21730465')

    def test_get_slideshows_by_tag(self):
        api = slideshare.SlideshareAPI(API_KEY,SHARED_SECRET)
        sls = api.get_slideshows_by_tag('water')
        self.assertEqual(sls['Tag']['Name'], 'water')
        self.assertFalse(sls['Tag']['Count'] == '0')


    def test_get_slideshows_by_group(self):
        api = slideshare.SlideshareAPI(API_KEY,SHARED_SECRET)

    def test_get_slideshows_by_user(self):
        api = slideshare.SlideshareAPI(API_KEY,SHARED_SECRET)
        sls = api.get_slideshows_by_user(USERNAME)
        self.assertEqual(sls['User']['Name'], USERNAME)

    def test_search_slideshows(self):
        api = slideshare.SlideshareAPI(API_KEY,SHARED_SECRET)
        sls = api.search_slideshows(q='water')
        self.assertEqual(sls['Slideshows']['Meta']['Query'], 'water')
        self.assertFalse(sls['Slideshows']['Meta']['TotalResults'] == '0')

    def test_get_user_groups(self):
        api = slideshare.SlideshareAPI(API_KEY,SHARED_SECRET)
    def test_get_user_favorites(self):
        api = slideshare.SlideshareAPI(API_KEY,SHARED_SECRET)
    def test_get_user_contacts(self):
        api = slideshare.SlideshareAPI(API_KEY,SHARED_SECRET)
    def test_get_user_tags(self):
        api = slideshare.SlideshareAPI(API_KEY,SHARED_SECRET)
    def test_edit_slideshow(self):
        api = slideshare.SlideshareAPI(API_KEY,SHARED_SECRET)
    def test_delete_slideshow(self):
        api = slideshare.SlideshareAPI(API_KEY,SHARED_SECRET)
    def test_upload_slideshow(self):
        api = slideshare.SlideshareAPI(API_KEY,SHARED_SECRET)
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



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BasicTestCase))
    return suite

if __name__ == '__main__':
    unittest.main()
