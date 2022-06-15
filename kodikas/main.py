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

from fastapi import FastAPI, File, UploadFile
from kodikas.schemas import TestSchema


app = FastAPI()


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


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    print(file.filename)
    print("@@@@@@@@@@@@@@")
    contents = await file.read()
    print(contents)
    return {"filename": file.filename}
