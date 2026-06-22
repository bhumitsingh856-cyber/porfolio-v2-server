from contextlib import asynccontextmanager
from fastapi import FastAPI, Request 
from fastapi.responses import StreamingResponse
from app.agent import graph
from app.checkpointer import pool , checkpointer
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langchain_core.messages import HumanMessage
from fastapi.middleware.cors import CORSMiddleware
@asynccontextmanager
async def lifespan(app):
    await pool.open()
    checkpointer = AsyncPostgresSaver(pool)
    await checkpointer.setup()
    app.state.graph = graph.compile(checkpointer=checkpointer)
    yield
    await pool.close()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ask")
async def ask(req: Request):
    data = await req.json()
    agent = req.app.state.graph

    async def generator():
        async for msg, meta in agent.astream(
            {
                "messages": [
                    HumanMessage(
                        content=data['query']
                    )
                ]
            },
            {"configurable": {"thread_id": data["thread"]}},
            stream_mode="messages",
        ):
            if meta.get("langgraph_node") == "chat":
                if msg.content:
                    yield f"{msg.content}"
    return StreamingResponse(generator(), media_type="text/event-stream")

