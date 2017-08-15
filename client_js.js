var ids;

function getIDs(callback) {
  ids = [];
  // ids = '';
  for (i = 0; i < $('.anon-student').length; i++) {
      ids.push($('.anon-student')[i].innerHTML);
      // ids += ($('.anon-student')[i].innerHTML) + ' ';
  }
  console.log(ids);
  callback();
}

function send_emails () {
  var ann = ($('#annRadio').attr("checked") === "checked");
  var settings = {
    "async": true,
    "crossDomain": true,
    "url": "https://cahl.berkeley.edu:1337/api/email",
    "method": "POST",
    "data":
    {
      "ids": ids,
      "subject": $('#email-subject').attr('value'),
      "body": $('#email-body').attr('value'),
      "reply": $('#reply-to').attr('value'),
      "pass": "sadfvkn88asVLS891",
      "ann": ann
    },
    success: function(response) {
      console.log("Successfully sent!");
      alert("Successfully sent!");
    }
  };
  $.ajax(settings);
}

function toggleDropdown() {
    document.getElementById("myDropdown").classList.toggle("show");
}

// Close the dropdown menu if the user clicks outside of it
window.onclick = function(event) {
  if (!event.target.matches('.dropbtn')) {

    var dropdowns = document.getElementsByClassName("dropdown-content");
    var i;
    for (i = 0; i < dropdowns.length; i++) {
      var openDropdown = dropdowns[i];
      if (openDropdown.classList.contains('show')) {
        openDropdown.classList.remove('show');
      }
    }
  }
}



function get_interventions () {
var settings = {
  "async": true,
  "crossDomain": true,
  "url": "https://cahl.berkeley.edu:1337/api/interventions",
  "method": "GET",
  success: function(response) {
    var myDropdown = document.getElementById('myDropdown');
    myDropdown.innerHTML = '';

    var load = document.createElement("option");
    load.selected = true;
    load.disabled = true;
    load.text = "Load Past Communications";
    myDropdown.appendChild(load);

    for (var p in response) {
      var policy = document.createElement("option");
      var formatted_date = new Date(response[p].timestamp).toDateString().split(" ")
      var final_display = formatted_date[1] + " " + formatted_date[2] + " " + formatted_date[3] + " - " + response[p].name;
      if (response[p].auto === "true") {
        final_display = "(Active) " + final_display;
      }
      policy.innerHTML = final_display;
      policy.setAttribute("id", response[p].name);
      policy.setAttribute("value", JSON.stringify(response[p]));
      myDropdown.appendChild(policy);
    }
  }
};
$.ajax(settings);
}

function optSelected (response) {
  var response = JSON.parse(response);
  filter([response.comp, response.attr, response.cert]);
  $('#email-subject').attr('value', response.subject);
  $('#email-body').attr('value', response.body);
  $('#reply-to').attr('value', response.reply);
  $('#policyName').text(response.name);
  if (response.auto === "true") {
    $('#automated').attr('checked', true);
  }
  $('#saveChanges').css('display', 'inline-block');
}

function get_announcements () {
var settings = {
  "async": true,
  "crossDomain": true,
  "url": "https://cahl.berkeley.edu:1337/api/announcements",
  "method": "GET",
  success: function(response) {
    var myDropdown = document.getElementById('myDropdown');
    myDropdown.innerHTML = '';

    var load = document.createElement("option");
    load.selected = true;
    load.disabled = true;
    load.text = "Load Past Communications";
    myDropdown.appendChild(load);

    for (var p in response) {
      var policy = document.createElement("option");
      var formatted_date = new Date(response[p].timestamp).toDateString().split(" ")
      var final_display = formatted_date[1] + " " + formatted_date[2] + " " + formatted_date[3] + " - " + response[p].name;
      policy.innerHTML = final_display;
      policy.setAttribute("id", response[p].name);
      policy.setAttribute("value", JSON.stringify(response[p]));
      myDropdown.appendChild(policy);
    }
  }
};
$.ajax(settings);
}


function send_policy () {
  var comp = window.filterLimits["completion-chart"];
  var attr = window.filterLimits["attrition-chart"];
  var cert = window.filterLimits["certification-chart"];

  var automated = ($('#automated').attr("checked") === "checked");
  console.log("automated: " + automated);
  var intervention = ($('#intRadio').attr("checked") === "checked");

  var settings = {
    "async": true,
    "crossDomain": true,
    "url": "https://cahl.berkeley.edu:1337/api/save",
    "method": "POST",
    "data":
    {
      "ids": ids,
      "subject": $('#email-subject').attr('value'),
      "body": $('#email-body').attr('value'),
      "reply": $('#reply-to').attr('value'),
      "name": $('#email-subject').attr('value'),
      "comp": comp,
      "attr": attr,
      "cert": cert,
      "auto": automated,
      "timestamp": new Date(),
      "intervention": intervention
    },
    success: function(response) {
      console.log("Policy Successfully sent!");
      alert("Policy Saved!");
    }
  };
  $.ajax(settings);
}


function save_changes () {
  var settings = {
    "async": true,
    "crossDomain": true,
    "url": "https://cahl.berkeley.edu:1337/api/changes",
    "method": "POST",
    "data":
    {
      "name": $('#policyName')[0].innerHTML,
      "ids": ids,
      "subject": $('#email-subject').attr('value'),
      "body": $('#email-body').attr('value'),
      "reply": $('#reply-to').attr('value'),
      "comp": comp,
      "attr": attr,
      "cert": cert,
      "auto": automated,
    },
    success: function(response) {
      console.log("Policy Successfully Stopped!");
    }
  };
  $.ajax(settings);
}

window.onload = function() {
  drawGraphs("https://cahl.berkeley.edu:1337/api/predictions");
  get_interventions();
  $('#emailButton').on('click', function() {
    if ($('#intRadio').attr("checked") === "checked") {
      if (confirm("Are you sure you want to send this email to " + window.selectedStudents.length + " students?")) {
        getIDs(send_emails);
        getIDs(send_policy);
        get_interventions();
      }
    }
    else {
      if (confirm("Are you sure you want to send this email to " + $('#total')[0].innerHTML + " students?")) {
        getIDs(send_emails);
        getIDs(send_policy);
        get_announcements();
      }
    }
  });
  $('#comp-no-cert').on('click', function() {
    filter([[80, 100], null, [0, 20]]);
  });
  $('#attr-no-comp-cert').on('click', function() {
    filter([[0,70], [80, 100], [0, 70]]);
  });
  $('#annRadio').on('click', function() {
    get_announcements();
    $('#intervention').css('display', 'none');
    $('#automated').css('display', 'none');
    $('#automated2').css('display', 'none');
    $('#all-recipients').css('display', 'block');
    $('#recipients').css('display', 'none');
  });
  $('#intRadio').on('click', function() {
    get_interventions();
    $('#intervention').css('display', 'block');
    // $('#modalBtn').css('display', 'block');
    $('#automated').css('display', 'inline');
    $('#automated2').css('display', 'inline');
    $('#automated').attr('checked', false);
    $('#all-recipients').css('display', 'none');
    $('#recipients').css('display', 'block');
  });
  $('#test').on('click', function() {
    getIDs(send_policy);
    get_announcements();
  });
  $('#test2').on('click', function() {
    getIDs(send_policy);
    get_interventions();
  });
  $('#saveChanges').on('click', function() {
    save_changes();
    var toDelete = $('#policyName').text();
    $('#' + toDelete).remove();
    $('#policyName').text('');
  });
  $("#automated").hover(
    function() {
        $("#tip").show();
    },
    function() {
        $("#tip").hide();
    }
  );
};
