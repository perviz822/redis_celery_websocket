from celery_app import celery_app
import time

@celery_app.task
def process_task(client_id, payload):
    print(f"Processing task for client {client_id}: {payload}")
    time.sleep(10)  # simulate long-running work
    result = f"Processed: {payload}"
    print(f"Task for client {client_id} completed")
    return {"client_id": client_id, "result": result}
