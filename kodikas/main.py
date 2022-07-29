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
from typing import List, final
import requests


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

    for i in filenames:
        contents = i.file.read()

        if i.filename == "changed_file.py":
            changed_contents = contents.decode("utf-8")
            redis.hset(name=current_commit, key="changed_file", value=changed_contents)

        elif i.filename == "original_file.py":
            original_contents = contents.decode("utf-8")
            redis.hset(
                name=current_commit, key="original_file", value=original_contents
            )

    redis.hset(name=current_commit, key="file_path", value=file_path)

    # At this point saving the current commit data is successful so we delete the data for previous commit
    # if store_commit_data:
    #     redis.delete(previous_commit)

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


@app.get("/repos/")
def get_all_repos(
    request: Request,
    redis=Depends(redis_conn),
    repo_name: str = None,
    status_code=status.HTTP_200_OK,
):

    """API to get all the repos for an organisation."""

    import os
    from dotenv import load_dotenv

    load_dotenv()

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"token {os.getenv('GITHUB_TOKEN')}",
    }

    final_response = []
    if not repo_name:

        all_repos = requests.get(
            "https://api.github.com/orgs/xperiments-dev/repos", headers=headers
        )

        for repo in all_repos.json():
            final_response.append({"repo_id": repo["id"], "repo_name": repo["name"]})

    else:
        get_repo = requests.get(
            f"https://api.github.com/repos/xperiments-dev/{repo_name}", headers=headers
        )

        for repo in get_repo.json():
            final_response.append(repo["name"])

    return {"success": True, "repos": final_response}


@app.get("/prs/")
def get_prs(
    request: Request,
    redis=Depends(redis_conn),
    repo_name: str = None,
    status_code=status.HTTP_200_OK,
):
    import os
    from dotenv import load_dotenv

    load_dotenv()

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"token {os.getenv('GITHUB_TOKEN')}",
    }
    final_response = []
    if repo_name:

        get_prs = requests.get(
            f"https://api.github.com/repos/xperiments-dev/{repo_name}/pulls",
            headers=headers,
        )

        for pr_data in get_prs.json():
            final_response.append(
                {
                    "pr_url": pr_data["url"],
                    "pr_title": pr_data["title"],
                    "pr_state": pr_data["state"],
                    "pr_number": pr_data["number"],
                    "latest_commit_id": pr_data["head"]["sha"],
                    "pr_json_data": pr_data,
                }
            )

        return {"success": True, "repos": final_response}

    else:
        return {"success": False, "repos": final_response}
