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
