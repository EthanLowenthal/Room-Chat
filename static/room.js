
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
    window.removeEventListener("beforeunload", beforeunload);
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
    newMsg(`${data.name} created new problem: <a style="overflow: scroll;"  onclick="viewProblem(${data.id})" class="button button-medium">${data.title}</a>`);
    $("#problem-list").append(`<li data-id="${data.id}" class="problem-list-problem"><div onclick="viewProblem(${data.id})">${data.title}</div> <span class="problem-created-by">${data.name}</span></li>`)
    problems[data.id] = data
});
problemSolved = (problem_id) => {
    socket.emit('problem_solved', {id: problem_id, room:room});
    $('#problem-list-content').show();
    $('#view-problem-content').hide();
};
socket.on('new_problem_solved', function(data) {
      $(`[data-id='${data.id}']`).addClass('solved');
    problems[data.id]["solved"] = true;
    newMsg(`Problem was marked as solved: <a style="overflow: scroll;" onclick="viewProblem(${data.id})" class="button button-medium">${problems[data.id]['title']}</a>`);
});
problemDeleted = (problem_id) => {
    socket.emit('problem_deleted', {id: problem_id, room:room});
    $('#problem-list-content').show();
    $('#view-problem-content').hide();
};
socket.on('new_problem_deleted', function(data) {
    $(`[data-id='${data.id}']`).remove();
    delete problems[data.id];
    newMsg(`Problem was deleted: <a class="button button-medium button-disabled">${problems[data.id]['title']}</a>`);
});
viewProblem = (id) => {
    var problem = problems[id];
    if (problem == null) {
        $('#problem-list-content').show();
        $('#view-problem-content').hide();
        $("#view-problem-modal").show();
    } else {
        $('#view-problem-title').html(problem.title);
        $('#view-problem-message').html(problem.message);
        $('#problem-controls').attr('data-id', id);
        if (problem.sender_id == user_id) {
            $('#problem-controls').show();
        } else {
            $('#problem-controls').hide();
        }
        $('#problem-list-content').hide();
        $('#view-problem-content').show();
        $("#view-problem-modal").show();
    }

}
$("#problem-submit").on("click", () => {
    var message = $("#problem-message");
    var title = $("#problem-title");
    socket.emit('problem', {name: name, room: room, title:title.val(), message:message.val()});
    title.val("");
    message.val("");
    $("#new-problem-modal").hide();
});

beforeunload = (e) => {
  socket.emit('leave', {name: name, room: room});

  (e || window.event).returnValue = null;
  return null;
};
window.addEventListener("beforeunload", beforeunload);
