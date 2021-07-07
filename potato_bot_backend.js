require('dotenv').config()
const express = require('express');
const app = express();
const mongodb = require('mongodb');
const MongoClient = mongodb.MongoClient;
const uri = process.env.DATABASE_URL
var cors = require('cors')
app.use(cors())
app.use(express.json())

var db;

MongoClient.connect(uri, {useUnifiedTopology: true}, function (err, database){
    if (err) throw err;

    client = database;
    db = client.db('PotatoTrading')

    const port = process.env.PORT || 3000;
    app.listen(port, () => console.log(`Listening on port ${port}...`));
})

// Home page
app.get('/', (req, res) => {
    res.send('Hello World');
})

// User Data Commands
app.get('/find/:database/:authorID', (req, res) => {
    db.collection(req.params.database)
        .find({_id: parseInt(req.params.authorID)})
        .toArray(function (err, result){
            if (err) throw err
            res.send(result)
        })
})

app.get('/findoption/:authorID/:tickerStrikeType/:month/:day/:year', (req, res) => {
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
    db.collection('UserTrades')
        .find({_id: parseInt(req.params.authorID)})
        .project({openStocks: {$elemMatch:  {ticker: req.params.ticker}}})
        .toArray(function (err, result){
            if (err) throw err
            res.send(result)
        })
})

app.get('/findstockclosed/:authorID/:ticker', (req, res) => {
    db.collection('UserTrades')
        .find({_id: parseInt(req.params.authorID)})
        .project({closedStocks: {$elemMatch:  {ticker: req.params.ticker}}})
        .toArray(function (err, result){
            if (err) throw err
            res.send(result)
        })
})

app.get('/findoptionopen/:authorID/:tickerStrikeType/:month/:day/:year', (req, res) => {
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
    db.collection('UserData')
        .updateOne({_id: parseInt(req.params.authorID)}, {$set: {potatoes: parseFloat(req.params.newPotatoes)}})
        .then(() => {
            res.send(`${req.params.authorID}'s potatoes have been updated`)
        })
})

app.get('/updatenumtrades/:authorID/:numTrades', (req, res) => {
    var db = client.db('PotatoTrading')

    db.collection('UserData')
        .updateOne({_id: parseInt(req.params.authorID)}, {$set: {numTrades: parseInt(req.params.numTrades)}})
        .then(() => {
            res.send(`${req.params.authorID}'s open trades amount has been updated`)
        })
})

app.get('/updateopentrades/:authorID/:openTrades', (req, res) => {
    db.collection('UserData')
        .updateOne({_id: parseInt(req.params.authorID)}, {$set: {openTrades: parseInt(req.params.openTrades)}})
        .then(() => {
            res.send(`${req.params.authorID}'s open trades amount has been updated`)
        })
})

app.get('/updatewinningtrades/:authorID/:winningTrades', (req, res) => {
    db.collection('UserData')
        .updateOne({_id: parseInt(req.params.authorID)}, {$set: {winningTrades: parseInt(req.params.winningTrades)}})
        .then(() => {
            res.send(`${req.params.authorID}'s winning trades amount has been updated`)
        })
})

app.get('/updatelosingtrades/:authorID/:losingTrades', (req, res) => {
    db.collection('UserData')
        .updateOne({_id: parseInt(req.params.authorID)}, {$set: {losingTrades: parseInt(req.params.losingTrades)}})
        .then(() => {
            res.send(`${req.params.authorID}'s losing trades amount has been updated`)
        })
})

app.get('/updatetotalcost/:authorID/:totalCost', (req, res) => {
    db.collection('UserData')
        .updateOne({_id: parseInt(req.params.authorID)}, {$set: {totalCost: parseFloat(req.params.totalCost)}})
        .then(() => {
            res.send(`${req.params.authorID}'s total cost amount has been updated`)
        })
})

app.get('/updatetotalgain/:authorID/:totalGain', (req, res) => {
    db.collection('UserData')
        .updateOne({_id: parseInt(req.params.authorID)}, {$set: {totalGain: parseFloat(req.params.totalGain)}})
        .then(() => {
            res.send(`${req.params.authorID}'s total gain amount has been updated`)
        })
})

app.get('/updatetotalloss/:authorID/:totalLoss', (req, res) => {
    db.collection('UserData')
        .updateOne({_id: parseInt(req.params.authorID)}, {$set: {totalLoss: parseFloat(req.params.totalLoss)}})
        .then(() => {
            res.send(`${req.params.authorID}'s total loss amount has been updated`)
        })
})

// Trade Commands
app.get('/openstockopen/:authorID/:stock/:quantity/:totalCost', (req, res) => {
    db.collection('UserTrades')
        .updateOne({_id: parseInt(req.params.authorID)}, {$push: {openStocks: {ticker: req.params.stock, quantity: parseInt(req.params.quantity), totalCost: parseFloat(req.params.totalCost)}}})
        .then(() => {
            res.send(`${req.params.authorID} has opened a stock position`)
        })
})

