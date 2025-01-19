from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.hash import bcrypt
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from core.database import get_async_session
from core.auth.schemas import User, Token, UserCreate
from core.models import User as t_User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.config import jwt_secret, jwt_algorithm

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/sign-in/')


def check_auth(token: str = Depends(oauth2_scheme)) -> User:
    return AuthService.verify_token(token)


class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.verify(plain_password, hashed_password)

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hash(password)

    @staticmethod
    def verify_token(token: str) -> User:
        exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )
        try:
            payload = jwt.decode(
                token,
                jwt_secret,
                algorithms=[jwt_algorithm],
            )
        except JWTError:
            raise exception from None

        user_data = payload.get('user')

        try:
            user = User.parse_obj(user_data)
        except ValidationError:
            raise exception from None

        return user

    @staticmethod
    def create_token(user: t_User) -> Token:
        user_data = User.from_orm(user)
        now = datetime.utcnow()
        payload = {
            'iat': now,
            'nbf': now,
            'exp': now + timedelta(seconds=36000),
            'sub': str(user_data.id),
            'user': user_data.dict(),
        }
        token = jwt.encode(
            payload,
            jwt_secret,
            algorithm=jwt_algorithm,
        )
        return Token(access_token=token)

    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        self.session = session

    async def mail_verification(self, mail: str) -> bool:
        find_mail = await self.session.execute(select(t_User).where(t_User.mail == mail))
        find_mail = find_mail.scalar()
        if find_mail:
            return False
        else:
            return True

    async def register_new_user(self, user_data: UserCreate) -> Token:
        user = t_User(
            login=user_data.login,
            hashed_password=self.hash_password(user_data.password),
            mail=user_data.mail
        )

        try:
            self.session.add(user)
            await self.session.commit()
        except IntegrityError:
            raise HTTPException(status_code=500, detail="Taкой логин уже существует!")

        return self.create_token(user)

    async def authenticate_user(
        self,
        username: str,
        password: str,
    ) -> Token:
        exception = HTTPException(
            status_code=500,
            detail='Неправильный логин или пароль',
            headers={'WWW-Authenticate': 'Bearer'},
        )

        user = await self.session.execute(select(t_User).where(t_User.login == username))
        user = user.scalar()

        if not user:
            raise exception
        if not self.verify_password(password, user.hashed_password):
            raise exception

        return self.create_token(user)
