game.service ('Scene', [function () {
    var self = this;

    this.name = null;
    this.items = null;
    this.bgImage = null;
    this.config = null;  // Ref to source data

    this.active = false;

    this.set = function (scene) {
        self.config = scene;
        self.items = scene.items;
        self.name = scene.name;
        self.bgImage = scene.bgImage;
        self.active = true;
    };

    this.clear = function () {
        self.config = null;
        self.items = null;
        self.name = null;
        self.bgImage = null;
        self.active = false;
    }

    return this;
}]);

game.directive ('scene', function () {
    var controller = ['$scope', 'WorldMap', 'Scene', 'Player', 'Debugger',
      function ($scope, WorldMap, Scene, Player, Debugger) {
        $scope.visible = false;
        $scope.imageStyle = null;
        $scope.items = null;

        $scope.$watch (function(){return Scene.name;}, function(name) {
            if (Scene.active) {
                $scope.visible = true;
                $scope.imageStyle = {
                    'background-image': 'url(images/scenes/' + Scene.bgImage + ')',
                };
                $scope.items = Scene.items;
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

