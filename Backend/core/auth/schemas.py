from pydantic import BaseModel, ConfigDict


class BaseUser(BaseModel):
    login: str


class UserCreate(BaseUser):
    mail: str
    password: str


class User(BaseUser):
    id: int
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'
