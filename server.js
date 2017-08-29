var express = require('express');
var app = express();
var bodyParser = require('body-parser');
var https = require('https');
var http = require('http');
var fs = require('fs');
var auth = require('basic-auth');
var nodemailer = require('nodemailer');
var $ = jQuery = require('jquery');
require(process.cwd() + '/jquery.csv.min.js');

var Policy     = require(process.cwd() + '/app/models/policy');

var mongoose   = require('mongoose');
mongoose.connect('mongodb://cahl.berkeley.edu:1304/policies'); // ******put a /events after port to save into that db

// var csvWeekly = '../MASTER_user_info.csv';  // change this to location of email csv
var csvWeekly = '50_users.csv';  // change this to location of email csv
// var csvDaily = '/deepedu/research/moocdrop/live-data/prediction.csv'; // change this to location of prediction csv
var csvDaily = '/deepedu/research/moocdrop/live-data/moocdrop/50_pred.csv';

var gmailUsername = 'berkeleyx.communications@gmail.com'; // change to the account you want to have sending emails
var gmailPassword = 'AGfsdj45j&2jkfasdbjk$309vshadjkfhsadschsd32jhkjh!';
var secretUsername = 'john';  // change: must be shared with client.html
var secretPassword = 'secret'; // change: must be shared with client.html

// making anonID to email dict
var index_csv = csvWeekly;
var anon_to_email = {};
var all_ids = [];
fs.readFile(index_csv, 'UTF-8', function(err, csv) {
  $.csv.toArrays(csv, {}, function(err, data) {
    for(var i=1, len=data.length; i<len; i++) {
      if (data[i][3]) {
          all_ids.push(data[i][1]);
          anon_to_email[data[i][1]] = {'email': data[i][3]}; // email
          if (data[i][4]) {
            anon_to_email[data[i][1]].first = data[i][4].toUpperCase; // first name
          }
          if (data[i][5]) {
            anon_to_email[data[i][1]].last = data[i][5]; // last name
          }
      }
      else {
        continue;
      }
    }
  });
});

// var transporter = nodemailer.createTransport('smtps://' + gmailUsername + ':' + encodeURI(gmailPassword) + '@smtp.gmail.com', {pool:true, rateDelta:2000});
var transporter = nodemailer.createTransport('smtps://' + 'postmaster@sandbox76804c9965674d70aa186801c11a401e.mailgun.org' + ':' + encodeURI('9443478548bc8bd3aba3d6debba802f6') + '@smtp.mailgun.org');

// var my_auth = {
//     api_key: 'key-32232600888e04931773e38650963a0e',
//     domain: 'https://api.mailgun.net/v3/sandbox76804c9965674d70aa186801c11a401e.mailgun.org'
// };
// var transporter = nodemailer.createTransport({
//     service: 'Mailgun',
//     auth: my_auth
//   });

// These should exist on your server to use https
var pkey = fs.readFileSync('/etc/ssl/cahl.key').toString();
var pcert = fs.readFileSync('/etc/ssl/cahl.crt').toString();
var gd = [fs.readFileSync('/etc/ssl/gd_bundle.crt').toString()];

var options = {
    key: pkey,
    cert: pcert,
    ca: gd
};

// this will let us get the data from a POST
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

// set our port
var port = process.env.PORT || 1337;

app.use(function(req, res, next) {
  res.header("Access-Control-Allow-Origin", "*");
  res.header("Access-Control-Allow-Headers", "Authorization, Origin, X-Requested-With, Accept, X-CSRFToken, chap, seq, vert");
  res.header("Access-Control-Allow-Methods", "PUT, GET, POST");
  next();
});

// ROUTES FOR OUR API
// =============================================================================
var router = express.Router();

// middleware to use for all requests
router.use(function(req, res, next) {
    next();
});


function checkCredentials(credentials) {
  if (!credentials || credentials.name !== secretUsername || credentials.pass !== secretPassword) {
    return false;
  } else {
    return true;
  }
}

function myError(err) {
      if (err) {
          console.log(err);
          console.log("email send failed");
      }
}


 // on routes that end in /email
 // ----------------------------------------------------
