#!/usr/bin/python

import json
import requests

import pygaff.world

class WikiAPI (object):
    def __init__ (self, uri, username, password):
        self.username = username
        self.password = password
        self.uri = uri
        self.session = requests.Session()

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
            raise ValueError ('Unexpected login result: %s' % result)
        token = response['login']['token']
        params['lgtoken'] = token
        req = self.session.post(self.uri, params=params)
        result = req.json()['login']['result']
        if not result == 'Success':
            raise ValueError ('Unexpected login result (using token): %s' % result)
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
        return req.json()

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
        if contents:
            return response['query']['pages'].values()
        else:
            return response['query']['categorymembers']

class WorldJSONExporter (object):
    def __init__ (self, world):
        self.world = world

    def export_dialogue (self, dialogue):
        return {
            'name': dialogue.name,
            'lines': [self.export_dialogue_line(line) for line in dialogue.lines],
        }

    def export_dialogue_line (self, line):
        if isinstance(line, pygaff.world.DialogueLine):
            return {
                'event': 'line',
                'speaker': line.speaker,
                'content': line.content,
            }
        elif isinstance(line, pygaff.world.DialoguePrompt):
            return {
                'event': 'prompt',
                'options': [{
                    'label': option.label,
                    'result': [self.export_dialogue_line(line) for line in option.result],
                } for option in line.options],
            }
        raise TypeError ('Lines must be of "DialogueLine" or "DialoguePrompt" type, not %s' % type(line))
                            
    def to_string (self):
        world = self.world
        obj = {
            'scenes': [{
                'name': scene.name,
                'region': scene.region,
                'bgImage': scene.bgImage,
                'interactions': [{
                    'region': interaction.region,
                    'tooltip': interaction.tooltip,
                    'linkedItem': interaction.linkedItem,
                    'defaultAction': interaction.defaultAction,
                } for interaction in scene.interactions]
            } for scene in world.scenes],
            'characters': [{
                'name': character.name,
                'tooltip': character.tooltip,
                'image': character.image,
                'dialogues': [self.export_dialogue(dialogue) for dialogue in character.dialogues],
            } for character in world.characters],
            'items': [{
                'name': item.name,
                'inventoryTooltip': item.inventoryTooltip,
                'inventoryIcon': item.inventoryIcon,
                'examineImage': item.examineImage,
            } for item in world.items],
        }
        return json.dumps(obj, sort_keys=True, indent=4)

