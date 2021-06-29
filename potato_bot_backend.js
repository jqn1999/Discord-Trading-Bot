require('dotenv').config()
const express = require('express');
const app = express();
const mongodb = require('mongodb');
const MongoClient = mongodb.MongoClient;
const uri = process.env.DATABASE_URL
var cors = require('cors')
app.use(cors())
app.use(express.json())

MongoClient.connect(uri, {useUnifiedTopology: true}, function (err, database){
    if (err) throw err;

    client = database;
    
    const port = process.env.PORT || 3000;
    app.listen(port, () => console.log(`Listening on port ${port}...`));
})

app.get('/', (req, res) => {
    res.send('Hello World');
})

// User Data Commands
app.get('/find/:database/:authorID', (req, res) => {
    var db = client.db('PotatoTrading')

    db.collection(req.params.database)
        .find({_id: parseInt(req.params.authorID)})
        .toArray(function (err, result){
            if (err) throw err
            res.send(result)
        })
})

app.get('/findoption/:authorID/:tickerStrikeType/:month/:day/:year', (req, res) => {
    var db = client.db('PotatoTrading')

    var fullTicker = req.params.tickerStrikeType + req.params.month + '/' + req.params.day + '/' + req.params.year
    db.collection('UserTrades')
        .find({_id: parseInt(req.params.authorID)})
        .project({openOptions: {$elemMatch:  {ticker: fullTicker}}})
        .toArray(function (err, result){
            if (err) throw err
            res.send(result)
        })
})

app.get('/findstockopen/:authorID/:ticker', (req, res) => {
    var db = client.db('PotatoTrading')

    db.collection('UserTrades')
        .find({_id: parseInt(req.params.authorID)})
        .project({openStocks: {$elemMatch:  {ticker: req.params.ticker}}})
        .toArray(function (err, result){
            if (err) throw err
            res.send(result)
        })
})

app.get('/findstockclosed/:authorID/:ticker', (req, res) => {
    var db = client.db('PotatoTrading')

    db.collection('UserTrades')
        .find({_id: parseInt(req.params.authorID)})
        .project({closedStocks: {$elemMatch:  {ticker: req.params.ticker}}})
        .toArray(function (err, result){
            if (err) throw err
            res.send(result)
        })
})

app.get('/findoptionopen/:authorID/:tickerStrikeType/:month/:day/:year', (req, res) => {
    var db = client.db('PotatoTrading')
    var fullTicker = req.params.tickerStrikeType + req.params.month + '/' + req.params.day + '/' + req.params.year

    db.collection('UserTrades')
        .find({_id: parseInt(req.params.authorID)})
        .project({openOptions: {$elemMatch:  {ticker: fullTicker}}})
        .toArray(function (err, result){
            if (err) throw err
            res.send(result)
        })
})

app.get('/findoptionclosed/:authorID/:tickerStrikeType/:month/:day/:year', (req, res) => {
    var db = client.db('PotatoTrading')
    var fullTicker = req.params.tickerStrikeType + req.params.month + '/' + req.params.day + '/' + req.params.year

    db.collection('UserTrades')
        .find({_id: parseInt(req.params.authorID)})
        .project({closedOptions: {$elemMatch:  {ticker: fullTicker}}})
        .toArray(function (err, result){
            if (err) throw err
            res.send(result)
        })
})

app.get('/updatepotatoes/:authorID/:newPotatoes', (req, res) => {
    var db = client.db('PotatoTrading')

    db.collection('UserData')
        .updateOne({_id: parseInt(req.params.authorID)}, {$set: {potatoes: parseFloat(req.params.newPotatoes)}})
    
    res.send(`${req.params.authorID}'s potatoes have been updated`)
})

app.get('/updatenumtrades/:authorID/:numTrades', (req, res) => {
    var db = client.db('PotatoTrading')

    db.collection('UserData')
        .updateOne({_id: parseInt(req.params.authorID)}, {$set: {numTrades: parseInt(req.params.numTrades)}})
    
    res.send(`${req.params.authorID}'s open trades amount has been updated`)
})

