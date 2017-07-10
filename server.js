var express = require('express');
var app = express();
var bodyParser = require('body-parser');
var https = require('https');
var http = require('http');
var fs = require('fs');
var auth = require('basic-auth');
var csv = require('csvtojson');
var nodemailer = require('nodemailer');


var csvFilePath = 'studentEmails.csv';  // change this to location of email csv
var csvPredictionsPath = process.cwd() + '/studentPredictions.csv'; // change this to location of prediction csv
var gmailUsername = 'me%40gmail.com'; // change to the account you want to have sending emails, escape @ as '%40'
var gmailPassword = 'veryLongPassword';  //change to match
var secretUsername = 'john'  // change: must be shared with client.html
var secretPassword = 'secret' // change: must be shared with client.html

var transporter = nodemailer.createTransport('smtps://' + gmailUsername + ':' + gmailPassword + '@smtp.gmail.com');

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
var port = process.env.PORT || 1335;

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
        var fullList = [];
        var emailLookup = {};
        csv()
        .fromFile(csvFilePath)
        .on('json', function(jsonObj) {
            // combine csv header row and csv line to a json object
            // jsonObj.a ==> 1 or 4
            fullList.push(jsonObj);
        }).on('done', function(error) {
            for (var i = 0; i < fullList.length; i++) {
                var item = fullList[i];
                emailLookup[item.anonymizedId] = item.email;
            }
            var students = req.body.students;
            var email = req.body.email;
            for (var i = 0; i < students.length; i++) {
                var student = students[i];
                sendEmail(emailLookup[student.anonymizedId], email.Subject, email.Content, function (err) {
                    if (err) {
                        console.log("email send failed");
                    }
                });
            }
            res.send('sent');
        });
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
  res.sendFile(csvPredictionsPath);
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
