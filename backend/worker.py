import time
import json
from redis_connection import redis_client


print("Worker started, listening for tasks...")


while True:
    task_data = redis_client.blpop("tasks", timeout=0) # blocking pop #type:ignore
    if task_data:
        _, task_json = task_data #type:ignore
        task = json.loads(task_json)
        client_id = task["client_id"]
        payload = task["payload"]


        # Simulate long-running work
        print(f"Processing task for client {client_id}: {payload}")
        time.sleep(10)
        result = {"client_id": client_id, "result": f"Processed: {payload}"}
        redis_client.rpush("ready_tasks", json.dumps(result))
        print(f"Task for client {client_id} completed")