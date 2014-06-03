var game = angular.module ('game',[]);

game.directive('ngRightClick', function($parse) {
    return function(scope, element, attrs) {
        var fn = $parse(attrs.ngRightClick);
        element.bind('contextmenu', function(event) {
            scope.$apply(function() {
                event.preventDefault();
                fn(scope, {$event:event});
            });
        });
    };
});

game.directive ('game', function() {
    var link = function (scope, element, attrs) {
        $('.toolbar button').tooltip({container:'.toolbar'});
    };

    var controller = ['$scope', '$http', 'World', 'WorldMap', 'Assets', 'Character', 'Debugger',
      function($scope, $http, World, WorldMap, Assets, Character, Debugger) {
        $scope.debugEnabled = Debugger.enabled;

        $http.get('api/world').success(function(data) {
            World.data = data;
            Assets.imageRefs = data.imageRefs;
            WorldMap.loadMap ('initial');
            Character.onLoad (data.characters);
        });

        $scope.toggleDebugger = function () {
            $scope.debugEnabled = Debugger.enabled = !Debugger.enabled;
        };
    }];
    return {
        restrict: 'E',
        scope: true,
        controller: controller,
        link: link,
    }
});