app.get('/updateopentrades/:authorID/:openTrades', (req, res) => {
    var db = client.db('PotatoTrading')

    db.collection('UserData')
        .updateOne({_id: parseInt(req.params.authorID)}, {$set: {openTrades: parseInt(req.params.openTrades)}})
    
    res.send(`${req.params.authorID}'s open trades amount has been updated`)
})

app.get('/updatewinningtrades/:authorID/:winningTrades', (req, res) => {
    var db = client.db('PotatoTrading')

    db.collection('UserData')
        .updateOne({_id: parseInt(req.params.authorID)}, {$set: {winningTrades: parseInt(req.params.winningTrades)}})
    
    res.send(`${req.params.authorID}'s winning trades amount has been updated`)
})

app.get('/updatelosingtrades/:authorID/:losingTrades', (req, res) => {
    var db = client.db('PotatoTrading')

    db.collection('UserData')
        .updateOne({_id: parseInt(req.params.authorID)}, {$set: {losingTrades: parseInt(req.params.losingTrades)}})
    
    res.send(`${req.params.authorID}'s losing trades amount has been updated`)
})

app.get('/updatetotalcost/:authorID/:totalCost', (req, res) => {
    var db = client.db('PotatoTrading')

    db.collection('UserData')
        .updateOne({_id: parseInt(req.params.authorID)}, {$set: {totalCost: parseFloat(req.params.totalCost)}})
    
    res.send(`${req.params.authorID}'s total cost amount has been updated`)
})

app.get('/updatetotalgain/:authorID/:totalGain', (req, res) => {
    var db = client.db('PotatoTrading')

    db.collection('UserData')
        .updateOne({_id: parseInt(req.params.authorID)}, {$set: {totalGain: parseFloat(req.params.totalGain)}})
    
    res.send(`${req.params.authorID}'s total gain amount has been updated`)
})

app.get('/updatetotalloss/:authorID/:totalLoss', (req, res) => {
    var db = client.db('PotatoTrading')

    db.collection('UserData')
        .updateOne({_id: parseInt(req.params.authorID)}, {$set: {totalLoss: parseFloat(req.params.totalLoss)}})
    
    res.send(`${req.params.authorID}'s total loss amount has been updated`)
})

// Trade Commands
app.get('/openstockopen/:authorID/:stock/:quantity/:totalCost', (req, res) => {
    var db = client.db('PotatoTrading')

    db.collection('UserTrades')
        .updateOne({_id: parseInt(req.params.authorID)}, {$push: {openStocks: {ticker: req.params.stock, quantity: parseInt(req.params.quantity), totalCost: parseFloat(req.params.totalCost)}}})
    
    res.send(`${req.params.authorID} has opened a stock position`)
})

app.get('/removestockopen/:authorID/:stock', (req, res) => {
    var db = client.db('PotatoTrading')

    db.collection('UserTrades')
        .updateOne({_id: parseInt(req.params.authorID)}, {$pull: {openStocks: {ticker: req.params.stock}}})
    
    res.send(`${req.params.authorID} has removed a stock position`)
})

app.get('/openstockclosed/:authorID/:stock/:quantity/:totalCost/:totalCredit', (req, res) => {
    var db = client.db('PotatoTrading')

    db.collection('UserTrades')
        .updateOne({_id: parseInt(req.params.authorID)}, {$push: {closedStocks: {ticker: req.params.stock, quantity: parseInt(req.params.quantity), totalCost: parseFloat(req.params.totalCost), totalCredit: parseFloat(req.params.totalCredit)}}})
    
    res.send(`${req.params.authorID} has opened a stock position`)
})

app.get('/removestockclosed/:authorID/:stock', (req, res) => {
    var db = client.db('PotatoTrading')

    db.collection('UserTrades')
        .updateOne({_id: parseInt(req.params.authorID)}, {$pull: {closedStocks: {ticker: req.params.stock}}})

    res.send(`${req.params.authorID} has removed a stock position`)
})

