// client.js

// Restart client modal

$("#restartClientModalForm").submit(function(event) {
  event.preventDefault();

  var $form = $(this),
    url = $form.attr("action");

  var posting = $.post(url);

  $("#restartClientModal").modal("hide");

  posting.done(function(data) {
    window.location.href = "/dashboard";
  });
});

// Kill client modal

$("#killClientModalForm").submit(function(event) {
  event.preventDefault();

  var $form = $(this),
    url = $form.attr("action");

  var posting = $.post(url);

  $("#killClientModal").modal("hide");

  posting.done(function(data) {
    window.location.href = "/dashboard";
  });
});

// Accept friend request modal (when Accept button is clicked on a user)

$("#acceptFriendRequestModalForm").submit(function(event) {
  event.preventDefault();

  var $form = $(this),
    username = $form.find("input[name='username']").val(),
    url = $form.attr("action");

  var posting = $.post(url, {username: username});

  $("#acceptFriendRequestModal").modal("hide");

  posting.done(function(data) {
    if (data["success"]) {
      var toast_title = "Success!"
      var toast_class = "bg-success";
    } else {
      var toast_title = "Error!"
      var toast_class = "bg-danger";
    }
    $(document).Toasts('create', {
      autohide: true,
      delay: 10000,
      class: toast_class,
      title: toast_title,
      body: data["message"],
    });
  });
});

// Updates the accept friend request modal when the Accept button is clicked on a user

$('#acceptFriendRequestModal').on('show.bs.modal', function (event) {
  var button = $(event.relatedTarget)
  var username = button.data('username')
  var modal = $(this)
  modal.find('.modal-body #acceptFriendRequestModalUsernameDisplay').text(username)
  modal.find('.modal-body #acceptFriendRequestModalUsername').val(username)
});
