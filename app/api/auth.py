"""
Модуль аутентификации.
Содержит ручки для регистрации пользователя и получения токена доступа.
Реализует JWT-аутентификацию и проверку учетных данных пользователя.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.dependencies import get_user_service
from app.core.security import create_access_token
from app.schemas.token import Token, TokenData
from app.schemas.user import UserCreate, UserRead
from app.services.auth import UserService

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/register', response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(
        user_data: UserCreate,
        service: UserService = Depends(get_user_service)
):
    """
    Регистрация нового пользователя.

    Параметры:
    - username: логин пользователя
    - email: email пользователя
    - password: пароль пользователя

    Возвращает:
    - Данные созданного пользователя
    """
    try:
        return await service.create_user(user_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e


@router.post('/token', response_model=Token)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        service: UserService = Depends(get_user_service)
):
    """
    Аутентификация пользователя и получение JWT токена.

    Параметры:
    - username: логин пользователя
    - password: пароль пользователя

    Возвращает:
    - access_token: JWT токен для авторизации
    """
    user = await service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Неверное имя пользователя или пароль',
        )

    token_data = TokenData(user_id=str(user.id))
    access_token = create_access_token(token_data=token_data)

    return {'access_token': access_token}