app.get('/openoptionopen/:authorID/:tickerStrikeType/:month/:day/:year/:quantity/:totalCost', (req, res) => {
    var db = client.db('PotatoTrading')
    
    var fullTicker = req.params.tickerStrikeType + req.params.month + '/' + req.params.day + '/' + req.params.year

    db.collection('UserTrades')
        .updateOne({_id: parseInt(req.params.authorID)}, {$push: {openOptions: {ticker: fullTicker, quantity: parseInt(req.params.quantity), totalCost: parseFloat(req.params.totalCost)}}})
    
    res.send(`${req.params.authorID} has opened an option position\n${fullTicker}`)
})

app.get('/removeoptionopen/:authorID/:tickerStrikeType/:month/:day/:year', (req, res) => {
    var db = client.db('PotatoTrading')
    var fullTicker = req.params.tickerStrikeType + req.params.month + '/' + req.params.day + '/' + req.params.year

    db.collection('UserTrades')
        .updateOne({_id: parseInt(req.params.authorID)}, {$pull: {openOptions: {ticker: fullTicker}}})
    
    res.send(`${req.params.authorID} has opened an option position\n${fullTicker}`)
})

app.get('/openoptionclosed/:authorID/:tickerStrikeType/:month/:day/:year/:quantity/:totalCost/:totalCredit', (req, res) => {
    var db = client.db('PotatoTrading')
    var fullTicker = req.params.tickerStrikeType + req.params.month + '/' + req.params.day + '/' + req.params.year

    db.collection('UserTrades')
        .updateOne({_id: parseInt(req.params.authorID)}, {$push: {closedOptions: {ticker: fullTicker, quantity: parseInt(req.params.quantity), totalCost: parseFloat(req.params.totalCost), totalCredit: parseFloat(req.params.totalCredit)}}})
    
    res.send(`${req.params.authorID} has opened an option position\n${fullTicker}`)
})

app.get('/removeoptionclosed/:authorID/:tickerStrikeType/:month/:day/:year', (req, res) => {
    var db = client.db('PotatoTrading')
    var fullTicker = req.params.tickerStrikeType + req.params.month + '/' + req.params.day + '/' + req.params.year

    db.collection('UserTrades')
        .updateOne({_id: parseInt(req.params.authorID)}, {$pull: {closedOptions: {ticker: fullTicker}}})
    
    res.send(`${req.params.authorID} has opened an option position\n${fullTicker}`)
})

// Active gain commands
app.get('/workupdate/:authorID/:potatoes/:time', (req, res) => {
    var db = client.db('PotatoTrading')

    db.collection('UserData')
        .updateOne({_id: parseInt(req.params.authorID)}, {$set: {potatoes: parseFloat(req.params.potatoes)} })

    db.collection('UserData')
        .updateOne({_id: parseInt(req.params.authorID)}, {$set: {workTimer: parseInt(req.params.time)} })

    res.send(`User ${req.params.authorID} has worked`)
})

// Misc commands
app.get('/register/:authorID',  (req, res) => {
    var db = client.db('PotatoTrading')

    db.collection('UserData')
        .findOne({'_id': parseInt(req.params.authorID)})
        .then((user) => {
            if (user){
                var id = parseFloat(req.params.authorID)
                res.send(user)
            }else{
                db.collection('UserData')
                .insertOne({_id: parseFloat(req.params.authorID), potatoes: 1000.00, workTimer: 0, coinTimer: 0, numTrades: 0, openTrades: 0,winningTrades: 0, losingTrades: 0, totalCost: 0.0, totalGain: 0.0, totalLoss: 0.0 })
                
                db.collection('UserTrades')
                    .insertOne({_id: parseFloat(req.params.authorID), openStocks: [], closedStocks: [], openOptions: [], closedOptions: []}) 
        
                res.send(user)
            }
        })
})

app.get('/updatemany/:database', (req, res) => {
    var db = client.db('PotatoTrading')

    db.collection(req.params.database)
        .updateMany({}, {$set: {'asdas': 'None'}})
        .then(() => {
            res.send("All users have been updated")
        })
})

app.get('/clearall', (req, res) => {
    var db = client.db('PotatoTrading')

    db.listCollections().forEach(element => {
        db.collection(String(element["name"]))
            .deleteMany({})
    })
    res.send("All collections have been cleared")
})