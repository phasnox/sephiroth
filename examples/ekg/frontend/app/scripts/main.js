/* jshint devel:true */
console.log('\'Allo \'Allo!');

App = {};
App.services = {};
App.chartOptions = {
  maxValue: 1, 
  minValue: 0, 
  millisPerPixel: 5,
  grid: {verticalSections: 20, millisPerLine: 50}
};

App.zoom_out = function() {
  App.chart.options.millisPerPixel++;
}

App.zoom_in = function() {
  App.chart.options.millisPerPixel--;
}

App.pause = function() {
  App.close_ws = true;
}

App.init = function() {
  App.chart  = new SmoothieChart(App.chartOptions);
  App.signal = new TimeSeries();
  App.chart.addTimeSeries(App.signal, {lineWidth:2, strokeStyle:'#00ff00'});
  App.restart_monitor();
}

App.services.WebSocketService = {
  connect: function(path, on_open, on_close, on_message, on_error){
      var socket = new WebSocket(path);

      socket.onopen = function (){
          console.log("WS conexion abierta");
          if(on_open) on_open(socket);
      };

      socket.onmessage = function (e){
          if(on_message) on_message(e);
      };

      socket.onerror = function(error){
          console.log("WS error: " + error);
          if(on_error) on_error(error);
      };

      socket.onclose = function (){
          console.log("WS conexion cerrada");
          if(on_close) on_close();
      };

      return socket;
  }
  };

App.canvas_element = document.getElementById("ekg")
App.get_ws = function(onopen, hostname){
    hostname = hostname || location.hostname;
    return App.services.WebSocketService.connect(
        'ws://' +  hostname + ':7771/sephiroth',
        // onOpen
        function(socket){
            if(onopen) onopen(socket);
        },
        // onClose
        function(){
        },
        // onmessage
        function(e){
          if(e.data === 'hangup' || App.close_ws){
            App.ws.close();
            console.log('Ws closed..');
            App.close_ws = false;
            return;
          }
          var data = e.data.split(';');
          var time  = parseFloat(data[0]) * 1000;  
          var value = parseFloat(data[1]);
          App.signal.append(time, value);
          App.chart.reference_time = time;
        }
    );
}

App.start_monitor = function(ws) {
  App.chart.streamTo(App.canvas_element);
  if(ws.readyState === WebSocket.CONNECTING) {
        console.log('Websocket: conectando..');
        alert('Ha ocurrido un error.. intente mas tarde');
        return;
    }
    if(ws.readyState !== WebSocket.OPEN){
        alert('Ws not open.. :(');
    } else{
        ws.send($('#client_id')[0].value);
    }
};


function hr_monitor() { 
  App.hr_timeout = setTimeout(
    function(){
      if(App.ws_hr.readyState === WebSocket.OPEN){
        App.ws_hr.send($('#client_id')[0].value);
      }
      hr_monitor();
    }, 2000);
}

App.restart_monitor = function(){
  var hostname = $('#hostname')[0].value;
  App.ws       = App.get_ws(App.start_monitor, hostname);
  App.ws_hr    = App.get_hr_ws(App.start_monitor, hostname);
  if ( App.hr_timeout ){
    clearTimeout(App.hr_timeout);
    hr_monitor();
  } else {
    hr_monitor();
  }
}

// Heart Rate
App.get_hr_ws = function(onopen, hostname){
    hostname = hostname || location.hostname;
    return App.services.WebSocketService.connect(
        'ws://' +  hostname + ':7771/sephiroth_hr',
        // onOpen
        function(socket){
            if(onopen) onopen(socket);
        },
        // onClose
        function(){
        },
        // onmessage
        function(e){
          $('.heartrate').html(e.data);
        }
    );
}
