'''api.py -- Wikimedia API
'''

import requests

import gaff.log

class WikiAPI (object):
    def __init__ (self, uri, username, password, log=None):
        self.username = username
        self.password = password
        self.uri = uri
        self.session = requests.Session()
        if log: self.log = log
        else: self.log = gaff.log.EventLogger()

    def login (self):
        params = {
            'action': 'login',
            'format': 'json',
            'lgname': self.username,
            'lgpassword': self.password,
        }
        req = self.session.post(self.uri, params=params)
        response = req.json()
        result = response['login']['result']
        if result == 'Success': return req
        if not result == 'NeedToken':
            self.log.error ('Unexpected login result: %s' % result)
            raise ValueError ('Unexpected login result: %s' % result)
        token = response['login']['token']
        params['lgtoken'] = token
        req = self.session.post(self.uri, params=params)
        result = req.json()['login']['result']
        if not result == 'Success':
            self.log.error ('Unexpected login result (using token): %s' % result)
            raise ValueError ('Unexpected login result (using token): %s' % result)
        self.log.debug ('Logged in to wiki successfully.')
        return req

    def get_page_content (self, title):
        params = {
            'action': 'query',
            'format': 'json',
            'titles': title,
            'prop': 'revisions',
            'rvprop': 'content',
        }
        req = self.session.get(self.uri, params=params)
        return req.json()['query']['pages'].values()[0]

    def get_category_members (self, category_name, contents=False):
        if contents:
            params = {
                'action': 'query',
                'format': 'json',
                'generator': 'categorymembers',
                'gcmtitle': category_name,
                'prop': 'revisions',
                'rvprop': 'content',
            }
        else:
            params = {
                'action': 'query',
                'format': 'json',
                'list': 'categorymembers',
                'cmtitle': category_name,
            }
        req = self.session.get(self.uri, params=params)
        response = req.json()
        self.log.debug ('Retrieved category members for %s' % category_name)
        if contents:
            return response['query']['pages'].values()
        else:
            return response['query']['categorymembers']

    def get_image_urls (self, image_names):
        self.log.debug ('Getting URLs for %i images' % len(image_names))
        params = {
            'action': 'query',
            'format': 'json',
            'prop': 'imageinfo',
            'iiprop': 'url',
            'titles': '|'.join([i.replace(' ','_') for i in image_names]),
        }
        req = self.session.get(self.uri, params=params)
        response = req.json()
        imgdata = response['query']['pages'].values()
        self.log.debug ('Found %i image URLs' % len(imgdata))
        return imgdata

