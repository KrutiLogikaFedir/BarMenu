from typing import Annotated, Optional
from pydantic import BaseModel
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

app = FastAPI()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
VALID_USERNAME = "player"
VALID_PASSWORD = "bubabi"



class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float



db_items = {
    1: {"id": 1, "name": "Меч", "description": "Гострий залізний меч", "price": 150.0},
    2: {"id": 2, "name": "Щит", "description": "Дерев'яний щит", "price": 85.0},
    3: {"id": 3, "name": "Зілля здоров'я", "description": "Відновлює 50 HP", "price": 25.0},
}
item_id_counter = 4




@app.post("/token")
async def token_get(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    if form_data.username != VALID_USERNAME or form_data.password != VALID_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password"
        )
    return {"access_token": form_data.username, "token_type": "bearer"}


@app.get("/protected")
async def protected(token: str = Depends(oauth2_scheme)):
    return {"message": "This info is available only after user is authorized"}





@app.get("/items")
async def get_items(
        token: str = Depends(oauth2_scheme),
        search: Optional[str] = None
):

    items_list = list(db_items.values())

    if search:
        search_lower = search.lower()
        filtered_items = [
            item for item in items_list
            if search_lower in item["name"].lower() or
               (item["description"] and search_lower in item["description"].lower())
        ]
        return {"items": filtered_items}

    return {"items": items_list}



@app.post("/items", status_code=status.HTTP_201_CREATED)
async def create_item(
        item: ItemCreate,
        token: str = Depends(oauth2_scheme)
):
    global item_id_counter

    new_item = {
        "id": item_id_counter,
        "name": item.name,
        "description": item.description,
        "price": item.price
    }

    db_items[item_id_counter] = new_item
    item_id_counter += 1

    return {"message": "Елемент успішно додано", "item": new_item}



@app.delete("/items/{item_id}")
async def delete_item(
        item_id: int,
        token: str = Depends(oauth2_scheme)
):
    if item_id not in db_items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Елемент з ID {item_id} не знайдено в базі"
        )

    deleted_item = db_items.pop(item_id)
    return {"message": f"Елемент '{deleted_item['name']}' видалено", "deleted_item": deleted_item}


