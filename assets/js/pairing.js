import quickSearchInit from "./quickSearch";

function populateTabCards() {
  const roundNumber = $("#round-number").data("round-number");
  if (roundNumber) {
    $.ajax({
      url: `/round/${roundNumber}/stats`,
      success(result) {
        Object.entries(result).forEach(([teamId, stats]) => {
          const tabCardElement = $(`.tabcard[team-id=${teamId}]`);
          const text = [
            stats.wins,
            stats.total_speaks.toFixed(2),
            stats.govs,
            stats.opps,
            stats.seed
          ].join(" / ");
          tabCardElement.attr("title", "Wins / Speaks / Govs / Opps / Seed");
          tabCardElement.attr("href", `/team/card/${teamId}`);
          tabCardElement.text(`${text}`);
        });
      }
    });
  }
}

function assignTeam(e) {
  e.preventDefault();
  const teamId = $(e.target).attr("team-id");
  const roundId = $(e.target).attr("round-id");
  const position = $(e.target).attr("position");
  const url = `/pairings/assign_team/${roundId}/${position}/${teamId}`;
  const alertMsg = `
    An error occured.
    Refresh the page and try to fix any inconsistencies you may notice.
  `;

  $.ajax({
    url,
    success(result) {
      if (result.success) {
        const $container = $(`.row[round-id=${roundId}] .${position}-team`);
        $container.find(".team-assign-button").attr("team-id", result.team.id);
        $container.find(".team-link").text(result.team.name);
        $container.find(".team-link").attr("href", `/team/${result.team.id}`);
        $container.find(".tabcard").attr("team-id", result.team.id);

        populateTabCards();
        refreshRoomWarning(roundId);
      } else {
        window.alert(alertMsg);
      }
    },
    failure() {
      window.alert(alertMsg);
    }
  });
}

function assignRoom(e) {
  e.preventDefault();
  const roundId = $(e.target).attr("round-id");
  const roomId = $(e.target).attr("room-id");
  const curRoomId = $(e.target).attr("current-room-id");
  const url = `/round/${roundId}/assign_room/${roomId}/${curRoomId || ""}`;

  let $buttonWrapper;
  if (curRoomId) {
    $buttonWrapper = $(`span[round-id=${roundId}][room-id=${curRoomId}]`);
  }
  const $button = $buttonWrapper.find(".btn-sm");
  $button.addClass("disabled");

  $.ajax({
    url,
    success(result) {
      $button.removeClass("disabled");
      $buttonWrapper.removeClass("unassigned");
      $buttonWrapper.attr("room-id", result.room_id);
      $button.html(`${result.room_name}`);
      $(`.room span[round-id=${roundId}] .room-toggle`).css(
        "background-color",
        result.room_color
      );
    }
  });
}

function populateAlternativeRooms() {
  const $parent = $(this).parent();
  const roomId = $parent.attr("room-id");
  const roundId = $parent.attr("round-id");
  const url = `/round/${roundId}/alternative_rooms/${roomId || ""}`;

  $.ajax({
    url,
    success(result) {
      $parent.find(".dropdown-menu").html(result);
      $parent
        .find(".dropdown-menu")
        .find(".room-assign")
        .click(assignRoom);
      quickSearchInit($parent.find("#quick-search"));
      $parent.find("#quick-search").focus();
    }
  });
}

function populateAlternativeTeams() {
  const $parent = $(this).parent();
  const teamId = $parent.attr("team-id");
  const roundId = $parent.attr("round-id");
  const position = $parent.attr("position");
  const url = `/round/${roundId}/${teamId}/alternative_teams/${position}`;

  $.ajax({
    url,
    success(result) {
      $parent.find(".dropdown-menu").html(result);
      $parent
        .find(".dropdown-menu")
        .find(".team-assign")
        .click(assignTeam);
      quickSearchInit($parent.find("#quick-search"));
      $parent.find("#quick-search").focus();
    }
  });
}

