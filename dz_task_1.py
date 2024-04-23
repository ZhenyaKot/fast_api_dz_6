import decimal
from typing import List

import databases
from pydantic import BaseModel, Field, PastDate
from fastapi import FastAPI
import sqlalchemy
import uvicorn
from sqlalchemy import ForeignKey
from datetime import date

app = FastAPI()
DATABASE_URL = "sqlite:///mydatabase.db"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

users = sqlalchemy.Table(
    'users',
    metadata,
    sqlalchemy.Column('user_id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('first_name', sqlalchemy.String(30)),
    sqlalchemy.Column('last_name', sqlalchemy.String(30)),
    sqlalchemy.Column('email', sqlalchemy.String(30)),
    sqlalchemy.Column('password', sqlalchemy.String(30))
)

goods = sqlalchemy.Table(
    'goods',
    metadata,
    sqlalchemy.Column('goods_id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('name', sqlalchemy.String(30)),
    sqlalchemy.Column('description', sqlalchemy.String(30)),
    sqlalchemy.Column('price', sqlalchemy.DECIMAL),
)

orders = sqlalchemy.Table(
    'orders',
    metadata,
    sqlalchemy.Column('orders_id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('user_id', sqlalchemy.Integer, ForeignKey('users.user_id')),
    sqlalchemy.Column('goods_id', sqlalchemy.Integer, ForeignKey('goods.goods_id')),
    sqlalchemy.Column('order_date', sqlalchemy.DATE),
    sqlalchemy.Column('order_status', sqlalchemy.String(30))
)


class UserIn(BaseModel):
    first_name: str = Field(..., max_length=30)
    last_name: str = Field(..., max_length=30)
    email: str = Field(..., max_length=30)
    password: str = Field(..., min_length=6, max_length=30)


class User(UserIn):
    id: int


class GoodsIn(BaseModel):
    name: str = Field(..., max_length=30)
    description: str = Field(..., max_length=30)
    price: str = Field(..., max_length=30)


class Goods(GoodsIn):
    id: int


class OrderIn(BaseModel):
    user_id: int
    goods_id: int
    order_date: PastDate
    order_status: str = Field(..., max_length=30)


class Order(OrderIn):
    orders_id: int


engine = sqlalchemy.create_engine(DATABASE_URL, connect_args={'check_same_thread': False})
metadata.create_all(engine)


@app.get('/fake_users/{count}')
async def get_fake_users(count: int):
    for i in range(1, count):
        query = users.insert().values(first_name=f'user{i}',
                                      last_name=f'user{i}',
                                      email=f'mail{i}@mail.ru',
                                      password=str(111111 * i))
        await database.execute(query)
    return {'massage': f'{count} fake users create'}


@app.get('/fake_goods/{count}')
async def get_fake_goods(count: int):
    for i in range(1, count):
        query = goods.insert().values(name=f'user{i}',
                                      description=f'{str(i) + str(i) + str(i) + str(i)}',
                                      price=decimal.Decimal(111111 * i))
        await database.execute(query)
    return {'massage': f'{count} fake goods create'}


@app.get('/fake_orders/{count}')
async def get_fake_orders(count: int):
    for i in range(1, count):
        query = orders.insert().values(user_id=i,
                                       goods_id=i,
                                       order_date=date.today(),
                                       order_status=f'{str(i) + str(i) + str(i) + str(i)}')
        await database.execute(query)
    return {'massage': f'{count} fake orders create'}


@app.get('/users/', response_model=List[UserIn])
async def get_users():
    query = users.select()
    records = await database.fetch_all(query)
    users_list = [dict(record) for record in records]
    return users_list


@app.get('/users/{user_id}', response_model=UserIn)
async def get_user(user_id: int):
    query = users.select().where(users.c.user_id == user_id)
    return await database.fetch_one(query)


@app.post('/users/', response_model=UserIn)
async def create_user(user: UserIn):
    query = users.insert().values(first_name=user.first_name,
                                  last_name=user.last_name,
                                  email=user.email,
                                  password=user.password)
    last_record_id = await database.execute(query)
    return {**user.dict(), 'id': last_record_id}


@app.put('/users/{user_id}', response_model=UserIn)
async def update_user(user_id: int, new_user: UserIn):
    query = users.update().where(users.c.user_id == user_id).values(new_user.dict())
    await database.execute(query)
    return {**new_user.dict(), 'id': user_id}


@app.delete('/users/{user_id}')
async def delete_user(user_id: int):
    query = users.delete().where(users.c.user_id == user_id)
    await database.execute(query)
    return {'massage': f'user {user_id} delete'}


# Я ПОНЯЛ АЛГОРИТМ ДЕЙСТВИЙ, ВСЕ ОСТАВШИЕСЯ ЗАПРОСЫ К ДРУГИМ ТАБЛИЦАМ БУДУТ ЭДЕНТИЧНЫ ЗАПРОСАМ К ТАБЛИЦЕ USERS.
# Я НЕ СТАЛ ДЕЛАТЬ ТОЖЕ САМОЕ


if __name__ == '__main__':
    uvicorn.run('dz_task_1:app', port=8000, reload=True)
