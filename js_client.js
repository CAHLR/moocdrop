function get_interventions () {
var settings = {
  "async": true,
  "crossDomain": true,
  "url": "https://cahl.berkeley.edu:1336/api/interventions",
  "method": "GET",
  success: function(response) {
    for (var i=0; i < response.length, i++) {
      console.log(response[i].name);
      var policy = document.createElement("p");
      var text = document.createTextNode(response[i].name);
      policy.appendChild(text);
      policy.setAttribute("id", p.name);
      policy.onclick = (function (response, i) {
          return function () {
            filter([response[i].comp, response[i].attr, response[i].cert]);
            $('#email-subject').attr('value', response[i].subject);
            $('#email-body').attr('value', response[i].body);
            $('#reply-to').attr('value', response[i].reply);
            $('#policyName').text(response[i].name);
            $('#policyName').css('display', 'block');
            if (response[i].auto) {
              $('#automated').attr('checked', true);
              $('#automated').attr('disabled', "disabled");
            }
          };
      })(response, i);
      document.getElementById('myDropdown').appendChild(policy);
    }
  }
};
$.ajax(settings);
}
