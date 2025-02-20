

function teamCheckInOrOut(target, isCheckIn) {
  const $target = $(target);
  $target.prop("disabled", true);

  const teamId = $target.data("team-id");

  const $label = $(`label[for=${$target.attr("id")}]`);
  $label.text(isCheckIn ? "Checked In" : "Checked Out");

  const url = `/team/${teamId}/check_ins/`;
  const method = isCheckIn ? "POST" : "DELETE";

  $.ajax({
    url,
    beforeSend(xhr) {
      xhr.setRequestHeader(
        "X-CSRFToken",
        $("[name=csrfmiddlewaretoken]").val()
      );
    },
    method,
    success() {
      $target.prop("disabled", false);
    },
    error() {
      $target.prop("disabled", false);
      $target.prop("checked", !isCheckIn);
      $label.text(isCheckIn ? "Checked Out" : "Checked In");
      window.alert("An error occured. Refresh and try again");
    }
  });
}

function teamCheckinInit() {
  $(".team-checkin-toggle").click(e => {
    teamCheckInOrOut(e.target, $(e.target).prop("checked"));
  });
}

export default teamCheckinInit;
