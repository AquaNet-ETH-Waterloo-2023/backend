import asyncio
import json
import os

from dotenv import load_dotenv
from web3 import Web3

from app.controller import check_for_new_aquanet_profiles
from app.db import get_block_number_query, get_client, index_aquanet_aquacreated_query

load_dotenv()

CONTRACT_ADDRESS = os.getenv("AQUANET_CONTRACT_ADDRESS")


async def index_aquanet():
    client = await get_client()
    with open("./abi.json", "r") as file:
        abi = json.load(file)
    w3 = Web3(Web3.WebsocketProvider(os.getenv("WS_PROVIDER")))
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)

    while True:
        try:
            print("Checking for new events...")

            # query to get the block number we should index from
            row = await client.fetchrow(get_block_number_query, 1, CONTRACT_ADDRESS)

            # create a filter for the AquaCreated event
            filter = contract.events.AquaCreated.create_filter(
                fromBlock=row["block_number"]
            )
            for event in filter.get_all_entries():
                # Only index if the block has 7 confirmations
                if event["blockNumber"] <= w3.eth.block_number - 7:
                    # Handle the event data
                    await client.execute(
                        index_aquanet_aquacreated_query,
                        event.args["aquaId"],
                        event.args["tokenAddress"],
                        event.args["tokenId"],
                    )

            await check_for_new_aquanet_profiles()

        except Exception as e:
            print(e)

        await asyncio.sleep(12)
