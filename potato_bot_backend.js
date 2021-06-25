require('dotenv').config()
const express = require('express');
const app = express();
const mongodb = require('mongodb');
const MongoClient = mongodb.MongoClient;
const uri = process.env.DATABASE_URL
var cors = require('cors')
app.use(cors())
app.use(express.json())

app.get('/', (req, res) => {
    res.send('Hello World');
})

app.get('/register/:authorID',  (req, res) => {
    MongoClient.connect(uri, {useUnifiedTopology: true}, function (err, client) {
        if (err) throw err

        var db = client.db('PotatoTrading')
        db.collection('UserData')
            .findOne({'_id': parseInt(req.params.authorID)})
            .then((user) => {
                if (user){
                    res.send(user)
                }else{
                    db.collection('UserData')
                    .insertOne({'_id': parseInt(req.params.authorID), 'potatoes': 1000.00, 'workTimer': 0, 'coinTimer': 0, 'numTrades': 0, 'openTrades': 0,'winningTrades': 0, 'losingTrades': 0, 'totalCost': 0.0, 'totalGain': 0.0, 'totalLoss': 0.0 })
                    
                    db.collection('UserTrades')
                        .insertOne({'_id': parseInt(req.params.authorID), 'openStocks': [], 'closedStocks': [], 'openOptions': [], 'closedOptions': []}) 
            
                    res.send(user)
                }
            })
    })
})

app.get('/find/:database/:authorID', (req, res) => {
    MongoClient.connect(uri, {useUnifiedTopology: true}, function (err, client) {
        if (err) throw err
  
        var db = client.db('PotatoTrading')

        /*db.collection('UserData')
            .findOne({'_id': parseInt(req.params.authorID)})
            .then((user) => {
                res.send(user)
            })*/

        db.collection(req.params.database)
            .find({'_id': parseInt(req.params.authorID)})
            .toArray(function (err, result){
                if (err) throw err
                res.send(result)
            })
    })
})

app.get('/workupdate/:authorID/:potatoes/:time', (req, res) => {
    MongoClient.connect( uri, {useUnifiedTopology: true}, function (err, client) {
        if (err) throw err

        var db = client.db('PotatoTrading')

        db.collection('UserData')
            .updateOne({'_id': parseInt(req.params.authorID)}, {'$set': {'potatoes': parseFloat(req.params.potatoes)} })

        db.collection('UserData')
            .updateOne({'_id': parseInt(req.params.authorID)}, {'$set': {'workTimer': parseInt(req.params.time)} })

        res.send(`User ${req.params.authorID} has worked`)
    })
})

app.get('/updatemany/:database', (req, res) => {
    MongoClient.connect( uri, {useUnifiedTopology: true}, function (err, client) {
        if (err) throw err

        var db = client.db('PotatoTrading')

        db.collection(req.params.database)
            .updateMany({}, {'$set': {'asdas': 'None'}})
            .then(() => {
                res.send("All users have been updated")
            })
    })
})

app.get('/clearall', (req, res) => {
    MongoClient.connect( uri, {useUnifiedTopology: true}, function (err, client) {
        if (err) throw err

        var db = client.db('PotatoTrading')

        db.listCollections().forEach(element => {
            db.collection(String(element["name"]))
                .deleteMany({})
        })
        res.send("All collections have been cleared")
    })
})

const port = process.env.PORT || 3000;
app.listen(port, () => console.log(`Listening on port ${port}...`));