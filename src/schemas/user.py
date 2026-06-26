from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    username: str
    email: str


class UserRead(UserBase):
    model_config = ConfigDict(
        from_attributes=True
    )
    id: int


class UserCreate(UserBase):
    password: str

class UserVerification(BaseModel):
    email: str
    code: str

