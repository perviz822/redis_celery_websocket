const WebSocket = require('ws');

const client =  process.argv[2] || '0'

const ws = new WebSocket(`ws://127.0.0.1:8000/w/${client}`);

ws.on('open',()=>{
    console.log("Connected!")
    ws.send(process.argv[3] || "A message")
})

ws.on('message',(data)=>{
    console.log("Message received",data.toString())
})

