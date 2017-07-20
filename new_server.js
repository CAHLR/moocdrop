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


// NEED TO CHANGE MASTER to get actual, copy over
var csvWeekly = '../MASTER_user_info.csv';  // change this to location of email csv
// var csvDaily = process.cwd() + '../studentPredictions.csv'; // change this to location of prediction csv
var csvDaily = '/deepedu/research/moocdrop/live-data/new_prediction.csv';
console.log(process.cwd());
var gmailUsername = 'berkeleyx.communications%40gmail.com'; // change to the account you want to have sending emails, escape @ as '%40'
var gmailPassword = 'AGfsdj45j&2jkfasdbjk$309vshadjkfhsadschsd32jhkjh!';
//change to match
var secretUsername = 'john';  // change: must be shared with client.html
var secretPassword = 'secret'; // change: must be shared with client.html

// making anonID to email dict
var index_csv = csvWeekly;
var anon_to_email = {};
fs.readFile(index_csv, 'UTF-8', function(err, csv) {
  $.csv.toArrays(csv, {}, function(err, data) {
    for(var i=1 , len=data.length; i<len; i++) {
      console.log(data[i][1]);
      if (data[i][1]) {
        anon_to_email[data[i][1]] = data[i][3];
      }
      else {
        continue;
      }
    }
  });
});

// making policy dictionary
var policy_dict = {};
policy_dict['test'] = ['43',' 77'];

var transporter = nodemailer.createTransport('smtps://' + gmailUsername + ':' + encodeURI(gmailPassword) + '@smtp.gmail.com');

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
var port = process.env.PORT || 1336;

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

 // on routes that end in /email
 // ----------------------------------------------------
router.route('/email')
    // get the ids for emails
    .post(function(req, res) {
        for (var j = 0; j < req.body.ids.length; j++) {
          // console.log(req.body.ids[j]);
          var id = req.body.ids[j];
          if (id in anon_to_email) {
            sendEmail(anon_to_email[id], req.body.subject, req.body.body, function (err) {
                if (err) {
                    console.log(err);
                    console.log("email send failed");
                }
            });
          }
          else {
            continue;
          }
        }
        res.send('sent');
    });

function sendEmail(email, subject, content, cb) {
    var mailOptions = {
        from: gmailUsername, // sender address
        to: email, // list of receivers
        subject: subject, // Subject line
        text: content // plaintext body
    };

    // send mail with defined transport object
    transporter.sendMail(mailOptions, function(error, info){
        if(error) {
            cb(error);
        }
        cb(null);
    });
}

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

router.route('/policies').get(function(req, res) {
  res.json(policy_dict);
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
//app.use(express.static('public'));
// START THE SERVER
// =============================================================================
https.createServer(options, app).listen(port);
//http.createServer(app).listen(port);
console.log('Node server start on port: ' + port);
