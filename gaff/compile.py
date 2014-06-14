'''compile.py -- Gaff world compiler'''

import mwparserfromhell as parser

import gaff.world
import gaff.log

import sys
from datetime import datetime
import traceback

class TemplateDict (dict): 
    def gettext (self, k, d = None):
        if k in self: return self[k].strip()
        return d

    @classmethod
    def from_template (self, template):
        return TemplateDict({p.name.strip():p.value for p in template.params})


class WorldCompiler (object):
    def __init__ (self, api, log=None):
        self.api = api
        if log: self.log = log
        else: self.log = gaff.log.EventLogger()

    def compile (self):
        self.log.info ('Starting compile.')
        world = gaff.world.World ()
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
        character = gaff.world.Character()
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
        item = gaff.world.Item()
        for obj_name, params in source:
            if obj_name == 'Infobox Item':
                item.name = params.gettext('name')
                item.inventoryTooltip = params.gettext('inventory-tooltip')
                item.inventoryIcon = params.gettext('inventory-icon')
                if item.inventoryIcon and not item.inventoryIcon in imageRefs:
                    imageRefs[item.inventoryIcon] = None
        return item

    def compile_scene (self, title, source, imageRefs):
        self.log.info ('Processing scene: %s' % title)
        scene = gaff.world.Scene ()
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
                interaction = gaff.world.SceneInteraction ()

                # Extract general metadata
                interaction.overlayImage = params.gettext('overlay-image')
                if interaction.overlayImage and not interaction.overlayImage in imageRefs:
                    imageRefs[interaction.overlayImage] = None
                interaction.name = params.gettext('name')
                interaction.linkedItem = params.gettext('linked-item')
                interaction.linkedCharacter = params.gettext('linked-character')
                interaction.defaultAction = params.gettext('default-action')
                interaction.defaultState = params.gettext('default-state')
                
                # Compile action mappings
                mapTalk = params.get('action-talk')
                mapTake = params.get('action-take')
                mapUse = params.get('action-use')
                mapInspect = params.get('action-inspect')
                mapApply = params.get('action-apply')
                if mapTalk:
                    interaction.actionMappings['Talk'] = self.compile_action_map (mapTalk)
                if mapTake:
                    interaction.actionMappings['Take'] = self.compile_action_map (mapTake)
                if mapUse:
                    interaction.actionMappings['Use'] = self.compile_action_map (mapUse)
                if mapInspect:
                    interaction.actionMappings['Inspect'] = self.compile_action_map (mapInspect)
                if mapApply:
                    interaction.actionMappings['Apply'] = self.compile_action_map (mapApply)
                if not (mapTalk or mapUse or mapInspect or mapTake or mapApply):
                    self.log.warning ('Scene interaction %s has no action maps.' % interaction.name)

                paramActions = params.get('actions')
                if paramActions:
                    paramActionsTemplates = paramActions.filter_templates(recursive=False)
                    if not len(paramActionsTemplates) == 1:
                        self.log.warning ('Skipping SceneInteraction[%s].actions parameter: expected 1 template, got %i.' % (interaction.name,len(paramActionsTemplates)))
                    else:
                        actionsTemplate = paramActionsTemplates[0]
                        if not actionsTemplate.name.strip() == 'Actions':
                            self.log.warning ('Skipping SceneInteraction[%s].actions parameter: does not contain an Actions template.' % interaction.name)
                        actions = self.compile_actions (actionsTemplate)
                        interaction.actions = actions

                paramStates = params.get('states')
                if paramStates:
                    paramStatesTemplates = paramStates.filter_templates(recursive=False)
                    if not len(paramStatesTemplates) == 1:
                        self.log.warning ('Skipping SceneInteraction[%s].states: expected 1 template in parameter, got %i.' % (interaction.name,len(paramStatesTemplates)) )
                    else:
                        statesTemplate = paramStatesTemplates[0]
                        if not statesTemplate.name.strip() == 'States':
                            self.log.warning ('Skipping SceneInteraction[%s].states: parameter does not contain a States template.' % interaction.name)
                        else:
                            states = self.compile_interaction_states (statesTemplate, imageRefs)
                            interaction.states = states
                else:
                    self.log.error ('SceneInteraction[%s] contains no states.' % interaction.tooltip)

                scene.interactions.append (interaction)
        return scene

    def compile_interaction_states (self, statesTemplate, imageRefs):
        '''Compile a dict of names to InteractionStates from a States template.

        Arguments:
         statesTemplate -- Source for a States template.
         imageRefs -- Dict of image references in compile job.
        '''

        states = []
        catchallExists = False
        nInaccessible = 0
        for param in statesTemplate.params:
            paramName = param.name.strip()
            paramValue = param.value
            paramTemplates = paramValue.filter_templates(recursive=False)
            if not len(paramTemplates) == 1:
                self.log.error ('Skipping State parameter %s: expected 1 template in value, got %i.' % (paramName, len(paramTemplates)))
                continue
            stateTemplate = paramTemplates[0]
            stateTemplateName = stateTemplate.name.strip()
            if not stateTemplateName == 'State':
                self.log.error ('Skipping State parameter %s: parameter does not contain a State template.')
                continue
            if catchallExists: nInaccessible += 1
            state = self.compile_interaction_state (stateTemplate, paramName, imageRefs)
            if not state.condition: catchallExists = True
            states.append (state)
        if nInaccessible:
            self.log.warning ('%i states are inaccessible due to an earlier catchall state.' % nInaccessible)
        return states

    def compile_interaction_state (self, stateTemplate, stateName, imageRefs):
        '''Compile an InteractionState from a State template.

        Arguments
         stateTemplate -- Source for a State template.
        '''

        state = gaff.world.InteractionState()
        state.name = stateName
        params = TemplateDict.from_template(stateTemplate)
        state.condition = params.gettext('condition')
        state.tooltip = params.gettext('tooltip')
        state.enabled = params.gettext('enabled') == 'yes'
        state.visible = params.gettext('visible') == 'yes'
        state.image = params.gettext('image')
        if state.image and not state.image in imageRefs:
            imageRefs[state.image] = None
        try:
            # Determine interaction region
            # Regions are specified as edge positions
            state.region = [
                int(params.gettext('left')),
                int(params.gettext('top')),
                int(params.gettext('right'))-int(params.gettext('left')),
                int(params.gettext('bottom'))-int(params.gettext('top'))
            ]
        except:
            pass # Some interactions (e.g. items already taken) won't have regions

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

        action = gaff.world.Action()

        for param in actionTemplate.params:
            paramTemplates = param.value.filter_templates (recursive=False)
            if not len(paramTemplates) == 1:
                self.log.warning ('Expected 1 template in Action parameter, got %i. Skipping.' % len(paramTemplates))
                continue
            cmdTemplate = paramTemplates[0]
            cmd = None
            cmdTemplateName = cmdTemplate.name.strip()
            if cmdTemplateName == 'Narrate':
                cmd = gaff.world.CommandNarrate()
                cmd.content = cmdTemplate.get(1).strip()
            elif cmdTemplateName == 'MoveTo':
                cmd = gaff.world.CommandMoveTo()
                cmd.destination = cmdTemplate.get(1).strip()
            elif cmdTemplateName == 'Grant':
                cmd = gaff.world.CommandGrant()
                cmd.flag = cmdTemplate.get(1).strip()
            elif cmdTemplateName == 'Take':
                cmd = gaff.world.CommandTake()
                cmd.item = cmdTemplate.get(1).strip()
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
        
        params = TemplateDict.from_template(template)
        if len(params) == 0:
            self.log.warning ('Created an empty action map.')
            return []

        actions = []
        verb = params.gettext('verb')
        connective = params.gettext('connective')

        # Track how many actions will be inaccessible due to catchall conditions
        nInaccessible = 0
        catchallExists = False

        for param in template.params:
            # Ignore the named parameters
            paramName = param.name.strip()
            if paramName == 'verb' or paramName == 'connective': continue

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

            if catchallExists:
                nInaccessible += 1

            action = gaff.world.ActionMapping ()
            whenParams = TemplateDict.from_template(tmpl_when)
            action.item = whenParams.gettext('item')
            action.condition = whenParams.gettext('condition')
            action.action = whenParams.gettext('action')
            # We'll add support for contextual verbs and connectives later...
            action.verb = verb
            action.connective = connective

            if not action.condition:
                catchallExists = True
                action.condition = None

            actions.append(action)

        if nInaccessible:
            self.log.warning ('%i mapped actions are inaccessible due to an earlier catchall condition.' % nInaccessible)

        return actions

    def compile_dialogue (self, source):
        '''Construct a Dialogue object from a Dialogue wiki template.'''

        dialogue = gaff.world.Dialogue ()
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
        line = gaff.world.DialogueLine()
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
        jump = gaff.world.DialogueJump()
        jump.target = source.get(1).strip()
        return jump

    def compile_dialogue_grant (self, source):
        '''Construct a CommandGrant from a Grant wiki template.'''

        name = source.name.strip()
        if not name == 'Grant':
            raise ValueError ('Expected "Grant" template, got %s' % name)
        if not len(source.params) == 1:
            raise ValueError ('Grant template must have exactly 1 argument, got %i' % len(source.params))
        grant = gaff.world.CommandGrant()
        grant.flag = source.get(1).strip()
        return grant

    def compile_dialogue_prompt (self, source):
        '''Construct a DialoguePrompt from a Prompt wiki template.'''

        name = source.name.strip()
        if not name == 'Prompt':
            raise ValueError ('Expected "Prompt" template, got %s' % name)
        prompt = gaff.world.DialoguePrompt()

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

            option = gaff.world.DialogueOption()
            opt_params = TemplateDict.from_template(tmpl)
            option.label = opt_params.gettext ('label')
            option.condition = opt_params.gettext ('condition')
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
            params = TemplateDict.from_template(template)
            yield (name, params)

