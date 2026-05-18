from fastapi import APIRouter, HTTPException

from app.agent.graph import run_agent
from app.logger import logger
from app.schemas.query import QueryRequest, QueryResponse

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest) -> QueryResponse:
    logger.info("query received", extra={"question": request.question})

    try:
        result = await run_agent(request.question)
        logger.info(
            "query succeeded", extra={"question": request.question, "sql": result.sql}
        )
        return result

    except Exception as e:
        logger.error(
            "query failed", extra={"question": request.question, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail=str(e))
