import databases
import sqlalchemy
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List

DATABASE_URL = "sqlite:///my_database.db"

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(128)),
    sqlalchemy.Column("last_name", sqlalchemy.String(128)),
    sqlalchemy.Column("email", sqlalchemy.String(128)),
    sqlalchemy.Column("passwd", sqlalchemy.String(128)),
    sqlalchemy.Column("salt", sqlalchemy.String(128)),
)

zakazy = sqlalchemy.Table(
    "zakazy",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("user_id", sqlalchemy.Integer),
    sqlalchemy.Column("tovar_id", sqlalchemy.Integer),
    sqlalchemy.Column("date", sqlalchemy.String(128)),
    sqlalchemy.Column("status", sqlalchemy.String(128)),
)

tovary = sqlalchemy.Table(
    "tovary",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(128)),
    sqlalchemy.Column("description", sqlalchemy.String(255)),
    sqlalchemy.Column("price", sqlalchemy.String(128)),
)

engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
    )
metadata.create_all(engine)

app = FastAPI()

class UserIn(BaseModel):
    name: str = Field(max_length=128)
    last_name: str = Field(max_length=128)
    email: str = Field(max_length=128)
    passwd: str = Field(max_length=128)

class User(BaseModel):
    id: int
    name: str = Field(max_length=32)
    last_name: str = Field(max_length=128)
    email: str = Field(max_length=128)
    passwd: str = Field(max_length=128)
    salt: str = Field(max_length=128)

class ZakazyIn(BaseModel):
    user_id: int
    tovar_id: int
    date: str = Field(max_length=128)
    status: str = Field(max_length=128)

class Zakazy(BaseModel):
    id: int
    user_id: int
    tovar_id: int
    date: str = Field(max_length=128)
    status: str = Field(max_length=128)

class TovaryIn(BaseModel):
    name: str = Field(max_length=128)
    description: str = Field(max_length=255)
    price: str = Field(max_length=128)

class Tovary(BaseModel):
    id: int
    name: str = Field(max_length=128)
    description: str = Field(max_length=255)
    price: str = Field(max_length=128)

@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.post("/users/", response_model=User)
async def users_post(user: UserIn):
    salt = str(12345676890)
    passw = str(user.passwd)
    key =str(hash(passw+salt))
    query = users.insert().values(name=user.name, last_name=user.last_name, email=user.email, passwd=key, salt=salt)
    last_record_id = await database.execute(query)
    return {"name": user.name, "last_name": user.last_name, "email": user.email, "passwd": key, "salt": salt, "id": last_record_id}

@app.post("/tovary/", response_model=Tovary)
async def tovary_post(tovar: TovaryIn):
    query = tovary.insert().values(**tovar.dict())
    last_record_id = await database.execute(query)
    return {**tovar.dict(), "id": last_record_id}

@app.post("/zakazy/", response_model=Zakazy)
async def zakazy_post(zakaz: ZakazyIn):
    query = zakazy.insert().values(**zakaz.dict())
    last_record_id = await database.execute(query)
    return {**zakaz.dict(), "id": last_record_id}

@app.get("/users/", response_model=List[User])
async def users_get():
    query = users.select()
    return await database.fetch_all(query)

@app.get("/tovary/", response_model=List[Tovary])
async def tovary_get():
    query = tovary.select()
    return await database.fetch_all(query)

@app.get("/zakazy/", response_model=List[Zakazy])
async def zakazy_get():
    query = zakazy.select()
    return await database.fetch_all(query)

@app.get("/users/{user_id}", response_model=User)
async def users_get_id(user_id: int):
    query = users.select().where(users.c.id == user_id)
    return await database.fetch_one(query)

@app.get("/tovary/{tovar_id}", response_model=Tovary)
async def tovary_get_id(tovar_id: int):
    query = tovary.select().where(tovary.c.id == tovar_id)
    return await database.fetch_one(query)

@app.get("/zakazy/{zakaz_id}", response_model=Zakazy)
async def zakazy_get_id(zakaz_id: int):
    query = zakazy.select().where(zakazy.c.id == zakaz_id)
    return await database.fetch_one(query)

@app.put("/users/{user_id}", response_model=User)
async def users_put(user_id: int, new_user: UserIn):
    query = users.update().where(users.c.id == user_id).values(**new_user.dict())
    await database.execute(query)
    return {**new_user.dict(), "id": user_id}

@app.put("/tovary/{tovar_id}", response_model=Tovary)
async def tovary_put(tovar_id: int, new_tovar: TovaryIn):
    query = tovary.update().where(tovary.c.id == tovar_id).values(**new_tovar.dict())
    await database.execute(query)
    return {**new_tovar.dict(), "id": tovar_id}

@app.put("/zakazy/{zakaz_id}", response_model=Zakazy)
async def zakazy_put(zakaz_id: int, new_zakaz: ZakazyIn):
    query = zakazy.update().where(zakazy.c.id == zakaz_id).values(**new_zakaz.dict())
    await database.execute(query)
    return {**new_zakaz.dict(), "id": zakaz_id}

@app.delete("/users/{user_id}")
async def users_delete(user_id: int):
    query = users.delete().where(users.c.id == user_id)
    await database.execute(query)
    return {"message": 'User deleted.'}

@app.delete("/tovary/{tovar_id}")
async def tovary_delete(tovar_id: int):
    query = tovary.delete().where(tovary.c.id == tovar_id)
    await database.execute(query)
    return {"message": 'Tovar deleted.'}

@app.delete("/zakazy/{zakaz_id}")
async def zakazy_delete(zakaz_id: int):
    query = zakazy.delete().where(zakazy.c.id == zakaz_id)
    await database.execute(query)
    return {"message": 'Zakaz deleted.'}
