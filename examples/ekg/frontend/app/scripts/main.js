/* jshint devel:true */

// Variables
App = {};
App.services = {};
App.chartOptions = {
  maxValue: 1, 
  minValue: 0, 
  millisPerPixel: 5,
  grid: {verticalSections: 20, millisPerLine: 50}
};
App.READ_FREQUENCY = 50;  // Frequency in Hz
App.RFQ            = 1/App.READ_FREQUENCY; // In seconds
App.time = 0;
App.canvas_element = document.getElementById("ekg");
App.current_position = 0;

// Functions
App.init = function() {
  App.chart  = new SmoothieChart(App.chartOptions);
  App.signal = new TimeSeries();
  App.chart.addTimeSeries(App.signal, {lineWidth:2, strokeStyle:'#00ff00'});
  App.start_monitor();
}

App.zoom_out = function() {
  App.chart.options.millisPerPixel++;
}

App.zoom_in = function() {
  App.chart.options.millisPerPixel--;
}

App.pause = function() {
  App.close_ws = true;
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

App.get_ws = function(hostname, onopen, onmessage, onclose){
    hostname = hostname || location.hostname;
    return App.services.WebSocketService.connect(
        'ws://' +  hostname,
        // onOpen
        function(socket){
          if(onopen) onopen(socket);
        },
        // onClose
        function(){
          if(onclose) onclose();
        },
        // onmessage
        function(e){
          if(onmessage) onmessage(e);
        }
    );
}

App.start_monitor = function(){
  var hostname = $('#hostname')[0].value;
  hostname = hostname || location.hostname;
  App.ws_signal = App.get_ws(hostname + ':7771/sephiroth', onsignal_open, onsignal_received, onsignalclose);
  App.ws_hr     = App.get_ws(hostname + ':7771/sephiroth_hr', onhr_open, onhr_received, onhr_close);
  App.ws_hist   = App.get_ws(hostname + ':7771/sephiroth_hist', onhist_open, onhist_received, onhist_close);
}

// ======================
// Signal processing
// ======================
function onsignal_open(ws){
  App.time = 0;
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
}

function onsignal_received(e){
  if(e.data === 'hangup' || App.close_ws){
    App.ws.close();
    console.log('Ws closed..');
    App.close_ws = false;
    return;
  }
  var time  = App.time * 1000;  
  var value = parseFloat(e.data);
  App.signal.append(time, value);
  App.chart.reference_time = time;
  App.time = App.time + App.RFQ;
}

function onsignal_close(){
}

// ======================
// Heartrate processing
// ======================
function onhr_open(ws){
  function hr_monitor() { 
    App.hr_timeout = setTimeout(
      function(){
        if(App.ws_hr.readyState === WebSocket.OPEN){
          App.ws_hr.send($('#client_id')[0].value);
        }
        hr_monitor();
      }, 3000);
  }
  if ( App.hr_timeout ){
    clearTimeout(App.hr_timeout);
    hr_monitor();
  } else {
    hr_monitor();
  }
}
function onhr_received(e){
  $('.heartrate').html(e.data);
}
function onhr_close(){
}

// ======================
// Signal history
// ======================
function onhist_open(ws){
}
function onhist_received(e){
  App.more_data = true;
  var data      = JSON.parse(e.data);
  
  if(data === '') {
    alert('No existen mas datos');
    return;
  }

  if(typeof(data) !== 'array') {
    alert('Datos incorrectos');
    return;
  }
  var size  = data.length;
  App.time  = App.current_position * App.RFQ;
  for(var i=0; i<data.length; i++) {
    var time  = App.time * 1000;  
    var value = parseFloat(data[i]);
    App.signal.append(time, value);
    App.chart.reference_time = time;
    App.time = App.time + App.RFQ;
  }
}

function onhist_close(){
}

// History
/**
 * requests_hist_data
 * Sends request for data n_records from server from point: from_point
 * The response is then processed by function onhist_received
 */
App.request_hist_data(from_point, n_records) {
  var client_id = $('#client_id')[0].value;
  var request   = client_id + ';' + from_point + ';' + n_records;
  App.ws_hist.send(request);
}

App.more_data = true;
App.move_forward = function() {
  App.close_ws = true;
  if(!App.more_data) return;
  App.more_data = false;
  App.current_position = App.current_position + App.page_size;
  App.request_hist_data(App.current_position, 500);
}

App.move_back = function() {
  App.close_ws = true;
  App.current_position = App.current_position - App.page_size;
  if(App.current_position < 0) {
    App.current_position = App.current_position - App.page_size;
  } else {
    App.request_hist_data(App.current_position, 500);
  }

}