function refreshRoomWarning(roundId) {
  $.ajax({
    url: `/pairings/room_tag_warnings/${roundId}`,
    success(result) {
      const warningParent = $(`.warning-parent[round-id=${roundId}]`);
      const warningElement = $(`.room-warning[round-id=${roundId}]`);
      if (result.room_tag_warnings) {
        if (warningElement.length) {
          console.log("Updating warning");
          warningElement.text(result.room_tag_warnings);
        } else {
          console.log("Adding warning:" + result.room_tag_warnings);
          warningParent.append(
            `<div class="alert alert-danger text-center room-warning" round-id="${roundId}" role="alert" style="font-size: 1.5em;">
              ${result.room_tag_warnings}
            </div>`
          );
        }
      } else {
        console.log("Removing warning");
        warningElement.remove();
      }
    },
    failure() {
      console.error("Failed to refresh room warning");
    }
  });
}

function assignJudge(e) {
  e.preventDefault();
  const roundId = $(e.target).attr("round-id");
  const judgeId = $(e.target).attr("judge-id");
  const curJudgeId = $(e.target).attr("current-judge-id");
  const url = `/round/${roundId}/assign_judge/${judgeId}/${curJudgeId || ""}`;

  let $buttonWrapper;
  if (curJudgeId) {
    $buttonWrapper = $(`span[round-id=${roundId}][judge-id=${curJudgeId}]`);
  } else {
    $buttonWrapper = $(`span[round-id=${roundId}].unassigned`).first();
  }
  const $button = $buttonWrapper.find(".btn-sm");
  $button.addClass("disabled");

  $.ajax({
    url,
    success(result) {
      $button.removeClass("disabled");
      $buttonWrapper.removeClass("unassigned");
      $buttonWrapper.attr("judge-id", result.judge_id);

      const rank = result.judge_rank.toFixed(2);
      $button.html(`${result.judge_name} <small>(${rank})</small>`);
      $(`.judges span[round-id=${roundId}] .judge-toggle`).removeClass("chair");
      $(`.judges span[round-id=${roundId}][judge-id=${result.chair_id}]
        .judge-toggle`).addClass("chair");
        refreshRoomWarning(roundId);
    }
  });
}

function populateAlternativeJudges() {
  const $parent = $(this).parent();
  const judgeId = $parent.attr("judge-id");
  const roundId = $parent.attr("round-id");
  const url = `/round/${roundId}/alternative_judges/${judgeId || ""}`;

  $.ajax({
    url,
    success(result) {
      $parent.find(".dropdown-menu").html(result);
      $parent
        .find(".dropdown-menu")
        .find(".judge-assign")
        .click(assignJudge);
      quickSearchInit($parent.find("#quick-search"));
      $parent.find("#quick-search").focus();
    }
  });
}

function lazyLoad(element, url) {
  element.addClass("loading");
  $.ajax({
    url,
    success(result) {
      element.html(result);
      element.removeClass("loading");
    },
    failure() {
      element.html("Error received from server");
      element.removeClass("loading");
    }
  });
}

function alertLink() {
  window.alert(`Note that you have assigned a judge from within the pairing.
    You need to go and fix that round now.`);
}

function togglePairingRelease(event) {
  event.preventDefault();
  $.ajax({
    url: "/pairing/release",
    success(result) {
      if (result.pairing_released) {
        $("#close-pairings").removeClass("d-none");
        $("#release-pairings").addClass("d-none");
      } else {
        $("#close-pairings").addClass("d-none");
        $("#release-pairings").removeClass("d-none");
      }
    }
  });
}

$(document).ready(() => {
  populateTabCards();
  $("#team_ranking").each((_, element) => {
    lazyLoad($(element).parent(), "/team/rank/");
  });
  $("#debater_ranking").each((_, element) => {
    lazyLoad($(element).parent(), "/debater/rank/");
  });
  // Note: getting a warning that .click is deprecated.
  // Still working but should be migrated at some point.
  $(".judge-toggle").click(populateAlternativeJudges);
  $(".team-toggle").click(populateAlternativeTeams);
  $(".room-toggle").click(populateAlternativeRooms);
  $(".alert-link").click(alertLink);
  $(".btn.release").click(togglePairingRelease);
});
