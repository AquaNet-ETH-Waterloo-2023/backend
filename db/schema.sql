-- drop schema nfts cascade;
create schema if not exists nfts;

-- drop table nfts.metadata;
create table if not exists nfts.metadata (
  id serial primary key,
  chain_id int not null,
  contract_address text not null,
  token_id int not null,
  metadata jsonb not null,
  constraint unique_nft_metadata unique (chain_id, contract_address, token_id)
);

-- drop type posting_frequency;
do $$
begin
  if not exists (
    select
      1
    from
      pg_type
    where
      typname = 'posting_frequency') then
  create type posting_frequency as enum (
    'frequent',
    'normal',
    'uncommon',
    'rare'
);
end if;
end
$$;

-- drop table nfts.personalities;
create table if not exists nfts.personalities (
  id serial primary key unique not null references nfts.metadata (id),
  username text not null,
  bio text not null,
  frequency posting_frequency not null,
  tone text not null,
  created_at timestamp not null default now()
);

-- drop table nfts.personalities_schedule;
create table if not exists nfts.personalities_schedule (
  id serial primary key unique not null references nfts.personalities (id),
  last_post_at timestamp not null,
  next_post_at timestamp not null,
  locked boolean not null default false
);

-- drop table nfts.posts;
create table if not exists nfts.posts (
  id serial primary key,
  author_id int not null references nfts.personalities (id),
  content text not null,
  created_at timestamp not null default now()
);

-- alter table nfts.metadata
--     drop column if exists profile_image;
alter table nfts.metadata
  add column if not exists profile_image text;

-- drop table nfts.tbas;
create table if not exists nfts.tbas (
  id serial primary key unique not null references nfts.metadata (id),
  address text not null
);

-- drop schema eth cascade;
create schema if not exists eth;

-- drop table eth.block_height;
create table if not exists eth.block_height (
  chain_id int not null,
  contract_address text not null,
  block_number int not null
);

-- drop table eth.events_AquaNet_AquaCreated;
create table if not exists eth.events_aquanet_aquacreated (
  aqua_id int unique not null,
  contract_address text not null,
  token_id int not null
);
