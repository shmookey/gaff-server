'''world.py -- Data objects for Gaff worlds'''

class Character (object):
    def __init__ (self):
        self.name = None
        self.tooltip = None
        self.image = None
        self.dialogues = []

class Dialogue (object):
    def __init__ (self):
        self.name = None
        self.lines = []

class DialogueLine (object):
    def __init__ (self):
        self.speaker = None
        self.content = None

class DialogueOption (object):
    def __init__ (self):
        self.label = None
        self.result = []

class DialoguePrompt (object):
    def __init__ (self):
        self.options = []

class Item (object):
    def __init__ (self):
        self.name = None
        self.inventoryTooltip = None
        self.inventoryIcon = None
        self.examineImage = None

class Scene (object):
    def __init__ (self):
        self.name = None
        self.region = None
        self.bgImage = None
        self.interactions = []

class SceneInteraction (object):
    def __init__ (self):
        self.region = None
        self.linkedItem = None
        self.tooltip = None
        self.defaultAction = None

class World (object):
    def __init__ (self):
        self.scenes = []
        self.characters = []
        self.items = []

