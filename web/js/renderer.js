game.directive ('renderer', function () {
    var viewer, viewerElement;

    var link = function (scope, element, attrs) {
        viewerElement = element[0];
    };
    
    var controller = ['$scope', '$rootScope', 'WorldMap', function ($scope, $rootScope, WorldMap) {
        $scope.$watch(function(){return WorldMap.mapName;},function(mapName){
            if (!WorldMap.mapName) return;
            if (WorldMap.viewportRestricted) {
                PanoJS.restricted = true;
                PanoJS.CREATE_INFO_CONTROLS = false;
                PanoJS.CREATE_CONTROLS = false;
                PanoJS.CREATE_THUMBNAIL_CONTROLS = false;
            }
            PanoJS.MSG_BEYOND_MIN_ZOOM = null;
            PanoJS.MSG_BEYOND_MAX_ZOOM = null;
            PanoJS.USE_SLIDE = false;
            PanoJS.MAX_OVER_ZOOM = 0;
            viewer = new PanoJS(viewerElement, {
                tileBaseUri     : 'images/maps/tiles',
                tilePrefix      : mapName + '-',
                tileSize        : 256,
                imageWidth      : WorldMap.mapSize.width,
                imageHeight     : WorldMap.mapSize.height,
                initialPan      : {
                    x: WorldMap.screenViewport.x1,
                    y: WorldMap.screenViewport.y1
                },
                initialZoom     : WorldMap.zoomLevel,
                maxZoom         : WorldMap.zoomMax,
                tileExtension   : 'png',
                blankTile       : 'lib/panojs/images/blank.gif',
                loadingTile     : 'lib/panojs/images/progress.gif'
            });
            if (!viewer.maximized) viewer.toggleMaximize();
            viewer.init();
            Ext.EventManager.addListener (window, 'resize', callback (viewer, viewer.resize));
            Ext.EventManager.addListener (window, 'resize', callback (WorldMap, WorldMap.onResize));
            viewer.addViewerMovedListener ($scope.viewportListener);
            viewer.addViewerZoomedListener ($scope.viewportListener);
        });

        $scope.viewportListener = {
            viewerMoved: function (position) {
                WorldMap.onPan (-position.x, -position.y);
                if (!$rootScope.$$phase) $scope.$apply();
            },
            viewerZoomed: function (zoom) {
                WorldMap.onZoom (zoom.level, zoom.x, zoom.y);
                if (!$rootScope.$$phase) $scope.$apply();
            },
        };
    }];

    return {
        restrict: 'E',
        link: link,
        controller: controller,
        scope: true,
    }
});

