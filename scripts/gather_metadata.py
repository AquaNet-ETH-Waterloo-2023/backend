import argparse
import concurrent.futures
import os

import psycopg2
import requests
from dotenv import load_dotenv
from psycopg2.extras import Json

load_dotenv()

# API endpoint to get NFT metadata batch
API_ENDPOINT = "https://eth-mainnet.g.alchemy.com/nft/v2/{}/getNFTMetadataBatch"


def process_batch(tokens, conn, cursor, start_token, end_token):
    """
    Process a batch of tokens and save metadata to the PostgreSQL database.
    """

    print(f"Processing tokens {start_token + 1}-{end_token}")

    # Make a POST request to the API endpoint with tokens payload
    response = requests.post(
        API_ENDPOINT.format(API_KEY),
        headers={"content-type": "application/json"},
        json={"tokens": tokens},
    )

    # Save each token metadata to the PostgreSQL database
    for token in response.json():
        metadata = token.get("metadata", {}).get("attributes")
        if metadata:
            chain_id = 1  # Assuming mainnet with chain ID 1

            insert_query = """
                INSERT INTO nfts.metadata (chain_id, contract_address, token_id, metadata)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """
            cursor.execute(
                insert_query,
                (chain_id, ADDRESS, token["id"]["tokenId"], Json(metadata)),
            )
            conn.commit()


def main(address, api_key, database_url, amount):
    """
    Retrieve NFT metadata for tokens in batches and save them to a PostgreSQL database.
    """
    # Load environment variables
    global ADDRESS, API_KEY, DATABASE_URL
    ADDRESS = address or os.environ.get("ADDRESS")
    API_KEY = api_key or os.environ.get("API_KEY")
    DATABASE_URL = database_url or os.environ.get("DATABASE_URL")

    if not ADDRESS:
        raise ValueError("Contract address not provided")
    if not API_KEY:
        raise ValueError("API key not provided")
    if not DATABASE_URL:
        raise ValueError("Database URL not provided")

    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    # run the schema query in ../db/schema.sql
    with open("./db/schema.sql", "r") as f:
        cursor.execute(f.read())
        conn.commit()

    batch_size = 100
    total_batches = (amount + batch_size - 1) // batch_size

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []

        for batch_num in range(total_batches):
            start_token = batch_num * batch_size
            end_token = min((batch_num + 1) * batch_size, amount)

            tokens = [
                {
                    "tokenId": j,
                    "contractAddress": ADDRESS,
                    "tokenType": "ERC721",
                }
                for j in range(start_token, end_token)
            ]

            futures.append(
                executor.submit(
                    process_batch, tokens, conn, cursor, start_token, end_token
                )
            )

        # Wait for all futures (batches) to complete
        concurrent.futures.wait(futures)

    cursor.close()
    conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Retrieve NFT metadata and save to PostgreSQL database."
    )
    parser.add_argument("-a", "--address", help="The contract address of the NFTs")
    parser.add_argument(
        "-k", "--api-key", help="The API key for accessing the NFT metadata"
    )
    parser.add_argument(
        "-d", "--database-url", help="The URL of the PostgreSQL database"
    )
    parser.add_argument(
        "--amount",
        "-m",
        type=int,
        default=10000,
        help="The total number of tokens to process",
    )
    args = parser.parse_args()
    main(args.address, args.api_key, args.database_url, args.amount)
