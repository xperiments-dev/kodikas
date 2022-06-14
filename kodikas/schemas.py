from pydantic import BaseModel


class TestSchema(BaseModel):
    text: str
