#!/usr/bin/python

import json

import requests

import pygaff.world
import pygaff.log

class WikiAPI (object):
    def __init__ (self, uri, username, password, log=None):
        self.username = username
        self.password = password
        self.uri = uri
        self.session = requests.Session()
        if log: self.log = log
        else: self.log = pygaff.log.EventLogger()

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

class WorldJSONExporter (object):
    def __init__ (self, world):
        self.world = world

    def export_dialogue (self, dialogue):
        return {
            'event': 'dialogue',
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
                'name': line.name,
                'options': [{
                    'label': option.label,
                    'result': [self.export_dialogue_line(line) for line in option.result],
                } for option in line.options],
            }
        elif isinstance(line, pygaff.world.DialogueJump):
            return {
                'event': 'jump',
                'target': line.target,
            }
        elif isinstance(line, pygaff.world.DialogueGrant):
            return {
                'event': 'grant',
                'flag': line.flag,
            }
        raise TypeError ('Lines must be of Dialogue event type, not %s' % type(line))
    
    def export_command (self, command):
        if isinstance(command, pygaff.world.CommandNarrate):
            return {
                'event': 'narrate',
                'content': command.content
            }
        elif isinstance(command, pygaff.world.CommandMoveTo):
            return {
                'event': 'moveto',
                'destination': command.destination,
            }
        raise TypeError ('Unknown type for command: %s' % type(command))
 
    def to_obj (self):
        world = self.world
        obj = {
            'mapName': world.mapName,
            'image': world.image,
            'size': world.size,
            'panStart': world.panStart,
            'zoomStart': world.zoomStart,
            'zoomMax': world.zoomMax,
            'viewportRestricted': world.viewportRestricted,
            'imageRefs': world.imageRefs,
            'scenes': {scene.name: {
                'name': scene.name,
                'mapRegion': scene.mapRegion,
                'bgImage': scene.bgImage,
                'bgSize': scene.bgSize,
                'indoors': scene.indoors,
                'interactions': [{
                    'region': interaction.region,
                    'tooltip': interaction.tooltip,
                    'linkedItem': interaction.linkedItem,
                    'linkedCharacter': interaction.linkedCharacter,
                    'defaultAction': interaction.defaultAction,
                    'overlayImage': interaction.overlayImage,
                    'actionMappings': {actionType: [{
                            'condition': actionMapping.condition,
                            'action': actionMapping.action,
                        } for actionMapping in actionMappings
                    ] for (actionType, actionMappings) in interaction.actionMappings.items()},
                    'actions': {actionName: 
                        [self.export_command(command) for command in action.commands]
                    for (actionName, action) in interaction.actions.items()},
                    'states': {stateName: {
                        'tooltip': state.tooltip,
                        'image': state.image,
                        'region': state.region,
                    } for (stateName, state) in interaction.states.items()},
                } for interaction in scene.interactions]
            } for scene in world.scenes},
            'characters': {character.name: {
                'name': character.name,
                'tooltip': character.tooltip,
                'image': character.image,
                'speechColor': character.speechColor,
                'dialogues': {dialogue.name: self.export_dialogue(dialogue) for dialogue in character.dialogues},
            } for character in world.characters},
            'items': [{
                'name': item.name,
                'inventoryTooltip': item.inventoryTooltip,
                'inventoryIcon': item.inventoryIcon,
                'examineImage': item.examineImage,
            } for item in world.items],
        }
        return obj

    def to_string (self):
        obj = self.to_obj()
        return json.dumps(obj, sort_keys=True, indent=2)

