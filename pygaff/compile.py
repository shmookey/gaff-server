'''compile.py -- Gaff world compiler'''

import mwparserfromhell as parser

import pygaff.world
import pygaff.log

import sys
from datetime import datetime
import traceback

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

        try:
            world.scenes = self.compile_all_scenes(imageRefs)
            world.characters = self.compile_all_characters(imageRefs)
            world.items = self.compile_all_items(imageRefs)
            self.link (imageRefs)
            world.imageRefs = imageRefs
        except Exception as e:
            self.log.error ('Fatal error during compilation: unhandled exception.')
            tb_lines = traceback.format_exc().strip().split('\n')
            for line in tb_lines: self.log.debug (line)
            
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
                character.speechColor = params.gettext('speech-color')
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
                    scene.indoors = params.gettext('indoors','no') == 'yes'
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

                # Determine interaction region
                # Regions are specified as edge positions
                try:
                    interaction.region = [
                        int(params.gettext('left')),
                        int(params.gettext('top')),
                        int(params.gettext('right'))-int(params.gettext('left')),
                        int(params.gettext('bottom'))-int(params.gettext('top'))
                    ]
                except:
                    self.log.error ('Could not extract interaction region.')

                # Extract general metadata
                interaction.overlayImage = params.gettext('overlay-image')
                if interaction.overlayImage and not interaction.overlayImage in imageRefs:
                    imageRefs[interaction.overlayImage] = None
                interaction.tooltip = params.gettext('tooltip')
                interaction.linkedItem = params.gettext('linked-item')
                interaction.defaultAction = params.gettext('default-action')
                interaction.linkedCharacter = params.gettext('linked-character')
                
                # Compile action mappings
                paramActionMapTalk = params.get('action-talk')
                paramActionMapUse = params.get('action-use')
                paramActionMapInspect = params.get('action-inspect')
                if paramActionMapTalk:
                    interaction.actionMappings['Talk'] = self.compile_action_map (paramActionMapTalk)
                if paramActionMapUse:
                    interaction.actionMappings['Use'] = self.compile_action_map (paramActionMapUse)
                if paramActionMapInspect:
                    interaction.actionMappings['Inspect'] = self.compile_action_map (paramActionMapInspect)
                if not (paramActionMapTalk or paramActionMapUse or paramActionMapInspect):
                    self.log.warning ('Scene interaction with tooltip %s has no action maps.' % interaction.tooltip)

                paramActions = params.get('actions')
                if paramActions:
                    paramActionsTemplates = paramActions.filter_templates(recursive=False)
                    if not len(paramActionsTemplates) == 1:
                        self.log.warning ('Skipping SceneInteraction.actions parameter: expected 1 template, got %i.' % len(paramActionsTemplates))
                    else:
                        actionsTemplate = paramActionsTemplates[0]
                        if not actionsTemplate.name.strip() == 'Actions':
                            self.log.warning ('Skipping SceneInteraction.actions parameter: does not contain an Actions template.')
                        actions = self.compile_actions (actionsTemplate)
                        interaction.actions = actions

                paramStates = params.get('states')
                if paramStates:
                    paramStatesTemplates = paramStates.filter_templates(recursive=False)
                    if not len(paramStatesTemplates) == 1:
                        self.log.warning ('Skipping SceneInteraction.states: expected 1 template in parameter, got %i.' % len(paramStatesTemplates) )
                    else:
                        statesTemplate = paramStatesTemplates[0]
                        if not statesTemplate.name.strip() == 'States':
                            self.log.warning ('Skipping SceneInteraction.states: parameter does not contain a States template.')
                        else:
                            states = self.compile_interaction_states (statesTemplate, imageRefs)
                            interaction.states = states
                else:
                    self.log.warning ('Interaction with tooltip %s contains no states.' % interaction.tooltip)

                scene.interactions.append (interaction)
        return scene

    def compile_interaction_states (self, statesTemplate, imageRefs):
        '''Compile a dict of names to InteractionStates from a States template.

        Arguments:
         statesTemplate -- Source for a States template.
         imageRefs -- Dict of image references in compile job.
        '''

        states = {}
        for param in statesTemplate.params:
            paramName = param.name.strip()
            paramValue = param.value
            paramTemplates = paramValue.filter_templates(recursive=False)
            if not len(paramTemplates) == 1:
                self.log ('Skipping State parameter %s: expected 1 template in value, got %i.' % (paramName, len(paramTemplates)))
                continue
            stateTemplate = paramTemplates[0]
            stateTemplateName = stateTemplate.name.strip()
            if not stateTemplateName == 'State':
                self.log ('Skipping State parameter %s: parameter does not contain a State template.')
                continue
            state = self.compile_interaction_state (stateTemplate, imageRefs)
            states[paramName] = state
        return states

    def compile_interaction_state (self, stateTemplate, imageRefs):
        '''Compile an InteractionState from a State template.

        Arguments
         stateTemplate -- Source for a State template.
        '''

        state = pygaff.world.InteractionState()
        state.tooltip = stateTemplate.get('tooltip').value.strip()
        state.image = stateTemplate.get('image').value.strip()
        if state.image and not state.image in imageRefs:
            imageRefs[state.image] = None
        try:
            state.region = [
                int(stateTemplate.get('left').value.strip()),
                int(stateTemplate.get('top').value.strip()),
                int(stateTemplate.get('right').value.strip())-int(stateTemplate.get('left').value.strip()),
                int(stateTemplate.get('bottom').value.strip())-int(stateTemplate.get('top').value.strip())
            ]
        except:
            self.log.error ('Could not extract interaction state region.')
        return state

    def compile_actions (self, actionsTemplate):
        '''Compile an Actions map from an Actions template.

        Arguments
         actionsTemplate -- Source for an Actions template.
        '''

        actions = {}
        for param in actionsTemplate.params:
            actionName = param.name.strip()
            paramTemplates = param.value.filter_templates (recursive=False)
            if not len(paramTemplates) == 1:
                self.log.warning ('Expected 1 template in Actions parameter value, got %i. Skipping.' % len(paramTemplates))
                continue
            actionTemplate = paramTemplates[0]
            if not actionTemplate.name.strip() == 'Action':
                self.log.warning ('Actions parameter value does not contain an Action template. Skipping.')
                continue
            action = self.compile_action (actionTemplate)
            actions[actionName] = action
        return actions

    def compile_action (self, actionTemplate):
        '''Compile an action definition from an Action template.

        An Action template contains a list of command templates.

        Arguments
         actionTemplate -- Source for an Action template.
        '''

        action = pygaff.world.Action()

        for param in actionTemplate.params:
            paramTemplates = param.value.filter_templates (recursive=False)
            if not len(paramTemplates) == 1:
                self.log.warning ('Expected 1 template in Action parameter, got %i. Skipping.' % len(paramTemplates))
                continue
            cmdTemplate = paramTemplates[0]
            cmd = None
            cmdTemplateName = cmdTemplate.name.strip()
            if cmdTemplateName == 'Narrate':
                cmd = pygaff.world.CommandNarrate()
                cmd.content = cmdTemplate.get(1).strip()
            elif cmdTemplateName == 'MoveTo':
                cmd = pygaff.world.CommandMoveTo()
                cmd.destination = cmdTemplate.get(1).strip()
            else:
                self.log.warning ('Unknown Action command "%s" in command template list. Skipping.' % cmdTemplateName)
                continue
            action.commands.append (cmd)

        return action

    def compile_action_map (self, source):
        '''Construct a list of ActionMappings from an ActionMap wiki template.
        
        Arguments
         source -- Contents of action-map argument to SceneInteraction
        '''

        # Look for templates inside the provided action-map argument source
        templates = source.filter_templates(recursive=False)
        if len(templates) == 0:
            self.log.error ('Argument action-map appears to contain no templates.')
            return []
        elif len(templates) > 1:
            self.log.warning ('Ignoring extraneous data in action-map argument (found %i extra templates).' % len(templates))

        # Extract the ActionMap template from the action-map argument
        template = templates[0]
        tmpl_name = template.name.strip()
        if not tmpl_name == 'ActionMap':
            self.log.error ('Argument action-map contains unexpected template %s' % tmpl_name)
            return []
        if len(template.params) == 0:
            self.log.warning ('Created an empty action map.')
            return []

        actions = []
        for param in template.params:
            # Ignore the 'name' parameter for now
            if param.name.strip() == 'name': continue
            # Each numbered param should contain a single 'When' template
            child_source = param.value
            child_templates = child_source.filter_templates(recursive=False)
            if len(child_templates) == 0:
                self.log.warning ('Skipping ActionMap argument containing no templates (expecting a "When" template)')
                continue
            if len(child_templates) > 1:
                self.log.warning ('Skipping extraneous data in ActionMap argument (expecting a single "When" template)')
                continue
            tmpl_when = child_templates[0]
            tmpl_when_name = tmpl_when.name.strip()
            if not tmpl_when_name == 'When':
                self.log.warning ('Skipping ActionMap argument containing unexpected template (expected "When", got "%s")' % tmpl_when_name)
                continue

            action = pygaff.world.ActionMapping ()
            action.condition = tmpl_when.get(1).strip()
            action.action = tmpl_when.get(2).strip()
            actions.append(action)

        return actions

    def compile_dialogue (self, source):
        '''Construct a Dialogue object from a Dialogue wiki template.'''

        dialogue = pygaff.world.Dialogue ()
        dialogue.name = source.gettext ('name')
        lines_source = source.get('lines').filter_templates(recursive=False)[0]
        dialogue.lines = self.compile_dialogue_lines (lines_source)
        return dialogue

    def compile_dialogue_lines (self, source):
        '''Construct a list of DialogueLines from a Lines wiki template.'''

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
            elif tmplname == 'Jump':
                jump = self.compile_dialogue_jump (tmpl)
                lines.append (jump)
            elif tmplname == 'Grant':
                grant = self.compile_dialogue_grant (tmpl)
                lines.append (grant)
            else:
                self.log.warning ('Unknown directive in dialogue lines: %s' % tmplname)
        return lines
                        
    def compile_dialogue_line (self, source):
        '''Construct a DialogueLine from a Line wiki template.'''

        name = source.name.strip()
        if not name == 'Line':
            raise ValueError ('Expected "Line" template, got %s' % name)
        if not len(source.params) == 2:
            raise ValueError ('Line template must have 2 arguments, got %i' % len(source.params))
        line = pygaff.world.DialogueLine()
        line.speaker = source.get(1).strip()
        line.content = source.get(2).strip()
        return line

    def compile_dialogue_jump (self, source):
        '''Construct a DialogueJump from a Jump wiki template.'''

        name = source.name.strip()
        if not name == 'Jump':
            raise ValueError ('Expected "Jump" template, got %s' % name)
        if not len(source.params) == 1:
            raise ValueError ('Jump template must have exactly 1 argument, got %i' % len(source.params))
        jump = pygaff.world.DialogueJump()
        jump.target = source.get(1).strip()
        return jump

    def compile_dialogue_grant (self, source):
        '''Construct a DialogueGrant from a Grant wiki template.'''

        name = source.name.strip()
        if not name == 'Grant':
            raise ValueError ('Expected "Grant" template, got %s' % name)
        if not len(source.params) == 1:
            raise ValueError ('Grant template must have exactly 1 argument, got %i' % len(source.params))
        grant = pygaff.world.DialogueGrant()
        grant.flag = source.get(1).strip()
        return grant

    def compile_dialogue_prompt (self, source):
        '''Construct a DialoguePrompt from a Prompt wiki template.'''

        name = source.name.strip()
        if not name == 'Prompt':
            raise ValueError ('Expected "Prompt" template, got %s' % name)
        prompt = pygaff.world.DialoguePrompt()

        for prompt_param in source.params:
            if prompt_param.name.strip() == 'name':
                # This is the named argument 'name' on the prompt template
                prompt.name = prompt_param.value.strip()
                continue
            
            # Assume that all other parameters are Options
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

