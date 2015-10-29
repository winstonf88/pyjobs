(function(){
    angular.module('pyjobs', [])

    .factory('$websocket', function(){
        var dummy = function(){};

        function Socket(options){
            this.options = angular.extend(
                {onmessage: dummy, onclose: dummy, onerror: dummy, onclose: dummy},
                options
            );
            this.createConnection();
        }
        Socket.prototype = {
            createConnection: function(){
                if (!this.connection){
                    var self = this;
                    connection = new WebSocket('ws://localhost:8888/ws');
                    connection.onopen = function(){ self.onopen(); };
                    connection.onmessage = function(message){ self.onmessage(message); };
                    connection.onclose = function(){ self.onclose(); };
                    connection.onerror = function(){ self.onerror(); };
                    this.connection = connection;
                }
            },
            onopen: function(){
                this.options.onopen();
            },
            onclose: function(){
                this.connection = false;
                this.options.onclose();
                this.createConnection();
            },
            onerror: function(){
                this.options.onerror();
            },
            onmessage: function(message){
                var data = angular.fromJson(message.data);
                this.options.onmessage(data);
            },
            send: function(command, params){
                var query = angular.toJson({'cmd': command, 'params': params});
                console.debug(query);
                this.connection.send(query);

            },
            search: function(term, location){
                this.send('search', {'description': term, 'location': location});
            }
        }
        return function(options){
            return new Socket(options);
        };
    })

    .directive('btnConStatus', function(){
        return {
            restrict: 'A',
            scope: {btnConStatus: '='},
            link: function($scope, $element){
                var conStatus = {
                    'offline': 'label-danger',
                    'searching': 'label-warning',
                    'done': 'label-success'
                };
                $scope.$watch('btnConStatus', function(newStatus, oldStatus){
//                    console.debug('status', newStatus, oldStatus);
                    $element.removeClass(conStatus[oldStatus]);
                    $element.addClass(conStatus[newStatus]);
                });
            }
        };
    })

    .controller('pyjobsMain', ['$scope', '$timeout', '$websocket',
    function($scope, $timeout, $websocket){
        $scope.jobs = [];
        $scope.status = 'offline';

        var socketOptions = {
            onmessage: function(message){
                $timeout(function(){
                    if (message.type == 'data')
                        $scope.jobs = $scope.jobs.concat(message.data);
                    else if(message.type == 'status')
                        $scope.status = message.data;
                }, 0);
            },
            onopen: function(){
                if (!$scope.jobs.length)
                    $scope.search();
            }
        };
        var websocket = new $websocket(socketOptions);

        $scope.search = function(term, location){
            $scope.jobs = [];
            websocket.search(term, location);
        };
    }]);
})();