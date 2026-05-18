from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(
        ..., min_length=1, max_length=1000, description="Question en langage naturel"
    )


class QueryResponse(BaseModel):
    question: str
    sql: str
    result: list[dict]
    explanation: str
