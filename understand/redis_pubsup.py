import asyncio, redis.asyncio as redis, json

async def  publish_to_channel(r):
     await asyncio.sleep(7)
     await r.publish("ping.demo",json.dumps({"msg":"pong"}))


async def  publish_to_channel_2(r):
     await asyncio.sleep(10)
     await r.publish("ping.demo",json.dumps({"msg":"pong"}))     
     


async def main():
    r = redis.from_url("redis://localhost:6379")
    pubsub = r.pubsub()
    await pubsub.psubscribe("ping.*") # subscribing to  channel ping
    asyncio.create_task(publish_to_channel(r))
    asyncio.create_task(publish_to_channel_2(r))
    async for m in pubsub.listen():
         if m["type"] =="pmessage":
              print("Got the message")
              
    await pubsub.close()          




asyncio.run(main())



