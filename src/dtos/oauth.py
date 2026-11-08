from pydantic import BaseModel


class URLReturnDTO(BaseModel):
    url: str


class RedirectDataDTO(BaseModel):
    code: str
    state: str
