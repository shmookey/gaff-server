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
    var controller = ['$scope', '$http', 'World', 'WorldMap', 'Assets', 'Character', function($scope, $http, World, WorldMap, Assets, Character) {
        $http.get('api/world').success(function(data) {
            World.data = data;
            Assets.imageRefs = data.imageRefs;
            WorldMap.loadMap ('initial');
            Character.onLoad (data.characters);
        });
    }];
    return {
        restrict: 'E',
        scope: true,
        controller: controller,
    }
});

