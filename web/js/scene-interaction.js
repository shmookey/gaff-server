game.service ('SceneInteraction', ['Player', 'Character', 'Dialogue', 'ItemInspector', function(Player, Character, Dialogue, ItemInspector) {
    this.activate = function (interaction) {
        var actionMap = interaction.actions[interaction.defaultAction];

        // Run the action for the first mapping condition that passes
        for (var i=0; i<actionMap.length; i++) {
            var mapping = actionMap[i];
            if (!Player.evaluateCondition (mapping.condition)) continue;
            var action = mapping.action.split ('::');
            
            if (action[0] == 'Talk') {
                var character = Character.get(interaction.linkedCharacter);
                var dialogueName = action[1];
                Dialogue.beginDialogue (character, dialogueName, interaction);
            }
            return;
        }
        console.log ('No passing action mappings found!');
    };

    return this;
}]);

game.directive ('sceneInteraction', function () {
    var link = function (scope, element, attrs) {
        $(element).tooltip({title: scope.model.tooltip});
    };

    var controller = ['$scope', 'SceneInteraction', 'Assets', 'Debugger', function ($scope, SceneInteraction, Assets, Debugger) {
        $scope.css = {
            left: "0px",
            top: "0px",
            width: "0px",
            height: "0px"
        };
        $scope.showRegion = false;
        
        if ($scope.model.overlayImage) {
            var imageURI = Assets.getImageURI ($scope.model.overlayImage);
            $scope.css['background-image'] = 'url(' + imageURI + ')';
        }

        $scope.$watch(function(){return $scope.model.region;}, function(region) {
            $scope.css['left'] = region[0] + "px";
            $scope.css['top'] = region[1] + "px";
            $scope.css['width'] = region[2] + "px";
            $scope.css['height'] = region[3] + "px";
        }, true);

        $scope.$watch(function(){return Debugger.showRegions;}, function (showRegion) {
            $scope.showRegion = showRegion;
        });

        $scope.onClick = function () {
            SceneInteraction.activate($scope.model);
        };
    }];

    return {
        restrict: 'E',
        controller: controller,
        link: link,
        replace: true,
        templateUrl: 'partials/scene-interaction.html',
        scope: {
            model: '=ngModel',
        },
    };
});

