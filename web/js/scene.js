game.service ('Scene', [function () {
    var self = this;
    var narrationTimeout = null;

    this.name = null;
    this.interactions = null;
    this.bgImage = null;
    this.bgSize = null;
    this.config = null;    // Ref to source data
    this.narration = null; // Narrative text on-screen
    this.indoors = null;   // Is the scene indoors (no quick escape to map)

    this.active = false;

    this.set = function (scene) {
        self.config = scene;
        self.interactions = scene.interactions;
        self.name = scene.name;
        self.bgImage = scene.bgImage;
        self.bgSize = scene.bgSize;
        self.active = true;
        self.narration = null;
        self.indoors = scene.indoors;
        if (self.narrationTimeout) self.narrationTimeout();
        self.narrationTimeout = null;
    };

    this.clear = function () {
        self.config = null;
        self.interactions = null;
        self.name = null;
        self.bgImage = null;
        self.bgSize = null;
        self.active = false;
        self.narration = null;
        self.indoors = null;
        if (self.narrationTimeout) self.narrationTimeout();
        self.narrationTimeout = null;
    };

    this.narrate = function (content) {
        self.narration = content;
        narrationTimeout = $timeout(function() {
            self.narration = null;
        }, 2000);
    };

    return this;
}]);

game.directive ('scene', function () {
    var controller = ['$scope', 'WorldMap', 'Scene', 'Player', 'Assets', 'Debugger',
      function ($scope, WorldMap, Scene, Player, Assets, Debugger) {
        $scope.visible = false;
        $scope.imageStyle = null;
        $scope.interactions = null;
        $scope.narrative = null;
        $scope.indoors = false;

        $scope.$watch (function(){return Scene.name;}, function(name) {
            if (Scene.active) {
                $scope.visible = true;
                var imageURI = Assets.getImageURI (Scene.bgImage);
                $scope.imageStyle = {
                    'background-image': 'url(' + imageURI + ')',
                    'width': Scene.bgSize[0] + 'px',
                    'height': Scene.bgSize[1] + 'px',
                    'margin-left': (-Scene.bgSize[0]/2) + 'px',
                    'margin-top': (-Scene.bgSize[1]/2) + 'px',
                };
                $scope.interactions = Scene.interactions;
                if (Scene.indoors) $scope.indoors = true;
                else $scope.indoors = false;
            } else {
                $scope.visible = false;
                $scope.imageStyle = null;
            }
        });

        $scope.$watch (function(){return Scene.narration;}, function(narration) {
            $scope.narration = narration;
        });

        $scope.dismiss = function () {
            Player.leaveScene ();
        };

        $scope.onMouseMove = function (evt) {
            if (!$scope.visible) return;
            Debugger.mousePositionRelative = [evt.offsetX, evt.offsetY];
        };
    }];

    return {
        restrict: 'E',
        controller: controller,
        replace: true,
        templateUrl: '/partials/scene.html',
        scope: {},
    };
});

