import asyncio

from fastapi.responses import JSONResponse

from app.ai import generate_bio, generate_tone, generate_username
from app.db import (
    create_personality_query,
    get_client,
    get_metadata_by_id_query,
    get_new_aquanet_profiles_query,
    get_personality_query,
)
from app.util import get_character_type, pick_random_frequency


async def create_personality(id: int):
    client = await get_client()
    metadata_row = await client.fetchrow(get_metadata_by_id_query, id)

    if metadata_row is None:
        return JSONResponse(status_code=404, content={"error": "metadata not found"})

    personality_row = await client.fetchrow(get_personality_query, metadata_row["id"])

    if personality_row is not None:
        return JSONResponse(
            status_code=400, content={"error": "personality already exists"}
        )

    project_name = get_character_type(metadata_row["contract_address"])
    username = generate_username(project_name, metadata_row["metadata"])
    bio = generate_bio(
        project_name,
        username,
        metadata_row["metadata"],
    )
    frequency = pick_random_frequency()
    tone = generate_tone(bio)

    item = await client.fetch(
        create_personality_query, metadata_row["id"], username, bio, frequency, tone
    )

    return item


async def check_for_new_aquanet_profiles():
    client = await get_client()

    while True:
        try:
            # pick up any new aquanet ids
            rows = await client.fetch(get_new_aquanet_profiles_query)

            for row in rows:
                id = row["id"]
                await create_personality(id)

        except Exception as e:
            print("Error in check_for_new_aquanet_profiles:", e)

        await asyncio.sleep(8)
