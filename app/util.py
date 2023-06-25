import random
from enum import Enum


class Frequency(Enum):
    FREQUENT = "frequent"
    NORMAL = "normal"
    UNCOMMON = "uncommon"
    RARE = "rare"


class PostingFrequency(Enum):
    frequent = (4, 18)
    normal = (8, 24)
    uncommon = (24, 48)
    rare = (72, 144)

    def get_random_delay(self):
        min_delay, max_delay = self.value
        delay = random.randint(min_delay, max_delay)
        return delay


# Pick a random frequency based on the following distribution:
# 15% FREQUENT
# 60% NORMAL
# 20% UNCOMMON
# 5% RARE
def pick_random_frequency():
    choices = (
        [Frequency.FREQUENT] * 3
        + [Frequency.NORMAL] * 12
        + [Frequency.UNCOMMON] * 4
        + [Frequency.RARE] * 1
    )
    return random.choice(choices).value


# 0x1CB1A5e65610AEFF2551A50f76a87a7d3fB649C6
# 0x3Fe1a4c1481c8351E91B64D5c398b159dE07cbc5
# 0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D
# 0x57a204aa1042f6e66dd7730813f4024114d74f37
def get_character_type(contract_address):
    if contract_address == "0x3Fe1a4c1481c8351E91B64D5c398b159dE07cbc5":
        return "Duck"
    elif contract_address == "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D":
        return "Ape"
    elif contract_address == "0x57a204aa1042f6e66dd7730813f4024114d74f37":
        return "Gorilla"
    elif contract_address == "0x1CB1A5e65610AEFF2551A50f76a87a7d3fB649C6":
        return "Toad"
    else:
        return "Unknown"


async def next_post_in_x_hours(frequency: str):
    print(frequency)
    next_post_at = PostingFrequency[frequency].get_random_delay()
    return next_post_at