router.route('/email')
    .post(function(req, res) {
      console.log(req.body.from === "");
      if (req.body.pass === 'sadfvkn88asVLS891') {
        var ids = req.body.ids;
        if (req.body.ann === 'true') {
          ids = all_ids;
        }
        for (var j = 0; j < ids.length; j++) {
          var id = ids[j];
          if (id in anon_to_email) {
              var message_body = req.body.body;
              var from = req.body.course + " Instructor" + " <" + gmailUsername +">";
              if (req.body.from) {
                from = "'" + req.body.from + "'" + " <" + gmailUsername +">";
              }
              if (anon_to_email[id].first) {
                message_body = message_body.replace('[:firstname:]', anon_to_email[id].first);
              }
              else {
                message_body = message_body.replace('[:firstname:]', '');
              }

              if (anon_to_email[id].first && anon_to_email[id].last) {
                message_body = message_body.replace('[:fullname:]', anon_to_email[id].first + " " + anon_to_email[id].last);
              }
              else {
                message_body = message_body.replace('[:fullname:]', '');
              }
              if (req.body.from === "") {
                message_body += "\n\nPlease do not repond to this email.";
              }
              sendEmail(anon_to_email[id].email, from, req.body.subject, message_body, req.body.reply, myError);
          }
          else {
            continue;
          }
        }

        res.send('sent');
      }
      else {
        res.send('Access Denied');
        res.end('Access denied');
      }
    });

function sendEmail(email, from, subject, content, reply, cb) {
      var mailOptions = {
          from: from, // sender name and address
          to: email, // list of receivers
          subject: subject, // subject line
          text: content, // plaintext body
          replyTo: reply //replyTo address
      };

      // send mail with defined transport object
      transporter.sendMail(mailOptions, function(error, info){
          if(error) {
              cb(error);
          }
          cb(null);
      });
}

// Sends the prediction file to the client
router.route('/predictions').get(function(req, res) {
  var credentials = auth(req);
  if (!checkCredentials(credentials)) {
    res.statusCode = 401;
    res.setHeader('WWW-Authenticate', 'Basic realm="cahl.berkeley.edu"');
    res.end('Access denied');
    return;
  }
  res.sendFile(csvDaily);
});

// Queries the database for just
router.route('/analytics').get(function(req, res) {
  query = Policy.find({"analytics": "true" }).sort({"timestamp": -1});

  query.exec(function (err, output) {
      if (err) {
        return next(err);
      }
      else {
        res.json(output);
      }
    });
});

router.route('/all').get(function(req, res) {
  query = Policy.find({"analytics": "false" }).sort({"timestamp" : -1});

  query.exec(function (err, output) {
      if (err) {
        return next(err);
      }
      else {
        res.json(output);
      }
    });
});

router.route('/save').post(function(req, res) {
  var policy = new Policy();
  if (req.body.analytics === 'true') {
    policy.ids = req.body.ids;
    policy.comp = req.body.comp;
    policy.attr = req.body.attr;
    policy.cert = req.body.cert;
    policy.auto = req.body.auto;
  }
  else {
    policy.ids = '';
    policy.comp = [];
    policy.attr = [];
    policy.cert = [];
    policy.auto = 'false';
  }
  policy.subject = req.body.subject;
  policy.from = req.body.from;
  policy.body = req.body.body;
  policy.reply = req.body.reply;
  policy.timestamp = req.body.timestamp;
  policy.analytics = req.body.analytics;

  policy.save(function(err) {
    if (err) {
      console.log("error when saving policy");
      res.end();
      return;
    }
  });
});

router.route('/changes').post(function(req, res) {
  console.log("changes");
  var p = {};
  p.ids = req.body.ids;
  p.from = req.body.from;
  p.reply = req.body.reply;
  p.subject = req.body.subject;
  p.body = req.body.body;
  p.comp = req.body.comp;
  p.attr = req.body.attr;
  p.cert = req.body.cert;
  p.auto = req.body.auto;

  Policy.update({"subject": req.body.old_subject}, {"$set": p}).exec();
  res.json({ message: 'Successfully saved' });
});

// This route exists only for testing your password
router.route('/').get(function(req, res) {
  var credentials = auth(req);
  if (!checkCredentials(credentials)) {
    res.statusCode = 401;
    res.setHeader('WWW-Authenticate', 'Basic realm="cahl.berkeley.edu"');
    res.end('Access denied');
    return;
  }
  res.send("You logged in");
});

// REGISTER OUR ROUTES -------------------------------
// all of our routes will be prefixed with /api
app.use('/api', router);

// START THE SERVER
// =============================================================================
https.createServer(options, app).listen(port);
console.log('Node server start on port: ' + port);
