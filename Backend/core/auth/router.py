from fastapi import APIRouter, Depends

from fastapi.security import OAuth2PasswordRequestForm

from core.auth.schemas import UserCreate, User, Token
from core.auth.service import AuthService


router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


@router.post('/sign-in', response_model=Token, description='Аутентификация пользователя')
async def sign_in(
    auth_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(),
):
    return await auth_service.authenticate_user(auth_data.username, auth_data.password)


@router.post('/sign-up', response_model=Token, description='Регистрация пользователя')
async def sign_up(
    user_data: UserCreate,
    auth_service: AuthService = Depends(),
):
    return await auth_service.register_new_user(user_data)


@router.post('/mail-verification', response_model=bool, description='Проверка почты')
async def mail_verification(
    mail: str,
    auth_service: AuthService = Depends(),
):
    return await auth_service.mail_verification(mail)
