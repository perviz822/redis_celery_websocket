## How to run

1. Install    libraries -> `pip install requirements.txt`
2. Go to backend folder -> `cd backend`
3. Run ` uvicorn main:app --reload`
4. Inside backend folder run these commands to start  queue and celery

```
python redis_connection.py
```

```
python celery_app.py
celery -A tasks.celery_app worker --loglevel=info
```

To  visualize celery workers (optional)

`celery -A celery_app.celery_app flower --port=5555`

To visualize the redis queue

```
docker run -d --name redisinsight -p 8001:8001 redislabs/redisinsight:latest

```
