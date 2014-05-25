'''compile.py -- Gaff world compiler'''

import mwparserfromhell as parser

import pygaff.world

class CustomDict (dict): 
    def gettext (self, k, d = None):
        if k in self: return self[k].strip()
        return d

class WorldCompiler (object):
    def __init__ (self, api):
        self.api = api

    def compile (self):
        world = pygaff.world.World ()
        world.scenes = self.compile_all_scenes()
        world.characters = self.compile_all_characters()
        world.items = self.compile_all_items()
        return world

    def compile_all_scenes (self):
        scenes = []
        scene_dump = self.api.get_category_members ('Category:Scenes', contents=True)
        print 'Discovered %i scenes' % len(scene_dump)
        for scene_data in scene_dump:
            scene_objects = self.parse_objects (scene_data)
            scene = self.compile_scene (scene_data['title'], scene_objects)
            scenes.append (scene)
        return scenes

    def compile_all_characters (self):
        characters = []
        character_dump = self.api.get_category_members ('Category:Characters', contents=True)
        print 'Discovered %i characters' % len(character_dump)
        for character_data in character_dump:
            character_objects = self.parse_objects (character_data)
            character = self.compile_character (character_data['title'], character_objects)
            characters.append (character)
        return characters

    def compile_all_items (self):
        items = []
        item_dump = self.api.get_category_members ('Category:Items', contents=True)
        print 'Discovered %i items' % len(item_dump)
        for item_data in item_dump:
            item_objects = self.parse_objects (item_data)
            item = self.compile_item (item_data['title'], item_objects)
            items.append (item)
        return items

    def compile_character (self, title, source):
        print '  Processing character: %s' % title
        character = pygaff.world.Character()
        for obj_name, params in source:
            if obj_name == 'Infobox Character':
                character.name = params.gettext('name')
                character.tooltip = params.gettext('tooltip')
                character.image = params.gettext('image')
            elif obj_name == 'Dialogue':
                dialogue = self.compile_dialogue (params)
                character.dialogues.append (dialogue)
        return character

    def compile_item (self, title, source):
        print '  Processing item: %s' % title
        item = pygaff.world.Item()
        for obj_name, params in source:
            if obj_name == 'Infobox Item':
                item.name = params.gettext('name')
                item.inventoryTooltip = params.gettext('inventory-tooltip')
                item.inventoryIcon = params.gettext('inventory-tooltip')
                item.examineImage = params.gettext('examine-image')
        return item

    def compile_scene (self, title, source):
        print '  Processing scene: %s' % title
        scene = pygaff.world.Scene ()
        for obj_name, params in source:
            if obj_name == 'Infobox Scene':
                scene.name = params.gettext('name')
                if params.gettext('visitable') == 'yes':
                    scene.bgImage = params.gettext('bg-image')
                if params.gettext('mapped') == 'yes':
                    scene.region = [
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
                except: pass
                interaction.tooltip = params.gettext('tooltip')
                interaction.linkedItem = params.gettext('linked-item')
                interaction.defaultAction = params.gettext('default-action')
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