app.get('/removestockopen/:authorID/:stock', (req, res) => {
    db.collection('UserTrades')
        .updateOne({_id: parseInt(req.params.authorID)}, {$pull: {openStocks: {ticker: req.params.stock}}})
        .then(() => {
            res.send(`${req.params.authorID} has removed a stock position`)
        })
})

app.get('/openstockclosed/:authorID/:stock/:quantity/:totalCost/:totalCredit', (req, res) => {
    db.collection('UserTrades')
        .updateOne({_id: parseInt(req.params.authorID)}, {$push: {closedStocks: {ticker: req.params.stock, quantity: parseInt(req.params.quantity), totalCost: parseFloat(req.params.totalCost), totalCredit: parseFloat(req.params.totalCredit)}}})
        .then(() => {
            res.send(`${req.params.authorID} has opened a stock position`)
        })
})

app.get('/removestockclosed/:authorID/:stock', (req, res) => {
    db.collection('UserTrades')
        .updateOne({_id: parseInt(req.params.authorID)}, {$pull: {closedStocks: {ticker: req.params.stock}}})
        .then(() => {
            res.send(`${req.params.authorID} has removed a stock position`)
        })
})

app.get('/openoptionopen/:authorID/:tickerStrikeType/:month/:day/:year/:quantity/:totalCost', (req, res) => {
    var fullTicker = req.params.tickerStrikeType + req.params.month + '/' + req.params.day + '/' + req.params.year

    db.collection('UserTrades')
        .updateOne({_id: parseInt(req.params.authorID)}, {$push: {openOptions: {ticker: fullTicker, quantity: parseInt(req.params.quantity), totalCost: parseFloat(req.params.totalCost)}}})
        .then(() => {
            res.send(`${req.params.authorID} has opened an option position\n${fullTicker}`)
        })
})

app.get('/removeoptionopen/:authorID/:tickerStrikeType/:month/:day/:year', (req, res) => {
    var fullTicker = req.params.tickerStrikeType + req.params.month + '/' + req.params.day + '/' + req.params.year

    db.collection('UserTrades')
        .updateOne({_id: parseInt(req.params.authorID)}, {$pull: {openOptions: {ticker: fullTicker}}})
        .then(() => {
            res.send(`${req.params.authorID} has removed an option position\n${fullTicker}`)
        })
})

app.get('/openoptionclosed/:authorID/:tickerStrikeType/:month/:day/:year/:quantity/:totalCost/:totalCredit', (req, res) => {
    var fullTicker = req.params.tickerStrikeType + req.params.month + '/' + req.params.day + '/' + req.params.year

    db.collection('UserTrades')
        .updateOne({_id: parseInt(req.params.authorID)}, {$push: {closedOptions: {ticker: fullTicker, quantity: parseInt(req.params.quantity), totalCost: parseFloat(req.params.totalCost), totalCredit: parseFloat(req.params.totalCredit)}}})
        .then(() => {
            res.send(`${req.params.authorID} has opened an option position\n${fullTicker}`)
        })
})

app.get('/removeoptionclosed/:authorID/:tickerStrikeType/:month/:day/:year', (req, res) => {
    var fullTicker = req.params.tickerStrikeType + req.params.month + '/' + req.params.day + '/' + req.params.year

    db.collection('UserTrades')
        .updateOne({_id: parseInt(req.params.authorID)}, {$pull: {closedOptions: {ticker: fullTicker}}})
        .then(() => {
            res.send(`${req.params.authorID} has opened an option position\n${fullTicker}`)
        })
})

// Active gain commands
app.get('/workupdate/:authorID/:potatoes/:time', (req, res) => {
    db.collection('UserData')
        .updateOne({_id: parseInt(req.params.authorID)}, {$set: {potatoes: parseFloat(req.params.potatoes)} })
        .then(() => {
            res.send(`User ${req.params.authorID} has worked`)
        })

    db.collection('UserData')
        .updateOne({_id: parseInt(req.params.authorID)}, {$set: {workTimer: parseInt(req.params.time)} })
        .then(() => {
            res.send(`User ${req.params.authorID} has worked`)
        })

})

// Gambling commands
app.get('/flipupdate/:authorID/:potatoes/:time', (req, res) => {
    db.collection('UserData')
        .updateOne({_id: parseInt(req.params.authorID)}, {$set: {potatoes: parseFloat(req.params.potatoes)} })
        .then(() => {
            res.send(`User ${req.params.authorID} has flipped`)
        })
    db.collection('UserData')
        .updateOne({_id: parseInt(req.params.authorID)}, {$set: {coinTimer: parseInt(req.params.time)} })
        .then(() => {
            res.send(`User ${req.params.authorID} has flipped`)
        })
})

// Game and monster
app.get('/findmonsters', (req, res) => {
    db.collection('GameVariables')
        .find({_id: "monsterList"})
        .toArray(function (err, result){
            if (err) throw err
            res.send(result)
        })
})

app.get('/addmonster/:name/:type/:experience/:hp/:attack', (req, res) => {
    db.collection('GameVariables')
        .updateOne({_id: "monsterList"}, {$push: {regular: {name: req.params.name, type: req.params.type, experience: parseInt(req.params.experience), health: parseInt(req.params.hp), attack: parseInt(req.params.attack)}}})
        .then(() => {
            res.send(`Monster has been added`)
        })
})

