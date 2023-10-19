# start the server
uvicorn src.main:app --host=0.0.0.0 --port=8002 --reload --forwarded-allow-ips="*"