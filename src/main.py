from fastapi import FastAPI, Request
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from Secweb import SecWeb
from src.google.routers import google_router


load_dotenv()


app = FastAPI(
    title="Eagle Bot API Automations",
    version="1.0.0",
)

# import debugpy
# debugpy.listen(("0.0.0.0", 5678))
# print("Waiting for client to attach...")
# debugpy.wait_for_client()


# @app.middleware("http")
# async def set_permissions_policy_header(request: Request, call_next):
#     response = await call_next(request)
#     response.headers["Permissions-Policy"] = ""
#     return response


# SecWeb(
#     app=app,
#     Option={
#         "hsts": {"max-age": 2592000},
#         "csp": {
#             "object-src": ["'none'"],
#             "style-src": ["'self'", "'unsafe-inline'"],
#             "script-src": ["'self'", "'unsafe-inline'"],
#             "base-uri": ["'self'"],
#         },
#     },
# )


# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

app.add_middleware(GZipMiddleware)


app.include_router(google_router)


@app.get("/")
def root():
    return {"message": "application started successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
