'''compile.py -- Gaff world compiler'''

import mwparserfromhell as parser

import pygaff.world
import pygaff.log

import sys
from datetime import datetime

class CustomDict (dict): 
    def gettext (self, k, d = None):
        if k in self: return self[k].strip()
        return d

class WorldCompiler (object):
    def __init__ (self, api, log=None):
        self.api = api
        if log: self.log = log
        else: self.log = pygaff.log.EventLogger()

    def compile (self):
        self.log.info ('Starting compile.')
        world = pygaff.world.World ()
        imageRefs = {}

        world_dump = self.api.get_page_content ('The_World')
        world_objects = self.parse_objects (world_dump)
        for obj_name, params in world_objects:
            if obj_name == 'Infobox World':
                world.size = [
                    int(params.gettext('map-width')),
                    int(params.gettext('map-height')),
                ]
                world.panStart = [
                    int(params.gettext('map-start-x')),
                    int(params.gettext('map-start-y')),
                ]
                world.mapName = params.gettext('map-name')
                world.image = params.gettext('image')
                if not world.image in imageRefs:
                    imageRefs[world.image] = None
                world.zoomMax = int(params.gettext('zoom-max'))
                world.zoomStart = int(params.gettext('zoom-start'))
                world.viewportRestricted = params.gettext('viewport-restricted') == 'yes'

        world.scenes = self.compile_all_scenes(imageRefs)
        world.characters = self.compile_all_characters(imageRefs)
        world.items = self.compile_all_items(imageRefs)
        
        self.link (imageRefs)
        world.imageRefs = imageRefs
        return world

    def link (self, imageRefs):
        '''Check references and discover external resource URLs.'''

        # Check URLs
        unresolvedImages = ['File:%s'%name.replace(' ','_') for (name, url) in imageRefs.items() if not url]
        url_data = self.api.get_image_urls (unresolvedImages)
        for record in url_data:
            name = record['title'][5:].replace(' ','_') # Strip off 'File:'
            if not name in imageRefs:
                self.log.warning ('Unexpected image resource: %s' % name)
            try:
                imageRefs[name] = record['imageinfo'][0]['url']
            except KeyError:
                self.log.warning ('Unable to resolve URL for image resource %s' % name)

    def compile_all_scenes (self, imageRefs):
        scenes = []
        scene_dump = self.api.get_category_members ('Category:Scenes', contents=True)
        self.log.info ('Discovered %i scenes' % len(scene_dump))
        for scene_data in scene_dump:
            scene_objects = self.parse_objects (scene_data)
            scene = self.compile_scene (scene_data['title'], scene_objects, imageRefs)
            scenes.append (scene)
        return scenes

    def compile_all_characters (self, imageRefs):
        characters = []
        character_dump = self.api.get_category_members ('Category:Characters', contents=True)
        self.log.info ('Discovered %i characters' % len(character_dump))
        for character_data in character_dump:
            character_objects = self.parse_objects (character_data)
            character = self.compile_character (character_data['title'], character_objects, imageRefs)
            characters.append (character)
        return characters

    def compile_all_items (self, imageRefs):
        items = []
        item_dump = self.api.get_category_members ('Category:Items', contents=True)
        self.log.info ('Discovered %i items' % len(item_dump))
        for item_data in item_dump:
            item_objects = self.parse_objects (item_data)
            item = self.compile_item (item_data['title'], item_objects, imageRefs)
            items.append (item)
        return items

    def compile_character (self, title, source, imageRefs):
        self.log.info ('Processing character: %s' % title)
        character = pygaff.world.Character()
        for obj_name, params in source:
            if obj_name == 'Infobox Character':
                character.name = params.gettext('name')
                character.tooltip = params.gettext('tooltip')
                character.image = params.gettext('image')
                if character.image and not character.image in imageRefs:
                    imageRefs[character.image] = None
            elif obj_name == 'Dialogue':
                dialogue = self.compile_dialogue (params)
                character.dialogues.append (dialogue)
        return character

    def compile_item (self, title, source, imageRefs):
        self.log.info ('Processing item: %s' % title)
        item = pygaff.world.Item()
        for obj_name, params in source:
            if obj_name == 'Infobox Item':
                item.name = params.gettext('name')
                item.inventoryTooltip = params.gettext('inventory-tooltip')
                item.inventoryIcon = params.gettext('inventory-icon')
                if item.inventoryIcon and not item.inventoryIcon in imageRefs:
                    imageRefs[item.inventoryIcon] = None
                item.examineImage = params.gettext('examine-image')
                if item.examineImage and not item.examineImage in imageRefs:
                    imageRefs[item.examineImage] = None
        return item

    def compile_scene (self, title, source, imageRefs):
        self.log.info ('Processing scene: %s' % title)
        scene = pygaff.world.Scene ()
        for obj_name, params in source:
            if obj_name == 'Infobox Scene':
                scene.name = params.gettext('name')
                if params.gettext('visitable') == 'yes':
                    scene.bgImage = params.gettext('bg-image')
                    if scene.bgImage and not scene.bgImage in imageRefs:
                        imageRefs[scene.bgImage] = None
                    scene.bgSize = [
                        int(params.gettext('bg-width')),
                        int(params.gettext('bg-height')),
                    ]
                if params.gettext('mapped') == 'yes':
                    scene.mapRegion = [
                        int(params.gettext('map-x')),
                        int(params.gettext('map-y')),
                        int(params.gettext('map-width')),
                        int(params.gettext('map-height')),
                    ]
                    scene.tooltip = params.gettext ('tooltip', scene.name)
            elif obj_name == 'Scene Interaction':
                interaction = pygaff.world.SceneInteraction ()
                try:
                    interaction.region = [
                        int(params.gettext('left')),
                        int(params.gettext('top')),
                        int(params.gettext('right'))-int(params.gettext('left')),
                        int(params.gettext('bottom'))-int(params.gettext('top'))
                    ]
                except:
                    self.log.error ('Could not extract interaction region.')
                interaction.overlayImage = params.gettext('overlay-image')
                if interaction.overlayImage and not interaction.overlayImage in imageRefs:
                    imageRefs[interaction.overlayImage] = None
                interaction.tooltip = params.gettext('tooltip')
                interaction.linkedItem = params.gettext('linked-item')
                interaction.defaultAction = params.gettext('default-action')
                interaction.linkedCharacter = params.gettext('linked-character')
                scene.interactions.append (interaction)
        return scene

    def compile_dialogue (self, source):
        dialogue = pygaff.world.Dialogue ()
        dialogue.name = source.gettext ('name')
        lines_source = source.get('lines').filter_templates(recursive=False)[0]
        dialogue.lines = self.compile_dialogue_lines (lines_source)
        return dialogue

    def compile_dialogue_lines (self, source):
        lines = []
        name = source.name.strip()
        if not name == 'Lines':
            raise ValueError ('Expected "Lines" template, got %s' % name)
        for param in source.params:
            tmpl = param.value.filter_templates(recursive=False)[0]
            tmplname = tmpl.name.strip()
            if tmplname == 'Line':
                line = self.compile_dialogue_line (tmpl)
                lines.append (line)
            elif tmplname == 'Prompt':
                prompt = self.compile_dialogue_prompt (tmpl)
                lines.append (prompt)
        return lines
                        
    def compile_dialogue_line (self, source):
        name = source.name.strip()
        if not name == 'Line':
            raise ValueError ('Expected "Line" template, got %s' % name)
        if not len(source.params) == 2:
            raise ValueError ('Line template must have 2 arguments, got %i' % len(source.params))
        line = pygaff.world.DialogueLine()
        line.speaker = source.get(1).strip()
        line.content = source.get(2).strip()
        return line

    def compile_dialogue_prompt (self, source):
        name = source.name.strip()
        if not name == 'Prompt':
            raise ValueError ('Expected "Prompt" template, got %s' % name)
        prompt = pygaff.world.DialoguePrompt()
        for prompt_param in source.params:
            tmpl = prompt_param.value.filter_templates(recursive=False)[0]
            tmplname = tmpl.name.strip()
            if not tmplname == 'Option':
                raise ValueError ('Expected "Option" template, got %s' % tmplname)
            option = pygaff.world.DialogueOption()
            option.label = tmpl.get('label').value.strip()
            result = tmpl.get('result').value.filter_templates(recursive=False)[0]
            lines = self.compile_dialogue_lines (result)
            option.result = lines
            prompt.options.append (option)
        return prompt

    def parse_objects (self, source):
        '''Extract template parameter objects from the wikitext markup.'''
        code = parser.parse(source['revisions'][0]['*'])
        templates = code.filter_templates()
        for template in templates:
            name = template.name.strip()
            params = CustomDict({p.name.strip():p.value for p in template.params})
            yield (name, params)

