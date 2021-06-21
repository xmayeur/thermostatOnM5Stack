let mqtt;
const reconnectTimeout = 2000;
const port = 9004;
const host = "192.168.0.17";
const topic = 'thermostat/state';
let data = {};
let week = [
    "lundi",
    "mardi",
    "mercredi",
    "jeudi",
    "vendredi",
    "samedi",
    "dimanche"
];
let temp = 1;
let schedule = [];
var app = angular.module('th', [])
    .controller('thCtrl', function ($scope, $rootScope, $timeout, $interval) {

        $scope.topic = topic;
        $scope.week = week;
        $scope.temp = temp;
        $scope.Schedule = schedule;

        $scope.isOpen = false;
        $scope.pind = -1;
        $scope.ind = -1;


        $scope.$watch('temp', function (newValue, oldValue) {
            $scope.temp = newValue;
            console.log(newValue, ' <- ', oldValue);
        });
        $scope.$watch('schedule', function (newValue, oldValue) {
            $scope.schedule = newValue;
            console.log(newValue, ' <- ', oldValue);
        });

        MQTTconnect();
        mqtt.onMessageArrived = onMessageArrived;


        // FUNCTIONS -----------------------------------------

        function onConnect() {
            console.log('connected!');
            mqtt.subscribe(topic);
        }

        function MQTTconnect() {
            console.log('connecting to mqtt server');
            mqtt = new Paho.MQTT.Client(host, port, 'clientJS');
            $.getScript("./password.js", function (username, pwd) {
                mqtt.connect({
                    onSuccess: onConnect,
                    userName: userName,
                    password: pwd
                });
            });


        }

        function onMessageArrived(message) {
            console.log('message arrived: ' + message.payloadString);
            data = JSON.parse(message.payloadString);
            console.log('temp: ' + String(data.curr_temp));
            $scope.temp = data.curr_temp;
            $scope.schedule = data.week_schedule;
            $scope.$apply();
            // Double Click Open Input Field
            $timeout(function () {
                $scope.$apply();
                $("td").dblclick(function () {
                    var p = $(this).parent().index();
                    var i = $(this).index();
                    var x = $(this);
                    openEdit(x);
                    setActiveCell(x, p, i);
                    addOnfocus();
                });
            }, 100);
            console.log('topic:           ' + message.destinationName);
            mqtt.subscribe(topic);
        }

        function setActiveCell(cell, p, i) {
            if ($scope.pind >= 0 && (p !== $scope.pind || i !== $scope.ind)) {
                $("tr").eq($scope.pind + 1).find("td").eq($scope.ind).find(".edit").remove();
            }
            $scope.pind = cell.parent().index();
            $scope.ind = cell.index();
            displayVals(p, i);
        }

        function openEdit(cell) {
            var type = cell.text();
            cell.append("<div class='edit'><input type='text' placeholder='" + type + "' /></div>");
            setTimeout(function () {
                cell.find("input").focus();
            }, 100);
        }

        function displayVals(p, i) {
            console.log("p: " + p);
            console.log("i: " + i);
            console.log("pind: " + $scope.pind);
            console.log("ind: " + $scope.ind);
        }

        function addOnfocus() {
            $(".edit > input").focusin(function () {
                $(this).parent().append("<div class='bubble'><div class='chng'><i class='fa fa-check'></i></div><div class='close'><i class='fa fa-times'></i></div></div>");
                addClickFunction();
            });
        }

        function addClickFunction() {
            $(".chng").on("click", function () {
                var t = $(this).parent().parent().find("input").val();
                if (t.length <= 0) {
                    var ph = $(this).parent().parent().find("input").attribute('placeholder');
                    $("tr").eq($scope.pind + 1).find("td").eq($scope.ind).text(ph);
                } else {
                    $("tr").eq($scope.pind + 1).find("td").eq($scope.ind).text(t);
                    console.log('new value: ' + t)
                }
            });

            $(".close").on("click", function () {
                $("tr").eq($scope.pind + 1).find("td").eq($scope.ind).find(".edit").remove();
            });
        }

    });
