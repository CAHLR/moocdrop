var express = require('express');
var app = express();
var bodyParser = require('body-parser');
var $ = jQuery = require('jquery');
require('./jquery.csv.min.js');
var https = require('https');
var http = require('http');
var fs = require('fs');
var querystring = require('querystring');

var pkey = fs.readFileSync('/etc/ssl/server.key').toString();
var pcert = fs.readFileSync('/etc/ssl/server.crt').toString();
var gd = [fs.readFileSync('/etc/ssl/gd_bundle.crt').toString()];

var options = {
    key: pkey,
    cert: pcert,
    ca: gd
};

// TODO: create a dict for alias to email

// create index to url dict
// create url to index dict
var index_csv = 'mappings.csv';
var index_to_url_name = {};
var url_name_to_index = {};
fs.readFile(index_csv, 'UTF-8', function(err, csv) {
  $.csv.toArrays(csv, {}, function(err, data) {
    for(var i=1 , len=data.length; i<len; i++) {
      index_to_url_name[data[i][0]] = data[i][1];
      url_name_to_index[data[i][1]] = data[i][0];
    }
  });
});

// this will let us get the data from a POST
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

// set our port
var port = process.env.PORT || port;

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

 // on routes that end in /rec
 // ----------------------------------------------------
   router.route('/rec')
       // get the recommendation (accessed at POST http://server:1334/rec)
       .post(function(req, res) {
             var dropOutLow = req.body.dropOutLow;
             var dropOutHigh = req.body.dropOutHigh;
             var compLow = req.body.compLow;
             var compHigh = req.body.compHigh;
             var certLow = req.body.certLow;
             var certHigh = req.body.certHigh;

             var post_data = 5;// data request to model goes here

             var post_options = {
                host: 'server',
                port: 'port',
                path: '/rec',
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Content-Length': Buffer.byteLength(post_data)
              }
            };

            // data is the response
            var post_req = http.request(post_options, function(response) {
                  response.setEncoding('utf8');
                  response.on('data', function (data) {
                    var result;
                    var final;
                     if (data.length > 0) {
                        result = data.split(" "); // make the model return the alias in a string with a space in between 
                        for (a = 0; a < result.length; a++) {
                            final.push(alias_to_email[result[a]]);
                        }
                     }
                     else {
                         res.status(500).send('No data from Oracle');
                     }
                     res.json({array: final});
                   });

            });

            post_req.on('error', function(e) {
                res.end();
            });

        });

// REGISTER OUR ROUTES -------------------------------
// all of our routes will be prefixed with /api
app.use('/api', router);
app.use(express.static('public'));
// START THE SERVER
// =============================================================================
https.createServer(options, app).listen(port);
console.log('Node server start on port: ' + port);
