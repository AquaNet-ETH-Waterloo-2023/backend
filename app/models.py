from pydantic import BaseModel

class PersonalityGenerateRequest(BaseModel):
    chain_id: int
    contract_address: str
    token_id: int
