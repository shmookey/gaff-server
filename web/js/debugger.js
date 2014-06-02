game.service ('Debugger', ['WorldMap', function(WorldMap) {
    this.showRegions = false;
    this.mousePositionRelative = [0,0];
    this.mousePositionScreen = [0,0];

    this.onMouseMove = function (event) {
        //this.mousePositionScene = WorldMap.screenToMapCoords(event.xy);
        //this.mousePositionMap = WorldMap.screenToMapCoords(event.xy);
    };

    return this;
}]);

game.directive ('debugger', function() {
    var controller = ['$scope', 'WorldMap', 'Debugger', function ($scope, WorldMap, Debugger) {
        // Watches
        $scope.$watch(function(){return WorldMap.mapViewport;}, function(mapViewport) {
            $scope.mapViewport = mapViewport;
        }, true);
        $scope.$watch(function(){return WorldMap.screenViewport;}, function(screenViewport) {
            $scope.screenViewport = screenViewport;
        }, true);
        $scope.$watch(function(){return WorldMap.screenSize;}, function(screenSize) {
            $scope.screenSize = screenSize;
        }, true);
        $scope.$watch(function(){return WorldMap.mapSize;}, function(mapSize) {
            $scope.mapSize = mapSize;
        }, true);
        $scope.$watch(function(){return WorldMap.zoomLevel;}, function(zoomLevel) {
            $scope.zoomLevel = zoomLevel;
        }, true);
        $scope.$watch(function(){return WorldMap.zoomScale;}, function(zoomScale) {
            $scope.zoomScale = zoomScale;
        }, true);
        $scope.$watch(function(){return Debugger.mousePositionRelative;}, function(position) {
            $scope.mousePositionRelative = position;
        }, true);

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

