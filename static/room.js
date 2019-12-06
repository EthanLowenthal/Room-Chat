
newMsg = (msg) => {
          // Insert text
    var para = document.createElement("P");                 // Create a <p> element
    para.innerHTML = msg;
    chat = document.getElementById("chat-box");
    chat.appendChild(para);
    chat.scrollTop = chat.scrollHeight;

};

var socket = io();
socket.on('connect', function() {
    socket.emit('join', {name: name, room: room});
});
socket.on('room_deleted', function() {
    alert("room deleted: redirecting to home page");
    window.location.href = "/";
});

socket.on('disconnection', function(data) {
    newMsg(`[server]: ${data.name} has left the room`);
    document.querySelector("#user-count").innerHTML = parseInt(document.querySelector("#user-count").innerHTML) - 1;
    document.querySelector("#users").innerHTML = document.querySelector("#users").innerHTML.replace(`${data.name}<br>`, "");
});

socket.on('connection', function(data) {
    newMsg(`[server]: ${data.name} has entered the room`);
    document.querySelector("#user-count").innerHTML = parseInt(document.querySelector("#user-count").innerHTML) + 1;
    document.querySelector("#users").innerHTML += `${data.name}<br>`
});

socket.on('new_message', function(data) {
    newMsg(`${data.name}: ${data.message}`);
});

sendMessage = () => {
    if (document.getElementById("message").value != "") {
        console.log(document.getElementById("message").value);
        socket.emit('message', {name: name, room: room, message: document.getElementById("message").value});
        document.getElementById("message").value = "";
    }
};

window.addEventListener("beforeunload", function (e) {
  socket.emit('leave', {name: name, room: room});

  (e || window.event).returnValue = null;
  return null;
});