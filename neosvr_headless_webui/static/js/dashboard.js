// dashboard.js

// Restart client modal

$("#restartClientModalForm").submit(function(event) {
  event.preventDefault();

  var $form = $(this),
    client_id = $form.find("input[name='client_id']").val()

  // I have no idea if this is an acceptable way of doing this. If you're
  // reading this, feel free to make my JavaScript code suck less.

  var action = event.originalEvent.submitter.value;

  if (action == "restart") {
    var posting = $.post("/api/v1/" + client_id + "/restart_client");
  } else if (action == "kill") {
    var posting = $.post("/api/v1/" + client_id + "/terminate");
  }

  $("#restartClientModal").modal("hide");

  posting.done(function(data) {
    window.location.reload(true);
  });
});

// Updates the restart modal when the restart link is clicked on a user

$('#restartClientModal').on('show.bs.modal', function (event) {
  var link = $(event.relatedTarget)
  var client_id = link.data('clientid')
  var modal = $(this)
  modal.find('.modal-body #restartClientModalClientID').val(client_id)
});
