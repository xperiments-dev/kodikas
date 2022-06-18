from pydantic import BaseModel


class TestSchema(BaseModel):
    text: str


class CommitData(BaseModel):
    previous_commit_sha: str
    current_commit_sha: str
    changed_code: str
    original_code: str
    file_path: str
