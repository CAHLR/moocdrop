var express = require('express');
var app = express();
var bodyParser = require('body-parser');
var $ = jQuery = require('jquery');
require('./jquery.csv.min.js');
var https = require('https');
var http = require('http');
var fs = require('fs');
var querystring = require('querystring');

var pkey = fs.readFileSync('/etc/ssl/cahl.key').toString();
var pcert = fs.readFileSync('/etc/ssl/cahl.crt').toString();
var gd = [fs.readFileSync('/etc/ssl/gd_bundle.crt').toString()];

var options = {
    key: pkey,
    cert: pcert,
    ca: gd
};

// TODO: create a dict for alias to email

// create index to url dict
// create url to index dict
// var index_csv = 'mappings.csv';
// var index_to_url_name = {};
// var url_name_to_index = {};
// fs.readFile(index_csv, 'UTF-8', function(err, csv) {
//   $.csv.toArrays(csv, {}, function(err, data) {
//     for(var i=1 , len=data.length; i<len; i++) {
//       index_to_url_name[data[i][0]] = data[i][1];
//       url_name_to_index[data[i][1]] = data[i][0];
//     }
//   });
// });

// this will let us get the data from a POST
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

// set our port
var port = process.env.PORT || 1335;

app.use(function(req, res, next) {
  res.header("Access-Control-Allow-Origin", "*");
  res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Accept, X-CSRFToken, chap, seq, vert");
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

 // on routes that end in /email
 // ----------------------------------------------------
   router.route('/email')
       // get the ids for emails
       .post(function(req, res) {
             var ids = req.body.ids;
             for (i = 0; i < ids.length; i++) {
               console.log(ids[i]);
             }
        });

// REGISTER OUR ROUTES -------------------------------
// all of our routes will be prefixed with /api
app.use('/api', router);
app.use(express.static('public'));
// START THE SERVER
// =============================================================================
https.createServer(options, app).listen(port);
console.log('Node server start on port: ' + port);
