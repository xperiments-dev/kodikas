from fastapi import FastAPI, File, UploadFile
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
from typing import List

app = FastAPI()

origins = ["*"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency for APIs
def redis_conn():
    return Redis().connection


@app.get("/")
def read_root():
    return {"Hello": "You just discovered the root! Now find the branches ;)"}


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

    redis_sub_data_map = {"file_path": commit_data.file_path}

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


@app.post("/file-upload/")
def upload_commit_file(
    request: Request,
    filenames: List[UploadFile],
    redis=Depends(redis_conn),
    status_code=status.HTTP_200_OK,
):
    previous_commit = request.headers["x-previous-commit"]
    current_commit = request.headers["x-current-commit"]
    file_path = request.headers["x-file-path"]

    changed_contents = ""
    original_contents = ""

    for i in filenames:
        contents = i.file.read()

        if i.filename == "script.py":
            changed_contents = contents.decode("utf-8")

        elif i.filename == "main.py":
            original_contents = contents.decode("utf-8")

    redis_sub_data_map = {
        "file_path": file_path,
        "changed_file": changed_contents,
        "original_file": original_contents,
    }

    store_commit_data = redis.hset(name=current_commit, mapping=redis_sub_data_map)

    redis.hset(name=current_commit, key="original_file", value=contents)
    redis.hset(name=current_commit, key="changed_file", value=contents)

    # At this point saving the current commit data is successful so we delete the data for previous commit
    if store_commit_data:
        redis.delete(previous_commit)

    return {"success": True}


@app.get("/commit-data/")
def get_commit_data(
    commit_id: str,
    request: Request,
    redis=Depends(redis_conn),
    status_code=status.HTTP_200_OK,
):

    file_path = redis.hget(commit_id, "file_path")
    changed_file = redis.hget(commit_id, "changed_file")
    original_file = redis.hget(commit_id, "original_file")

    return {
        "success": True,
        "changed_file": changed_file,
        "original_file": original_file,
        "file_path": file_path,
    }
