/* jshint devel:true */
console.log('\'Allo \'Allo!');

App = {};
App.services = {};

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
App.get_ws = function(onopen){
    return App.services.WebSocketService.connect(
        'ws://' +  location.hostname + ':7771/sephiroth',
        // onOpen
        function(socket){
            if(onopen) onopen(socket);
        },
        // onClose
        function(){
        },
        // onmessage
        function(e){
            if(e.data === 'hangup'){
                console.log('Ws closed..');
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

App.restart_monitor = function(){
  App.ws = App.get_ws(App.start_monitor);
}

