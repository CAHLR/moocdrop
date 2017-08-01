var mongoose     = require('mongoose');
var Schema       = mongoose.Schema;

var PolicySchema   = new Schema({
    name: String,
    ids: Array, // could be changed
    subject: String,
    body: String,
    reply: String,
    comp: Array, // could be changed
    attr: Array, // could be changed
    cert: Array, // could be changed
    auto: String,
    timestamp: String,
    intervention: String
});

module.exports = mongoose.model('Policy', PolicySchema);
