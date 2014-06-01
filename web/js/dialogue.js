game.service ('Dialogue', ['Character', function (Character) {
    var self = this;

    this.character = null;
    this.tree = null;
    this.activeLines = null;

    this.beginDialogue = function (character, dialogueName) {
        this.character = character;
        this.tree = character.dialogues[dialogueName];
        this.activeLines = [];
    };

    this.endDialogue = function () {
        this.character = null;
        this.tree = null;
        this.activeLines = null;
    };

    return this;
}]);

game.directive ('dialogue', function () {
    var controller = ['$scope', 'Dialogue', function ($scope, Dialogue) {
        var unwatchLines = null;
        var unwatchPrompt = null;

        $scope.lines = null;
        $scope.prompt = null;
        $scope.visible = false;
        
        $scope.$watch(function(){return Dialogue.character;}, function (character) {
            // The character being spoken to has changed (possibly to no one)

            if (!character) {
                // No active dialogue, clear scope and cancel watches

                if (unwatchLines) unwatchLines();
                if (unwatchPrompt) unwatchPrompt();
                unwatchLines = unwatchPrompt = null;
                $scope.visible = false;
                return;
            }

            $scope.visible = true;

            // Set up watches
            unwatchLines = $scope.$watch(function(){return Dialogue.activeLines;}, onLinesChange, true);
            unwatchPrompt = $scope.$watch(function(){return Dialogue.prompt;}, onPromptChange, true);
        });

        function onLinesChange (lines) {
            // The active lines have changed, format them for display

            $scope.lines = [];
            if (!lines) return;
            for (var i=0; i<lines.length; i++) {
                var line = lines[i];
                var displayLine = {content: line.content, style: {}};
                if (line.speaker == 'Player') {
                    displayLine.style.color = 'yellow';
                    displayLine.style.bottom = '30px';
                }
                $scope.lines.push (displayLine);
            }
        }

        function onPromptChange (prompt) {
            // Current prompt options have changed, format them for display

        }
    }];

    return {
        restrict: 'E',
        replace: true,
        templateUrl: 'partials/dialogue.html',
        controller: controller,
    };
});
