import asyncio
import os
import sys

import aiohttp
import asyncpg
from dotenv import load_dotenv

load_dotenv()


async def get_client():
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"))
    return conn


save_image_query = """
update nfts.metadata
set profile_image = $1
where chain_id = 1
    and contract_address ILIKE $2
    and token_id = $3
"""


contract_address = "0x1CB1A5e65610AEFF2551A50f76a87a7d3fB649C6"
url = "https://api.reservoir.tools/tokens/v6"
headers = {"accept": "*/*", "x-api-key": "demo-api-key"}
continuation_key = None
image_folder = "./images/"

# Create the image folder if it doesn't exist
if not os.path.exists(image_folder):
    os.makedirs(image_folder)


async def process_tokens(tokens):
    for token in tokens:
        token_id = token.get("token", {}).get("tokenId")
        image_url = token.get("token", {}).get("image")

        if image_url is None:
            image_url = token.get("token", {}).get("collection", {}).get("image")

        if image_url is None:
            print(f"Token {token_id} has no image URL. Skipping...")
            continue

        print(f"Saving image for token {token_id}...")
        while True:
            try:
                await client.execute(
                    save_image_query, image_url, contract_address, int(token_id)
                )
                break
            except Exception:
                print("Got an error from PG. Retrying...")
                continue


async def main():
    global continuation_key, client  # Declare continuation_key as a global variable
    client = await get_client()

    while True:
        params = {
            "contract": contract_address,
            "sortBy": "tokenId",
            "sortDirection": "asc",
            "limit": 100,
        }

        if continuation_key:
            params["continuation"] = continuation_key

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params, headers=headers) as response:
                    data = await response.json()

                    # Extract the continuation key from the response
                    continuation_key = data.get("continuation")

                    tokens = data.get("tokens", [])

                    await process_tokens(tokens)

                    # Break the loop if no more continuation key is provided
                    if not continuation_key:
                        break

            except aiohttp.ClientError as e:
                print("Error:", e)
                sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
