import asyncio
import os

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.db import (
    get_client,
    get_personality_query,
    get_posts_by_nft_query,
    schedule_posts,
)
from app.eth import index_aquanet

app = FastAPI()


@app.get("/posts")
async def get_posts(token_address: str, token_id: int):
    client = await get_client()

    posts = await client.fetch(get_posts_by_nft_query, token_address, token_id)
    return {"posts": posts}


@app.get("/personality")
async def get_personality(token_address: str, token_id: int):
    client = await get_client()
    row = await client.fetchrow(get_personality_query, token_address, token_id)
    if row is None:
        return JSONResponse(status_code=404, content={"error": "personality not found"})

    return {"personality": row}


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
