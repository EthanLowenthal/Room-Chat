
newMsg = (msg) => {
    chat = $("#chat-box");
    chat.append(`<p>${msg}</p>`);
    chat.scrollTop(chat.prop('scrollHeight'));
};
sendMessage = () => {
    message = $("#message");
    if (message.val() != "") {
        console.log(message.val());
        socket.emit('message', {name: name, room: room, message: message.val()});
        message.val("");
    }
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
    user_cout = $("#user-count");
    users = $("#users");
    user_cout.html(parseInt(user_cout.html()) - 1);
    users.html(users.html().replace(`${data.name}<br>`, ""));
});

socket.on('connection', function(data) {
    newMsg(`[server]: ${data.name} has entered the room`);
    user_cout = $("#user-count");
    users = $("#users");
    user_cout.html(parseInt(user_cout.html()) + 1);
    users.append(`${data.name}<br>`);
});
socket.on('new_message', function(data) {
    newMsg(`${data.name}: ${data.message}`);
});
socket.on('new_problem', function(data) {
    newMsg(`${data.name} created new problem: <a onclick="veiwProblem(${data.id})" class="button button-medium">${data.title}</a>`);
    $("#problem-list").append(`<li class="problem-list-problem"><div onclick="veiwProblem(${data.id})">${data.title}</div> <span class="problem-created-by">${data.name}</span></li>`)
    problems[data.id] = data
});
veiwProblem = (id) => {
    var problem = problems[id];
    $('#veiw-problem-title').html(problem.title);
    $('#veiw-problem-message').html(problem.message);
    $('#problem-list-content').hide();
    $('#veiw-problem-content').show();
    $("#view-problem-modal").show();
}
$("#problem-submit").on("click", () => {
    var message = $("#problem-message");
    var title = $("#problem-title");
    socket.emit('problem', {name: name, room: room, title:title.val(), message:message.val()});
    title.val("");
    message.val("");
    $("#new-problem-modal").hide();
});

window.addEventListener("beforeunload", function (e) {
  socket.emit('leave', {name: name, room: room});

  (e || window.event).returnValue = null;
  return null;
});
