# start the server
uvicorn src.main:app --host=0.0.0.0 --port=8000 --reload --forwarded-allow-ips="*"