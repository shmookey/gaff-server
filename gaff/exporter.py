#!/usr/bin/python

import json

import gaff.world
import gaff.log

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
        if isinstance(line, gaff.world.DialogueLine):
            return {
                'event': 'line',
                'speaker': line.speaker,
                'content': line.content,
            }
        elif isinstance(line, gaff.world.DialoguePrompt):
            return {
                'event': 'prompt',
                'name': line.name,
                'options': [{
                    'label': option.label,
                    'condition': option.condition,
                    'result': [self.export_dialogue_line(line) for line in option.result],
                } for option in line.options],
            }
        elif isinstance(line, gaff.world.DialogueJump):
            return {
                'event': 'jump',
                'target': line.target,
            }
        elif isinstance(line, gaff.world.CommandGrant):
            return {
                'event': 'grant',
                'flag': line.flag,
            }
        raise TypeError ('Lines must be of Dialogue event type, not %s' % type(line))
    
    def export_command (self, command):
        if isinstance(command, gaff.world.CommandNarrate):
            return {
                'event': 'narrate',
                'content': command.content
            }
        elif isinstance(command, gaff.world.CommandMoveTo):
            return {
                'event': 'moveto',
                'destination': command.destination,
            }
        elif isinstance(command, gaff.world.CommandGrant):
            return {
                'event': 'grant',
                'flag': command.flag,
            }
        elif isinstance(command, gaff.world.CommandTake):
            return {
                'event': 'take',
                'item': command.item,
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
                    'name': interaction.name,
                    'linkedItem': interaction.linkedItem,
                    'linkedCharacter': interaction.linkedCharacter,
                    'defaultAction': interaction.defaultAction,
                    'defaultState': interaction.defaultState,
                    'overlayImage': interaction.overlayImage,
                    'actionMappings': {actionType: [{
                            'condition': actionMapping.condition,
                            'action': actionMapping.action,
                        } for actionMapping in actionMappings
                    ] for (actionType, actionMappings) in interaction.actionMappings.items()},
                    'actions': {actionName: 
                        [self.export_command(command) for command in action.commands]
                    for (actionName, action) in interaction.actions.items()},
                    'states': [{
                        'name': state.name,
                        'condition': state.condition,
                        'tooltip': state.tooltip,
                        'image': state.image,
                        'region': state.region,
                        'visible': state.visible,
                        'enabled': state.enabled,
                    } for state in interaction.states],
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
            } for item in world.items],
        }
        return obj

    def to_string (self):
        obj = self.to_obj()
        return json.dumps(obj, sort_keys=True, indent=2)

