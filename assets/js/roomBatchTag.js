import $ from "jquery";

function roomBatchTag(target, isTagged) {
    const $target = $(target);
    $target.prop("disabled", true);

    const roomId = $target.data("room-id");
    const tagId = $target.data("tag-id");

    const $label = $(`label[for=${$target.attr("id")}]`);
    $label.text(isTagged ? "Tagged" : "Untagged");

    const url = `/room/${roomId}/toggle_tag/${tagId}/`;
    const method = isTagged ? "POST" : "DELETE";

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
            $target.prop("checked", !isTagged);
            $label.text(isTagged ? "Untagged" : "Tagged");
            window.alert("An error occurred. Refresh and try again");
        }
    });
}

function roomBatchTagInit() {
    $(".tag-toggle").click(e => {
        roomBatchTag(e.target, $(e.target).prop("checked"));
    });
}

export default roomBatchTagInit;
