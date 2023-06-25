import asyncio
import os

import asyncpg
from dotenv import load_dotenv

from app.ai import create_post_from_tone
from app.util import next_post_in_x_hours

load_dotenv()


async def get_client():
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"))
    return conn


async def create_post(personality_id: int):
    client = await get_client()
    async with client.transaction():
        await client.execute(lock_schedule_query, personality_id)
        tone = await client.fetchrow(get_tone_query, personality_id)
        post = await create_post_from_tone(tone["tone"])
        await client.execute(create_post_query, personality_id, post)
        frequency = (await client.fetchrow(get_frequency_query, personality_id))[
            "frequency"
        ]
        x = await next_post_in_x_hours(frequency)
        await client.execute(update_personality_schedule_query, personality_id, x)
        print(f"Created post for personality {personality_id}, next post in {x} hours")


async def schedule_posts():
    while True:
        client = await get_client()
        try:
            # pick up any new personalities
            rows = await client.fetch(get_unscheduled_personalities_query)
            # pick up any personalities that are ready to post
            rows += await client.fetch(get_personalities_ready_for_posting)
            for row in rows:
                print(f"Creating post for personality {row['id']}")
                await create_post(row["id"])

        except Exception as e:
            print("Error in schedule_posts:", e)

        await asyncio.sleep(18)


get_metadata_query = """
select *
from nfts.metadata
where chain_id = $1
    and contract_address = $2
    and token_id = $3
"""

get_metadata_by_id_query = """
select *
from nfts.metadata
where id = $1
"""

get_personality_query = """
select *
from nfts.personalities
where id = $1
"""

create_personality_query = """
insert into nfts.personalities (id, username, bio, frequency, tone)
values ($1, $2, $3, $4, $5)
returning id, username, bio, frequency, tone
"""

get_unscheduled_personalities_query = """
select nfts.personalities.id
from nfts.personalities
left join nfts.personalities_schedule
    on nfts.personalities.id = nfts.personalities_schedule.id
where nfts.personalities_schedule.id is null
"""

get_personalities_ready_for_posting = """
select id
from nfts.personalities_schedule
where next_post_at < now()
    and locked is false
limit 10
"""

get_tone_query = """
select tone
from nfts.personalities
where id = $1
"""

create_post_query = """
insert into nfts.posts (author_id, content)
values ($1, $2)
returning id
"""

update_personality_schedule_query = """
insert into nfts.personalities_schedule (id, last_post_at, next_post_at, locked)
values ($1, now(), now() + $2 * interval '1 hour', false)
on conflict (id)
do update
set last_post_at = now(),
    next_post_at = now() + $2 * interval '1 hour',
    locked = false
"""

get_frequency_query = """
select frequency
from nfts.personalities
where id = $1
"""

lock_schedule_query = """
update nfts.personalities_schedule
set locked = true
where id = $1
"""

get_all_posts_query = """
select
    posts.id,
    posts.author_id,
    posts.content,
    posts.created_at,
    personalities.username as author_username
from nfts.posts
inner join nfts.personalities
    on posts.author_id = personalities.id
order by created_at desc
"""

get_posts_by_nft_query = """
select
    posts.id,
    posts.author_id,
    posts.content,
    posts.created_at,
    personalities.username as author_username
from nfts.posts
inner join nfts.personalities
    on posts.author_id = personalities.id
inner join nfts.metadata
    on personalities.id = nfts.metadata.id
where nfts.metadata.contract_address ilike $1
    and nfts.metadata.token_id = $2
order by created_at desc
"""

get_posts_by_personality_query = """
select *
from nfts.posts
where author_id = $1
order by created_at desc
"""

get_posts_since_query = """
select *
from nfts.posts
where id > $1
order by created_at desc
"""

get_posts_by_personality_since_query = """
select *
from nfts.posts
where author_id = $1
    and id > $2
order by created_at desc
"""

get_block_number_query = """
select block_number
from eth.block_height
where chain_id = $1
    and contract_address ilike $2
"""

update_block_number_query = """
update eth.block_height
set block_number = $1
where chain_id = $2
    and contract_address ilike $3
"""

index_aquanet_aquacreated_query = """
insert into eth.events_aquanet_aquacreated
    (aqua_id, contract_address, token_id)
values ($1, $2, $3)
on conflict (aqua_id)
    do nothing
"""

get_new_aquanet_profiles_query = """
select metadata.id
from nfts.metadata
inner join eth.events_aquanet_aquacreated
    on eth.events_aquanet_aquacreated.contract_address = metadata.contract_address
    and eth.events_aquanet_aquacreated.token_id = metadata.token_id
where metadata.id not in (select id from nfts.personalities)
"""
