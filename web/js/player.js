game.service ('Player', ['Scene', function(Scene) {
    var self = this;
    var reTokens = new RegExp (/[^ &|()!]+/g);

    this.scene = null;
    this.progressFlags = [];

    this.goToScene = function (scene) {
        /* Go to the specified scene. */

        self.scene = scene;
        Scene.set (scene);
    };

    this.leaveScene = function () {
        /* Leave the current scene. */

        self.scene = null;
        Scene.clear ();
    };

    this.grantFlag = function (flag) {
        /* Grant the specified progress flag to the player. */

        if (self.progressFlags.indexOf(flag) == -1)
            self.progressFlags.push (flag);
    };

    this.hasFlag = function (flag) {
        /* Check whether a player has been granted the specified progress flag. */

        return self.progressFlags.indexOf(flag) != -1;
    };

    this.evaluateCondition = function (condition) {
        /* Safely evaluate a flag-based boolean condition. */

        // Replace all non-operator elements with 0 or 1
        var tokens = condition.match(reTokens);
        for (var i=0; i<tokens.length; i++) {
            var token = tokens[i];
            var value = '0';
            if (self.hasFlag(token)) value = '1';
            condition = condition.replace(token, value);
        }
        return eval (condition);
    };

    return this;
}]);
