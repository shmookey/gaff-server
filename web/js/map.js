game.service ('WorldMap', ['$document', 'World', function($document, World) {
    var self = this;
    this.mapName = '';
    
    // 'map' attributes contain coordinates relative to the original map
    // they are not affected by the current zoom level
    this.mapSize = {width:0,height:0};
    this.mapViewport = {x1:0,y1:0,x2:0,y2:0};
    
    // 'screen' attributes contain coordinates relative to the map as rendered
    // they ARE affected by the current zoom level
    this.screenSize = {width:0,height:0};
    this.screenViewport = {x1:0,y1:0,x2:0,y2:0};
    this.viewportRestricted = false;

    this.zoomScale = 1; // Scale factor: xMap = xScreen * zoomScale
    this.zoomLevel = 1;
    this.zoomMax = 1;

    this.locations = [];

    this.screenSize.width = $document[0].documentElement.clientWidth;
    this.screenSize.height = $document[0].documentElement.clientHeight;

    this.loadMap = function (mapName) {
        var map = World[mapName];
        self.mapName = mapName;
        self.mapSize.width = map.size.width;
        self.mapSize.height = map.size.height;
        self.zoomLevel = map.zoomStart;
        self.zoomMax = map.zoomMax;
        self.zoomScale = Math.pow(2,self.zoomMax-self.zoomLevel);
        self.mapViewport.x1 = map.panStart.x;
        self.mapViewport.y1 = map.panStart.y;
        self.mapViewport.x2 = map.panStart.x + self.screenSize.width*self.zoomScale;
        self.mapViewport.y2 = map.panStart.y + self.screenSize.height*self.zoomScale;
        self.screenViewport.x1 = self.mapViewport.x1 / self.zoomScale;
        self.screenViewport.y1 = self.mapViewport.y1 / self.zoomScale;
        self.screenViewport.x2 = self.mapViewport.x2 / self.zoomScale;
        self.screenViewport.y2 = self.mapViewport.y2 / self.zoomScale;
        self.viewportRestricted = map.viewportRestricted;
        self.locations = angular.copy(map.locations);
        self.updateLocations ();
    };

    this.onPan = function (x, y) {
        /* Update the map after a pan event, takes screen coordinates. */
        self.setScreenPan (x, y);
    };

    this.onZoom = function (level, x, y) {
        /* Update the map after a zoom event. */
        self.zoomLevel = level;
        self.zoomScale = Math.pow(2,self.zoomMax-level);
        self.setScreenPan (x, y);
    };

    this.onResize = function () {
        console.log ('resize! ' + arguments);
    };

    this.recalculateMapCoords = function () {
        /* Updates map coords based on screen coords and zoom level. */
        self.mapViewport.x1 = self.screenViewport.x1 * self.zoomScale;
        self.mapViewport.x2 = self.screenViewport.x2 * self.zoomScale;
        self.mapViewport.y1 = self.screenViewport.y1 * self.zoomScale;
        self.mapViewport.y2 = self.screenViewport.y2 * self.zoomScale;
    };

    this.setScreenPan = function (x, y) {
        /* Set the pan relative to the screen and triggers a refresh. */
        self.screenViewport.x1 = x;
        self.screenViewport.y1 = y;
        self.screenViewport.x2 = x + self.screenSize.width;
        self.screenViewport.y2 = y + self.screenSize.height;
        self.recalculateMapCoords ();
        self.updateLocations ();
    };

    this.updateLocations = function () {
        var scale = self.zoomScale;
        var viewport = self.mapViewport;
        for (var i=0; i<self.locations.length; i++) {
            var loc = self.locations[i];
            loc.screenRegion = [
                (loc.region[0] - viewport.x1) * scale,
                (loc.region[1] - viewport.y1) * scale,
                loc.region[2] * scale,
                loc.region[3] * scale,
            ];
        }
    };

    return this;
}]);

game.directive ('map', function () {
    var controller = ['$scope','WorldMap',function($scope,WorldMap){
        $scope.$watch(function(){return WorldMap.locations;},function(locations) {
            $scope.locations = locations;
        });
    }];

    return {
        restrict: 'E',
        templateUrl: 'partials/map.html',
        controller: controller,
        scope: true,
    };
});