app.get('/huntupdate/:authorID/:time', (req, res) => {
    db.collection('UserData')
        .updateOne({_id: parseInt(req.params.authorID)}, {$set: {huntTimer: parseInt(req.params.time)} })
        .then(() => {
            res.send(`User ${req.params.authorID} has hunted`)
        })
})

app.get('/gameuserupdate/:authorID/:level/:experience/:regular/:epic/:legend/:mythic', (req, res) => {
    db.collection('UserGameStats')
        .updateOne({_id: parseInt(req.params.authorID)}, {$set: {level: parseInt(req.params.level)} })
        .then(() => {
            res.send(`User ${req.params.authorID}`)
        })

    db.collection('UserGameStats')
        .updateOne({_id: parseInt(req.params.authorID)}, {$set: {experience: parseInt(req.params.experience)} })
        .then(() => {
            res.send(`User ${req.params.authorID}`)
        })

    db.collection('UserGameStats')
        .updateOne({_id: parseInt(req.params.authorID)}, {$set: {regularKills: parseInt(req.params.regular)} })
        .then(() => {
            res.send(`User ${req.params.authorID}`)
        })
    db.collection('UserGameStats')
        .updateOne({_id: parseInt(req.params.authorID)}, {$set: {epicKills: parseInt(req.params.epic)} })
        .then(() => {
            res.send(`User ${req.params.authorID}`)
        })
    db.collection('UserGameStats')
        .updateOne({_id: parseInt(req.params.authorID)}, {$set: {legendaryKills: parseInt(req.params.legend)} })
        .then(() => {
            res.send(`User ${req.params.authorID}`)
        })
    db.collection('UserGameStats')
        .updateOne({_id: parseInt(req.params.authorID)}, {$set: {mythicKills: parseInt(req.params.mythic)} })
        .then(() => {
            res.send(`User ${req.params.authorID}`)
        })
})

app.get('/updatelosses/:authorID/:losses', (req, res) => {
    db.collection('UserGameStats')
        .updateOne({_id: parseInt(req.params.authorID)}, {$set: {losses: parseInt(req.params.losses)} })
        .then(() => {
            res.send(`User ${req.params.authorID} has updated losses`)
        })
})

app.get('/updatehuntgain/:authorID/:gain', (req, res) => {
    db.collection('UserGameStats')
        .updateOne({_id: parseInt(req.params.authorID)}, {$set: {totalGain: parseInt(req.params.gain)} })
        .then(() => {
            res.send(`User ${req.params.authorID} has updated totalGain ${req.params.gain}}`)
        })
})

// Misc commands
app.get('/register/:authorID/:name',  (req, res) => {
    db.collection('UserData')
        .findOne({'_id': parseInt(req.params.authorID)})
        .then((user) => {
            if (user){
                var id = parseFloat(req.params.authorID)
                res.send(user)
            }else{
                db.collection('UserData')
                .insertOne({_id: parseFloat(req.params.authorID), name: req.params.name, rank: "Spud", potatoes: 1000.00, workTimer: 0, coinTimer: 0, huntTimer: 0, numTrades: 0, openTrades: 0,winningTrades: 0, losingTrades: 0, totalCost: 0.0, totalGain: 0.0, totalLoss: 0.0 })
                
                db.collection('UserTrades')
                    .insertOne({_id: parseFloat(req.params.authorID), name: req.params.name, openStocks: [], closedStocks: [], openOptions: [], closedOptions: []}) 
                
                db.collection('UserGameStats')
                    .insertOne({_id: parseFloat(req.params.authorID), name: req.params.name, level: 1, experience: 0, regularKills: 0, epicKills: 0, legendaryKills: 0, mythicKills: 0, losses: 0, totalGain: 0})
        
                res.send(user)
            }
        })
})

app.get('/testregister/:authorID', (req, res) => {
    db.collection('UserGameStats')
        .insertOne({_id: parseFloat(req.params.authorID), level: 1, experience: 0, regularKills: 0, epicKills: 0, legendaryKills: 0, mythicKills: 0})
        .then(() => {
            res.send("User has been test registered")
        })
})

app.get('/addgamevariable/:name', (req, res) => {
    varName = req.params.name
    db.collection('GameVariables')
        .insertOne({_id: varName, regular: [], epic: [], legendary: [], mythic: []})
        .then(() => {
            res.send("Game variable added")
        })
})

app.get('/updatemany/:database', (req, res) => {
    db.collection(req.params.database)
        .updateMany({}, {$set: {rank: "Spud"}})
        .then(() => {
            res.send("All users have been updated")
        })
})

app.get('/clearall', (req, res) => {
    /*
    db.listCollections().forEach(element => {
        db.collection(String(element["name"]))
            .deleteMany({})
    })*/

    db.collection("UserData")
        .deleteMany({})
    db.collection("UserTrades")
        .deleteMany({})
    db.collection("UserGameStats")
        .deleteMany({})
    res.send("All collections have been cleared")
})