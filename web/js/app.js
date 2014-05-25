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
    var controller = ['$scope', 'WorldMap', function($scope, WorldMap) {
        WorldMap.loadMap ('initial');
    }];
    return {
        restrict: 'E',
        scope: true,
        controller: controller,
    }
});

