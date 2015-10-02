(function(){
    angular.module('pyjobs', [])

    .factory('$websocket', function(){
        return function(){
            return new WebSocket('ws://localhost:8888/ws');
        };
    })

    .controller('pyjobsMain', ['$scope', '$timeout', '$websocket',
    function($scope, $timeout, $websocket){
        $scope.jobs = [];
        $scope.status = 0;

        var ws = $websocket();
        ws.onopen = function onopen(){
            console.debug('connection opened');
            $timeout(function(){
                $scope.status = 1;
            }, 0);
            ws.send(angular.toJson({'cmd': 'search'}))
        };

        ws.onclose = function(){
            console.debug('connection closed');
            $timeout(function(){
                $scope.status = 0;
            }, 0);
        }

        ws.onmessage = function(message){
            var response = angular.fromJson(message.data);
            $timeout(function(){
                $scope.jobs = $scope.jobs.concat(response.data);
                console.debug(response.data);
            }, 0);
//            console.debug('Message: ', message.data);
        };

        $scope.sendMessage = function(message){
            console.debug(ws, message);
            ws.send(message);
        }

    }]);
})();