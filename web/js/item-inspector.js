game.service ('ItemInspector', [function () {
    var self = this;

    this.item = null;

    this.inspect = function (item) {
        this.item = item;
    };

    this.close = function () {
        this.item = null;
    };

    return this;
}]);

game.directive ('itemInspector', function () {
    var controller = ['$scope', 'ItemInspector', 'Debugger', function ($scope, ItemInspector, Debugger) {
        $scope.imageStyle = null;
        $scope.visible = false;

        $scope.$watch(function(){return ItemInspector.item;}, function(item) {
            if (item) {
                $scope.imageStyle = {
                    'background-image': 'url(images/items/closeups/' + item.closeUpImage + ')',
                };
                $scope.visible = true;
                $scope.features = item.features;
            } else {
                $scope.imageStyle = null;
                $scope.visible = false;
            }
        });

        $scope.dismiss = function () {
            ItemInspector.close ();
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
        templateUrl: 'partials/item-inspector.html',
        scope: {
            item: '=ngModel',
        },
    };
});

