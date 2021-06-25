// session.js

// TODO: Remove all this boilerplate code. I'm not a JavaScript expert.
// Tried a for loop already but there must be some scope issue I'm not understanding.

// Name modal

$("#nameModalForm").submit(function(event) {
  event.preventDefault();

  var $form = $(this),
    name = $form.find("input[name='name']").val(),
    url = $form.attr("action");

  var posting = $.post(url, {name: name});

  $("#nameModal").modal("hide");

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

// Description modal

$("#descriptionModalForm").submit(function(event) {
  event.preventDefault();

  var $form = $(this),
    description = $form.find("textarea[name='description']").val(),
    url = $form.attr("action");

  var posting = $.post(url, {description: description});

  $("#descriptionModal").modal("hide");

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

// Access level modal

$("#accessLevelModalForm").submit(function(event) {
  event.preventDefault();

  var $form = $(this),
    access_level = $form.find("select[name='access_level']").val(),
    url = $form.attr("action");

  var posting = $.post(url, {access_level: access_level});

  $("#accessLevelModal").modal("hide");

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

// Hide from listing modal

$("#hideFromListingModalForm").submit(function(event) {
  event.preventDefault();

  var $form = $(this),
    hide = $form.find("input[name='hide']")[0].checked,
    url = $form.attr("action");

  var posting = $.post(url, {hide: hide});

  $("#hideFromListingModal").modal("hide");

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

// Max users modal

$("#maxUsersModalForm").submit(function(event) {
  event.preventDefault();

  var $form = $(this),
    max_users = $form.find("input[name='max_users']").val(),
    url = $form.attr("action");

  var posting = $.post(url, {max_users: max_users});

  $("#maxUsersModal").modal("hide");

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

// Away kick interval modal

$("#awayKickIntervalModalForm").submit(function(event) {
  event.preventDefault();

  var $form = $(this),
    interval = $form.find("input[name='interval']").val(),
    url = $form.attr("action");

  var posting = $.post(url, {interval: interval});

  $("#awayKickIntervalModal").modal("hide");

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

// Invite modal

$("#inviteModalForm").submit(function(event) {
  event.preventDefault();

  var $form = $(this),
    username = $form.find("input[name='username']").val(),
    url = $form.attr("action");

  var posting = $.post(url, {username: username});

  $("#inviteModal").modal("hide");

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

// Kick by name modal

$("#kickByNameModalForm").submit(function(event) {
  event.preventDefault();

  var $form = $(this),
    username = $form.find("input[name='username']").val(),
    url = $form.attr("action");

  var posting = $.post(url, {username: username});

  $("#kickByNameModal").modal("hide");

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

// Ban by name modal

$("#banByNameModalForm").submit(function(event) {
  event.preventDefault();

  var $form = $(this),
    username = $form.find("input[name='username']").val(),
    url = $form.attr("action");

  var posting = $.post(url, {username: username});

  $("#banByNameModal").modal("hide");

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

// Role modal (when a user's role is clicked)

$("#roleModalForm").submit(function(event) {
  event.preventDefault();

  var $form = $(this),
    username = $form.find("input[name='username']").val(),
    role = $form.find("select[name='role']").val(),
    url = $form.attr("action");

  var posting = $.post(url, {username: username, role: role});

  $("#roleModal").modal("hide");

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

// Message modal (when Message button is clicked on a user)
// This modal is slightly different from the others.

$("#messageModalForm").submit(function(event) {
  event.preventDefault();

  var $form = $(this),
    username = $form.find("input[name='username']").val(),
    message = $form.find("textarea[name='message']").val(),
    url = $form.attr("action");

  var posting = $.post(url, {username: username, message: message});

  $("#messageModal").modal("hide");

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

// Kick modal (when Kick button is clicked on a user)

$("#kickModalForm").submit(function(event) {
  event.preventDefault();

  var $form = $(this),
    username = $form.find("input[name='username']").val(),
    url = $form.attr("action");

  var posting = $.post(url, {username: username});

  $("#kickModal").modal("hide");

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

// Ban modal (when Ban button is clicked on a user)

$("#banModalForm").submit(function(event) {
  event.preventDefault();

  var $form = $(this),
    username = $form.find("input[name='username']").val(),
    url = $form.attr("action");

  var posting = $.post(url, {username: username});

  $("#banModal").modal("hide");

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

// Updates the role modal when a user's role is clicked

$('#roleModal').on('show.bs.modal', function (event) {
  var button = $(event.relatedTarget)
  var username = button.data('username')
  var modal = $(this)
  modal.find('.modal-body #roleModalUsernameDisplay').text(username)
  modal.find('.modal-body #roleModalUsername').val(username)
});

// Updates the message modal when the Message button is clicked on a user
// This modal is slightly different from the others.

$('#messageModal').on('show.bs.modal', function (event) {
  var button = $(event.relatedTarget)
  var username = button.data('username')
  var modal = $(this)
  modal.find('.modal-body #messageModalUsername').val(username)
});

// Updates the kick modal when the Kick button is clicked on a user

$('#kickModal').on('show.bs.modal', function (event) {
  var button = $(event.relatedTarget)
  var username = button.data('username')
  var modal = $(this)
  modal.find('.modal-body #kickModalUsernameDisplay').text(username)
  modal.find('.modal-body #kickModalUsername').val(username)
});

// Updates the ban modal when the Ban button is clicked on a user

$('#banModal').on('show.bs.modal', function (event) {
  var button = $(event.relatedTarget)
  var username = button.data('username')
  var modal = $(this)
  modal.find('.modal-body #banModalUsernameDisplay').text(username)
  modal.find('.modal-body #banModalUsername').val(username)
});
