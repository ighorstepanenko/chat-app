"""
Модуль управления групповыми чатами.
Содержит эндпоинты для создания групп и управления их участниками.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_current_user, get_group_service
from app.schemas.group import GroupCreate, GroupList, GroupRead
from app.services.group import GroupService

router = APIRouter(prefix='/groups', tags=['groups'])


@router.post('/', response_model=GroupRead, status_code=status.HTTP_201_CREATED)
async def create_group(
        group_data: GroupCreate,
        current_user: int = Depends(get_current_user),
        service: GroupService = Depends(get_group_service)
):
    """
    Создание новой группы.

    Параметры:
    - name: название группы
    - creator_id: ID создателя группы

    Возвращает:
    - Созданную группу с ID и списком участников
    """
    if group_data.creator_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Нельзя создавать группу от имени другого пользователя'
        )

    return await service.create_group(group_data)


@router.get('/', response_model=GroupList)
async def get_user_groups(
        current_user: int = Depends(get_current_user),
        service: GroupService = Depends(get_group_service)
):
    """
    Получение списка групп пользователя.

    Возвращает:
    - Список групп, в которых участвует пользователь
    """
    return await service.get_user_groups(current_user)


@router.get('/{group_id}', response_model=GroupRead)
async def get_group(
        group_id: int,
        current_user: int = Depends(get_current_user),
        service: GroupService = Depends(get_group_service)
):
    """
    Получение информации о группе.

    Параметры:
    - group_id: ID группы

    Возвращает:
    - Информацию о группе
    """
    group = await service.get_group(group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Группа не найдена'
        )

    if current_user not in group.members:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Вы не являетесь участником этой группы'
        )

    return group


@router.get('/{group_id}/members', response_model=list[int])
async def get_group_members(
        group_id: int,
        current_user: int = Depends(get_current_user),
        service: GroupService = Depends(get_group_service)
):
    """
    Получение списка участников группы.

    Параметры:
    - group_id: ID группы

    Возвращает:
    - Список ID участников группы
    """
    group = await service.get_group(group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Группа не найдена'
        )

    if current_user not in group.members:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Вы не являетесь участником этой группы'
        )

    return await service.get_group_members(group_id)


@router.post('/{group_id}/members/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def add_group_member(
        group_id: int,
        user_id: int,
        current_user: int = Depends(get_current_user),
        service: GroupService = Depends(get_group_service)
):
    """
    Добавление участника в группу.

    Параметры:
    - group_id: ID группы
    - user_id: ID добавляемого пользователя
    """
    group = await service.get_group(group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Группа не найдена'
        )

    if current_user not in group.members:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Вы не являетесь участником этой группы'
        )

    if not await service.add_member(group_id, user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Пользователь уже в группе или группа не найдена'
        )


@router.delete('/{group_id}/members/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def remove_group_member(
        group_id: int,
        user_id: int,
        current_user: int = Depends(get_current_user),
        group_service: GroupService = Depends(get_group_service)
):
    """
    Удаление участника из группы.

    Параметры:
    - group_id: ID группы
    - user_id: ID удаляемого пользователя
    """
    group = await group_service.get_group(group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Группа не найдена'
        )

    if current_user not in group.members:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Вы не являетесь участником этой группы'
        )

    if user_id == group.creator_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Нельзя удалить создателя группы'
        )

    if not await group_service.remove_member(group_id, user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Пользователь не найден в группе'
        )
