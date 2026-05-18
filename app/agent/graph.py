from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode
from typing import TypedDict, Annotated
import operator

from app.agent.tools import list_tables, get_table_schema, run_sql_query
from app.config import settings
from app.logger import logger
from app.schemas.query import QueryResponse


# ----------------------------------------------------------------
# State
# ----------------------------------------------------------------
class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    question: str
    sql: str
    result: str
    explanation: str


# ----------------------------------------------------------------
# LLM + tools
# ----------------------------------------------------------------
llm = ChatBedrock(
    model_id=settings.bedrock_model_id,
    region_name=settings.aws_region,
    model_kwargs={"max_tokens": settings.bedrock_max_tokens},
)

tools = [list_tables, get_table_schema, run_sql_query]
llm_with_tools = llm.bind_tools(tools)
tool_node = ToolNode(tools)

SYSTEM_PROMPT = """Tu es un agent SQL expert. Tu as accès à un Glue Data Catalog AWS.
Pour répondre à une question :
1. Liste les tables disponibles
2. Récupère le schéma des tables pertinentes
3. Génère et exécute la requête SQL appropriée
4. Explique le résultat en langage naturel

Génère uniquement des requêtes SELECT. N'exécute jamais de DDL ou DML."""


# ----------------------------------------------------------------
# Nodes
# ----------------------------------------------------------------
def agent_node(state: AgentState) -> AgentState:
    logger.info("agent node", extra={"question": state["question"]})
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        *state["messages"],
    ]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


def should_continue(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "finalize"


def finalize_node(state: AgentState) -> AgentState:
    """Extrait le SQL, le résultat et l'explication du dernier message."""
    messages = state["messages"]

    sql = ""
    result = ""
    for msg in reversed(messages):
        if hasattr(msg, "tool_calls"):
            for tc in msg.tool_calls:
                if tc["name"] == "run_sql_query" and not sql:
                    sql = tc["args"].get("query", "")
        if hasattr(msg, "content") and isinstance(msg.content, str) and not result:
            result = msg.content

    return {
        "sql": sql,
        "result": result,
        "explanation": messages[-1].content if messages else "",
    }


# ----------------------------------------------------------------
# Graph
# ----------------------------------------------------------------
def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)
    graph.add_node("finalize", finalize_node)

    graph.add_edge(START, "agent")
    graph.add_conditional_edges(
        "agent", should_continue, {"tools": "tools", "finalize": "finalize"}
    )
    graph.add_edge("tools", "agent")
    graph.add_edge("finalize", END)

    return graph.compile()


agent = build_graph()


# ----------------------------------------------------------------
# Entrypoint
# ----------------------------------------------------------------
async def run_agent(question: str) -> QueryResponse:
    logger.info("running agent", extra={"question": question})

    initial_state: AgentState = {
        "messages": [HumanMessage(content=question)],
        "question": question,
        "sql": "",
        "result": "",
        "explanation": "",
    }

    final_state = await agent.ainvoke(initial_state)

    return QueryResponse(
        question=question,
        sql=final_state["sql"],
        result=final_state["result"],
        explanation=final_state["explanation"],
    )
