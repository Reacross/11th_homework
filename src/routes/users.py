import logging
from typing import List, Union

from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_

from src.database.db import get_db
from src.repository import users as repositories_users
from src.schemas.user import UserSchema, UserUpdateSchema, UserResponse
from src.entity.models import User

router = APIRouter(
    prefix="/users",
    tags=["users"])

logging.basicConfig(filename="Routes.log", level=logging.INFO)

@router.get("/", response_model=List[UserResponse])
async def get_users(limit: int = Query(10, ge=10, le=500),
                        offset: int = Query(0, ge=0),
                        db: AsyncSession = Depends(get_db)):
    users = await repositories_users.get_users(limit, offset, db)
    return users

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int = Path(ge=1),
                   db: AsyncSession = Depends(get_db)):
    user = await repositories_users.get_user(user_id, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found")
    return user

@router.get("/users/{search}", response_model=List[UserResponse])
async def search_users(user_data: str,
                         db: AsyncSession = Depends(get_db)):
    users = await repositories_users.search_users(user_data, db)
    if users is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Users not found")
    return users

@router.get("/users/", response_model=List[UserResponse])
async def get_users_with_birthday_in_period(count_of_days: int = Query(1, ge=1, le=7), 
                                            limit: int = Query(10, ge=10, le=500),
                                            offset: int = Query(0, ge=0),
                                            db: AsyncSession = Depends(get_db)):
    users = await repositories_users.get_users_with_birthday_in_period(count_of_days, limit, offset, db)
    if users is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Users not found")
    return users
    
    

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(body: UserSchema,
                      db: AsyncSession = Depends(get_db)):
    user = await repositories_users.create_user(body, db)
    return user

@router.put("/{user_id}")
async def update_user(body: UserUpdateSchema,
                      user_id: int = Path(ge=1),
                      db: AsyncSession = Depends(get_db)):
    user = await repositories_users.update_user(user_id, body, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found")
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int = Path(ge=1),
                      db: AsyncSession = Depends(get_db)):
    user = await repositories_users.delete_user(user_id, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found")
    return user
