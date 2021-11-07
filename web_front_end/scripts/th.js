let mqtt;
const reconnectTimeout = 2000;
const port = 9004;
const host = "192.168.1.10";
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

        // power on/off toggle flag
        let toggle = false;

        // thermostat control button reference
        let day = document.getElementById("dayToggle");
        let night = document.getElementById("nightToggle");
        let auto = document.getElementById("autoToggle");
        let power = document.getElementById("onToggle");

        $scope.topic = topic;
        $scope.week = week;
        $scope.temp = temp;
        $scope.schedule = schedule;
        $scope.mode = 'OFF';
        $scope.day_temp = 0;
        $scope.night_temp = 0;


        // action when a thermostat control button is clicked
        $scope.action = function (value) {
            console.log('action: ' + value);
            // thermostat control button act as
            // mutually exclusive radio button
            // on click, set the color to green, and the others to grey
	
            if (value === 'DAY') {
                day.style = "color:blue; position:relative; top:5px";
                night.style = "color:grey; position:relative; top:5px";
                auto.style = "color:grey; position:relative; top:5px";
            }
            if (value === 'NIGHT') {
                day.style = "color:grey; position:relative; top:5px";
                night.style = "color:blue; position:relative; top:5px";
                auto.style = "color:grey; position:relative; top:5px";
            }
            if (value === 'AUTO') {
                day.style = "color:grey; position:relative; top:5px";
                night.style = "color:grey; position:relative; top:5px";
                auto.style = "color:blue; position:relative; top:5px";
            }
	
            // if power button is clicked, toggle state
            if (value === 'OFF') {
                value = toggle ? 'ON' : 'OFF';
                toggle = !toggle;
            }

            // send a message to the thermostat with the selected control
            send('thermostat/mode',value);
        };

        // function to increment the day or night temperature values
        $scope.incr = function (key, val) {
            val = parseInt(val);
            val += 1;
            send('thermostat/' + key, String(val));
        };

        // function to decrement the day or night temperature values
        $scope.decr = function (key, val) {
            val = parseInt(val);
            val -= 1;
            send('thermostat/' + key, String(val));
        };


        $scope.isOpen = false;
        $scope.pind = -1;
        $scope.ind = -1;


        $scope.$watch('temp', function (newValue, oldValue) {
            $scope.temp = newValue;
            console.log('temp:' + newValue, ' <- ', oldValue);
        });
        $scope.$watch('schedule', function (newValue, oldValue) {
            $scope.schedule = newValue;
            console.log('schedule:' + newValue, ' <- ', oldValue);
        });


        MQTTconnect();
        mqtt.onMessageArrived = onMessageArrived;


        // FUNCTIONS -----------------------------------------

        function onConnect() {
            console.log('connected!');
            mqtt.subscribe(topic);
            m = new Paho.MQTT.Message("");
            m.destinationName = 'thermostat/getState';
            mqtt.send(m);
        }

        function MQTTconnect() {
            console.log('connecting to mqtt server');
            mqtt = new Paho.MQTT.Client(host, port, 'clientJS');
            $.get("http://"+host+":1880/redis?id=iot", function (o) {
                // o = JSON.parse(o);
                // console.log('user is: '+o.username);
                mqtt.connect({
                    onSuccess: onConnect,
                    userName: o.username,
                    password: o.password
                });
            });


        }

        function onMessageArrived(message) {
            console.log('message arrived: ' + message.payloadString);
            data = JSON.parse(message.payloadString);
            console.log('temp: ' + String(data.curr_temp));
            $scope.mode = data.mode;
            $scope.day_temp = data.day_temp;
            $scope.night_temp = data.night_temp;
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

        function send(topic, msg){
            console.log(topic +': '+ msg);
            m = new Paho.MQTT.Message(msg);
            m.destinationName = topic;
            mqtt.send(m);
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
