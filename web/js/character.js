function CharacterNotFound(name){this.characterName=name;}
CharacterNotFound.prototype = GaffException;

game.service ('Character', function () {
    var self = this;
    this.characters = null;

    this.onLoad = function (characterData) {
        /* Initialise world data. */

        self.characters = characterData;
    };

    this.get = function (name) {
        /* Return a character object by name. */

        if (!self.characters)
            throw new ServiceNotReady ('Character');

        if (!self.characters[name])
            throw new CharacterNotFound (name);
       
        return self.characters[name];
    };

    return this;
});
