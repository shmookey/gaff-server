game.service ('Debugger', ['WorldMap', function(WorldMap) {
    this.showRegions = false;
    this.mousePositionRelative = [0,0];
    this.mousePositionScreen = [0,0];
    this.enabled = false;

    this.onMouseMove = function (event) {
        //this.mousePositionScene = WorldMap.screenToMapCoords(event.xy);
        //this.mousePositionMap = WorldMap.screenToMapCoords(event.xy);
    };

    return this;
}]);

game.directive ('debugger', function() {
    var controller = ['$scope', 'WorldMap', 'Debugger', function ($scope, WorldMap, Debugger) {
        var watches = [];
        $scope.visible = false;

        $scope.$watch(function(){return Debugger.enabled;}, function(enabled) {
            $scope.visible = enabled;
            if (enabled) setUpWatches ();
            else cancelWatches ();
        });
        
        function setUpWatches () {
            watches.push($scope.$watch(function(){return WorldMap.mapViewport;}, function(mapViewport) {
                $scope.mapViewport = mapViewport;
            }, true));
            watches.push($scope.$watch(function(){return WorldMap.screenViewport;}, function(screenViewport) {
                $scope.screenViewport = screenViewport;
            }, true));
            watches.push($scope.$watch(function(){return WorldMap.screenSize;}, function(screenSize) {
                $scope.screenSize = screenSize;
            }, true));
            watches.push($scope.$watch(function(){return WorldMap.mapSize;}, function(mapSize) {
                $scope.mapSize = mapSize;
            }, true));
            watches.push($scope.$watch(function(){return WorldMap.zoomLevel;}, function(zoomLevel) {
                $scope.zoomLevel = zoomLevel;
            }, true));
            watches.push($scope.$watch(function(){return WorldMap.zoomScale;}, function(zoomScale) {
                $scope.zoomScale = zoomScale;
            }, true));
            watches.push($scope.$watch(function(){return Debugger.mousePositionRelative;}, function(position) {
                $scope.mousePositionRelative = position;
            }, true));
        }

        function cancelWatches () {
            for (var i=0; i<watches.length; i++) {
                var cancelFn = watches[i];
                cancelFn();
            }
            watches = [];
        }

        // Methods
        $scope.setRegionDisplay = function (isEnabled) {
            Debugger.showRegions = isEnabled;
        };

    }];

    return {
        restrict: 'E',
        replace: true,
        templateUrl: '/partials/debugger.html',
        controller: controller,
    };
});

