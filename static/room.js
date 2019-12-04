
newMsg = (msg) => {
          // Insert text
    var para = document.createElement("P");                 // Create a <p> element
    para.innerHTML = msg;
    chat = document.getElementById("chat-box");
    chat.appendChild(para);
    chat.scrollTop = chat.scrollHeight;

}

var socket = io();
socket.on('connect', function() {
    socket.emit('connection', {name: name, room: room});
});
socket.on('room_deleted', function() {
    alert("room deleted: redirecting to home page");
    window.location.href = "/";
});
// window.onunload = function() {
//     socket.emit('disconnect', {name: name, room: room});
// }

// socket.on('disconnect', (reason) => {
//   if (reason === 'io server disconnect') {
//     // the disconnection was initiated by the server, you need to reconnect manually
//     socket.connect();
//   }
//     socket.emit('disconnect', {name: name, room: room});
// });
// socket.on('disconnection', function(data) {
//     newMsg(`${data.name} has left the room`);
// });
socket.on('new_connection', function(data) {
    newMsg(`${data.name} has entered the room`);
    document.querySelector("#user-count").innerHTML = parseInt(document.querySelector("#user-count").innerHTML) + 1;
    document.querySelector("#users").innerHTML += `${data.name}<br>`
});
socket.on('new_message', function(data) {
    newMsg(`${data.name}: ${data.message}`);
});
sendMessage = () => {
    if (document.getElementById("message").value != "") {
        socket.emit('message', {name: name, room: room, message: document.getElementById("message").value});
        document.getElementById("message").value = "";
    }
}