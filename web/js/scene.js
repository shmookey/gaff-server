game.service ('Scene', [function () {
    var self = this;

    this.name = null;
    this.interactions = null;
    this.bgImage = null;
    this.bgSize = null;
    this.config = null;  // Ref to source data

    this.active = false;

    this.set = function (scene) {
        self.config = scene;
        self.interactions = scene.interactions;
        self.name = scene.name;
        self.bgImage = scene.bgImage;
        self.bgSize = scene.bgSize;
        self.active = true;
    };

    this.clear = function () {
        self.config = null;
        self.interactions = null;
        self.name = null;
        self.bgImage = null;
        self.bgSize = null;
        self.active = false;
    }

    return this;
}]);

game.directive ('scene', function () {
    var controller = ['$scope', 'WorldMap', 'Scene', 'Player', 'Assets', 'Debugger',
      function ($scope, WorldMap, Scene, Player, Assets, Debugger) {
        $scope.visible = false;
        $scope.imageStyle = null;
        $scope.interactions = null;

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
            } else {
                $scope.visible = false;
                $scope.imageStyle = null;
            }
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

