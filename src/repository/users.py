import logging
from datetime import datetime, timedelta

from sqlalchemy import or_
from sqlalchemy.future import select as fut_select
from sqlalchemy import select
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import User
from src.schemas.user import UserSchema, UserUpdateSchema

logging.basicConfig(filename="logfilename.log", level=logging.INFO)

async def get_users(limit: int, offset: int, db:AsyncSession):
    query = select(User).limit(limit).offset(offset)
    users = await db.execute(query)
    return users.scalars().all()

async def get_user(user_id: int, db:AsyncSession):
    query = select(User).filter_by(id=user_id)
    user = await db.execute(query)
    return user.scalar_one_or_none()


async def create_user(body: UserSchema, db:AsyncSession):
    user = User(**body.model_dump())
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def update_user(user_id: int,
                      body: UserUpdateSchema, 
                      db:AsyncSession):
    query = select(User).filter_by(id=user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if user:
        user.first_name = body.first_name
        user.last_name = body.last_name
        user.email = body.email
        user.phone = body.phone
        user.birthday = body.birthday
        user.additional_data = body.additional_data
        await db.commit()
        await db.refresh(user)
        return user


async def delete_user(user_id: int, db:AsyncSession):
    query = select(User).filter_by(id=user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if user:
        await db.delete(user)
        await db.commit()
    return user



async def search_users(query: str, db: AsyncSession):
    logging.info('Searching users')
    stmt = select(User).where(
        or_(
            User.first_name.ilike(f'%{query}%'),
            User.last_name.ilike(f'%{query}%'),
            User.email.ilike(f'%{query}%')
        )
    )
    result = await db.execute(stmt)
    result = result.scalars().all()
    return result


async def get_users_with_birthday_in_period(count_of_days: int, limit: int, offset: int, db: AsyncSession):
    today = datetime.today().date()
    end_date = today + timedelta(days=count_of_days)
    today_str = today.strftime("%m-%d")
    end_date_str = end_date.strftime("%m-%d")
    if today.month <= end_date.month:
        query = select(User).where(
            func.to_char(User.birthday, "MM-DD").between(today_str, end_date_str)
        ).limit(limit).offset(offset)
    else:
        query = select(User).where(
            or_(
                func.to_char(User.birthday, "MM-DD") >= today_str,
                func.to_char(User.birthday, "MM-DD") <= end_date_str
            )
        ).limit(limit).offset(offset)
    result = await db.execute(query)
    users = result.scalars().all()
    return users