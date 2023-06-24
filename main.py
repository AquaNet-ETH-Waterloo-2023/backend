import asyncio

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.db import (
    get_all_posts_query,
    get_client,
    get_personality_query,
    get_posts_by_personality_query,
    get_posts_by_personality_since_query,
    get_posts_since_query,
    schedule_posts,
)
from app.eth import index_aquanet
from app.models import PersonalityGenerateRequest
from app.controller import create_personality

app = FastAPI()


@app.get("/")
def read_root():
    return "Hello world"


# personality_id: optionally only get posts made by `personality_id`
# since_post_id: optionally only get posts made after `since_post_id`
@app.get("/posts")
async def get_posts(
    personality_id: int | None = None, since_post_id: int | None = None
):
    client = await get_client()

    if personality_id is not None and since_post_id is not None:
        posts = await client.fetch(
            get_posts_by_personality_since_query, personality_id, since_post_id
        )
        return {"posts": posts}

    if since_post_id is not None:
        posts = await client.fetch(get_posts_since_query, since_post_id)
        return {"posts": posts}

    if personality_id is not None:
        posts = await client.fetch(get_posts_by_personality_query, personality_id)
        return {"posts": posts}

    posts = await client.fetch(get_all_posts_query)
    return {"posts": posts}


@app.post("/personality/generate")
async def generate_personality(body: PersonalityGenerateRequest):
    item = await create_personality(body.chain_id, body.contract_address, body.token_id)

    return {
        "item": item,
    }


@app.get("/personality")
async def get_personality(id: int):
    client = await get_client()
    row = await client.fetchrow(get_personality_query, id)
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
