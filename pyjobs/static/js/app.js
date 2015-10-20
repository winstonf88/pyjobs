(function(){
    angular.module('pyjobs', [])

    .factory('$websocket', function(){
        return function(){
            return new WebSocket('ws://localhost:8888/ws');
        };
    })

    .filter('conStatus', function(){
        var conStatus = {
            0: 'offline',
            1: 'searching',
            2: 'done'
        };
        return function(status){
            return (conStatus[status] || '');
        };
    })

    .directive('btnConStatus', function(){
        return {
            restrict: 'A',
            scope: {btnConStatus: '='},
            link: function($scope, $element){
                var conStatus = {
                    0: 'label-danger',
                    1: 'label-warning',
                    2: 'label-success'
                };
                $scope.$watch('btnConStatus', function(newStatus, oldStatus){
                    console.debug('status', newStatus, oldStatus);
                    $element.removeClass(conStatus[oldStatus]);
                    $element.addClass(conStatus[newStatus]);
                });
            }
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
                $scope.status = 'connected';
            }, 0);
            ws.send(angular.toJson({'cmd': 'search'}));
        };

//        ws.onclose = function(){
//            console.debug('connection closed');
//            $timeout(function(){ $scope.status = 0; }, 0);
//        }

        ws.onmessage = function(message){
            var response = angular.fromJson(message.data);
            $timeout(function(){
                if (response.type == 'data')
                    $scope.jobs = $scope.jobs.concat(response.data);
                else if(response.type == 'status')
                    $scope.status = response.data;

                console.debug(response.data);
            }, 0);
        };

        $scope.sendMessage = function(message){
            console.debug(ws, message);
            ws.send(message);
        }

    }]);
})();