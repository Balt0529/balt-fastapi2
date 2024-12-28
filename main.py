from fastapi import FastAPI,Body
from fastapi.middleware.cors import CORSMiddleware
from database import read_users,read_posts,read_favorites,add_users,add_posts,delete_posts
from pydantic import BaseModel
from typing import Union
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Item(BaseModel):
    name:str
    price:float
    is_offer:Union[bool,None]=None

@app.get("/")
async def root():
    return {"message": "Hello World From Fast API!"}

@app.get("/items/{item_id}")
def read_item(item_id:int, q:Union[str,None]=None):
    return {"item_id":item_id,"q":q}

@app.put("/items/{item_id}")
def update_item(item_id:int,item:Item):
    return{"item_name":item.name,"item_id":item_id}

#users
@app.get("/users")
def get_users():
    return read_users

@app.post("/users")
def post_users(id:str=Body(...),email:str=Body(...),name:str=Body(...)):
    postusers=add_users(id,email,name)
    return {"id":postusers.id,"email":postusers.email,"name":postusers.name}

#posts
@app.get("/posts")
def get_posts():
    return read_posts

# @app.post("/posts")
# def post_posts(id:int=Body(...),user_id:str=Body(...),place_id:str=Body(...),content:str=Body(...),created_at:datetime=Body(...)):
#     postposts=add_posts(id,user_id,place_id,content,created_at)
#     return {"id":postposts.id,"user_id":postposts.user_id,"place_id":postposts.place_id,"content":postposts.content,"created_at":postposts.created_at}

# @app.delete("/posts/{id}")
# def delete_posts_endpoint(id:int):
#     return delete_posts(id)

#favorites
@app.get("/favorites")
def get_favorites():
    return read_favorites