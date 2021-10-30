var img = document.getElementById("currentImage");
url = document.URL.replace('http','ws')
var ws = new WebSocket(url + "stream");

cam_com = {};

cam_com.input_handler = function (e){
	var message = {
		type: e.type || "",
		x: e.pageX - img.offsetLeft || 0,
		y: e.pageY - img.offsetTop || 0,
		button: e.button || 0,
		alt_key: e.altKey || false,
		ctrl_key: e.ctrlKey || false,
		meta_key: e.metaKey || false,
		shift_key: e.shiftKey || false,
		key_code: e.keyCode || 0
	}
	ws.send(JSON.stringify(message));
}

cam_com.input_handler_absolute = function (e){
    
	var message = {
		type: e.type || "",
		x: e.offsetX || 0,
		y: e.offsetY || 0,
		button: e.button || 0,
		alt_key: e.altKey || false,
		ctrl_key: e.ctrlKey || false,
		meta_key: e.metaKey || false,
		shift_key: e.shiftKey || false,
		key_code: e.keyCode || 0
	}
	ws.send(JSON.stringify(message));
}

ws.onopen = function() {
    console.log("connection was established");
    img.onmousedown = cam_com.input_handler;
    img.onmouseup = cam_com.input_handler;
    img.onmousemove = cam_com.input_handler;
    img.onclick = cam_com.input_handler;
    img.ondblclick = cam_com.input_handler;
    ws.send("next");
};

ws.onmessage = function(msg) {
    img.src = 'data:image/png;base64, ' + msg.data;
};

img.onload = function() {
  ws.send("next");
}

