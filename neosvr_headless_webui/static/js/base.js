// base.js

// TODO: Remove all this boilerplate code. I'm not a JavaScript expert.
// Tried a for loop already but there must be some scope issue I'm not understanding.

// Find user form

$("#findUserForm").submit(function(event) {
  event.preventDefault();

  var $form = $(this),
    username = $form.find("input[name='username']").val(),
    url = $form.attr("action");

  var posting = $.post(url, {username: username});

  posting.done(function(data) {
    // Try to redirect to the session they're present in first, if any.
    if (data["sessions"]["present"].length > 0) {
      var session = data["sessions"]["present"][0];
      window.location.href = "/client/" + session[0] + "/session/" + session[1];
    } else if (data["sessions"]["current"].length > 0) {
      var session = data["sessions"]["current"][0];
      window.location.href = "/client/" + session[0] + "/session/" + session[1];
    } else {
      $(document).Toasts('create', {
        autohide: true,
        delay: 10000,
        class: "bg-danger",
        title: "Error!",
        body: "User not found"
      });
    }
  });
});

// Kick everywhere form

$("#kickEverywhereForm").submit(function(event) {
  event.preventDefault();

  var $form = $(this),
    username = $form.find("input[name='username']").val(),
    url = $form.attr("action");

  var posting = $.post(url, {username: username});

  $("#kickEverywhereModal").modal("hide");

  posting.done(function(data) {
    var numSessions = data["kicks"].length
    if (numSessions > 0) {
      $(document).Toasts('create', {
        autohide: true,
        delay: 10000,
        class: "bg-success",
        title: "Success!",
        body: "User was kicked from " + numSessions + " session(s)"
      });
    } else {
      $(document).Toasts('create', {
        autohide: true,
        delay: 10000,
        class: "bg-danger",
        title: "Error!",
        body: "User not found"
      });
    }
  });
});

// Ban everywhere form

$("#banEverywhereForm").submit(function(event) {
  event.preventDefault();

  var $form = $(this),
    username = $form.find("input[name='username']").val(),
    kick = $form.find("input[name='kick']")[0].checked,
    url = $form.attr("action");

  var posting = $.post(url, {username: username, kick: kick});

  $("#banEverywhereModal").modal("hide");

  posting.done(function(data) {
    var numBanSessions = data["bans"].length,
      numKickSessions = data["kicks"].length
    if (numBanSessions > 0) {
      var message = "User banned from " + numBanSessions + " client(s)"
      if (numKickSessions > 0) {
        var message = message + ", and kicked from " + numKickSessions + " session(s)."
      }
      $(document).Toasts('create', {
        autohide: true,
        delay: 10000,
        class: "bg-success",
        title: "Success!",
        body: message
      });
    } else {
      $(document).Toasts('create', {
        autohide: true,
        delay: 10000,
        class: "bg-danger",
        title: "Error!",
        body: "User not found"
      });
    }
  });
});

$('#dark-toggle').click(function() {
  let darkMode = localStorage.getItem('dark-mode');
  if (darkMode !== null) {
    darkMode = !(darkMode === 'true');
  } else {
    darkMode = !(window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);
  }

  localStorage.setItem('dark-mode', darkMode);

  if (darkMode) {
    $('body').addClass('dark-mode');
    $('nav.main-header').removeClass('navbar-light navbar-white').addClass('navbar-dark');
    $('#dark-toggle i').removeClass('fa-sun').addClass('fa-moon');
  } else {
    $('body').removeClass('dark-mode');
    $('nav.main-header').removeClass('navbar-dark').addClass('navbar-light navbar-white');
    $('#dark-toggle i').removeClass('fa-moon').addClass('fa-sun');
  }
});

$(function() {
  const systemDarkMode = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  const darkMode = localStorage.getItem('dark-mode');
  if (darkMode === 'true' || (darkMode === null && systemDarkMode)) {
    $('body').addClass('dark-mode');
    $('nav.main-header').removeClass('navbar-light navbar-white').addClass('navbar-dark');
    $('#dark-toggle i').removeClass('fa-sun').addClass('fa-moon');
  }
});
