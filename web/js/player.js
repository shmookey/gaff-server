game.service ('Player', ['Scene', function(Scene) {
    var self = this;

    this.scene = null;

    this.goToScene = function (scene) {
        self.scene = scene;
        Scene.set (scene);
    }

    this.leaveScene = function () {
        self.scene = null;
        Scene.clear ();
    }

    return this;
}]);
