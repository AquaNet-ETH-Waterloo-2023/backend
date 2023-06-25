import asyncio
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.db import (
    get_client,
    get_friends_query,
    get_personality_by_nft_query,
    get_posts_by_id_query,
    get_posts_by_nft_query,
    get_posts_query,
    schedule_posts,
)
from app.eth import index_aquanet

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
    "https://aquanet.app",
    "https://web-git-main-aquanet.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/posts")
async def get_posts(token_address: str, token_id: int):
    client = await get_client()

    posts = await client.fetch(get_posts_by_nft_query, token_address, token_id)
    return {"posts": posts}


@app.get("/personality")
async def get_personality(token_address: str, token_id: int):
    client = await get_client()
    row = await client.fetchrow(get_personality_by_nft_query, token_address, token_id)
    if row is None:
        return JSONResponse(status_code=404, content={"error": "personality not found"})

    return {"personality": row}


@app.get("/friends")
async def get_friends():
    client = await get_client()
    rows = await client.fetch(get_friends_query)
    return {"friends": rows}


@app.get("/posts/all")
async def get_posts(author_id: int | None = None):
    client = await get_client()
    if author_id is None:
        rows = await client.fetch(get_posts_query)
        return {"posts": rows}

    rows = await client.fetch(get_posts_by_id_query, author_id)
    return {"posts": rows}


@app.on_event("startup")
async def startup_loop():
    loop = asyncio.get_event_loop()
    loop.create_task(main())


async def main():
    post_task = schedule_posts()
    index_task = index_aquanet()
    tasks = [post_task, index_task]
    for coroutine in asyncio.as_completed(tasks):
        try:
            results = await coroutine
        except Exception as e:
            print(e)
        else:
            print("Finished:", results)


if __name__ == "__main__":
    import uvicorn

    port = os.getenv("PORT", 8000)
    uvicorn.run(app, host="0.0.0.0", port=int(port))
