Frontend

- authenticate user w rainbowkit

- once authenticated, create tba
    - prompt for tx to create tba
    - figure out how to find a tba address by nft contract address and token id
- once a tba is created, mint a sbt
    - user must pay gas to mint the sbt
- create the personality using backend api

right now we have api endpoints to create a personality, but really what should be happening is we should just listen for SBTs to be minted and once they are minted, create the personality

the tokenURI for each SBT should be the api url to get all posts for a specific SBT id
