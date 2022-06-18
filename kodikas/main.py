from unicodedata import name
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    status,
    APIRouter,
    Request,
    WebSocket,
    WebSocketDisconnect,
)

from fastapi import Depends, FastAPI
from kodikas.schemas import TestSchema, CommitData
from kodikas.utils.redis import Redis


app = FastAPI()

# Dependency for APIs
def redis_conn():
    return Redis().connection


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/test")
def test_message(request: Request, test_schema: TestSchema):

    return {
        "data": test_schema.text,
        "status_code": status.HTTP_200_OK,
        "success": True,
        "message": "",
    }


@app.post("/send")
def send_commit_data(
    request: Request,
    commit_data: CommitData,
    redis=Depends(redis_conn),
    status_code=status.HTTP_201_CREATED,
):
    """
    This API is primarily responsible for handling the data sent from github action
    and storing in redis and returning a success response upon completion also deletes
    the stored data of previous commit.
    """

    redis_sub_data_map = {
        "original_code": commit_data.original_code,
        "changed_code": commit_data.changed_code,
        "file_path": commit_data.file_path,
    }

    store_commit_data = redis.hset(
        name=commit_data.current_commit_sha, mapping=redis_sub_data_map
    )

    # At this point saving the current commit data is successful so we delete the data for previous commit
    if store_commit_data:
        redis.delete(commit_data.previous_commit_sha)

    return {
        "success": True,
        "message": "Commit data sent successfully.",
    }
