var app = angular.module ('compiler',['ngSanitize']);

app.directive ('compiler', function() {
    var controller = ['$scope', '$http', function($scope, $http) {
        $scope.events = [];
        $scope.output = ['Compiling...'];
        var SEVERITY = {
            1000: 'INFO',
            1001: 'ERROR',
            1002: 'WARNING',
            1003: 'DEBUG',
        };
        $http.get('api/compile').success(function(data) {
            for (var i=0; i<data.log.length; i++) {
                var row = data.log[i];
                var evt = {
                    timestamp: row[0],
                    severity: SEVERITY[row[1]],
                    message: row[2],
                };
                $scope.events.push(evt);
            }
            var lines = data.output.split('\n');
            for (var i=0; i<lines.length; i++) {
                lines[i] = lines[i].replace (/"([^"]+)":/,'"<span class="field-name">$1</span>":');
                lines[i] = lines[i].replace (/: "([^"]+)"/,': "<span class="string">$1</span>"');
                lines[i] = lines[i].replace (/: ([0-9.-]+)/,': <span class="number">$1</span>');
                lines[i] = lines[i].replace (/: null/,': <span class="null">null</span>');
                lines[i] = lines[i].replace (/: \[/, ': <span class="array">[</span>');
                lines[i] = lines[i].replace (/(\])(, )?$/,'<span class="array">$1</span>$2');
                lines[i] = lines[i].replace (/{$/,'<span class="brace">{</span>');
                lines[i] = lines[i].replace (/}(, )?$/,'<span class="brace">}</span>$1');
                lines[i] = lines[i].replace (/([0-9.-]+)(, )?$/,'<span class="number">$1</span>$2');
                //var parts = line.split (':');
                //if (parts.length > 1) {
                //    var field = parts[0];
                //    var val = parts[
                //    parts[0] = field.replace (/"([^"]*)"/,'<span class="field-name">$1</span>');
                //}
            }
            $scope.output = lines;
        });
    }];
    return {
        restrict: 'E',
        scope: true,
        controller: controller,
        templateUrl: 'partials/compiler.html',
    }
});

