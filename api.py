from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.openapi.utils import get_openapi


class User(BaseModel):
    name: str
    email: str


class UserResponse(BaseModel):
    id: int


class UserDb:
    def __init__(self):
        self.max_id = 0
        self.db = {}

    def add(self, user):
        id = self.max_id
        self.db[id] = user
        self.max_id += 1
        return id

    def remove(self, id: int) -> None:
        del self.db[id]

    def get_users(self) -> list[User]:
        return [user for user in self.db.values()]

    def get_user(self, id: int) -> User:
        return self.db[id]


user_db = UserDb()

app = FastAPI()


@app.get("/user")
def get_users() -> list[User]:
    return user_db.get_users()


@app.get("/user/{id}", operation_id="getUser")
def get_user(id: int) -> User:
    try:
        return user_db.get_user(id)
    except KeyError:
        raise HTTPException(status_code=404, detail="User not found")


@app.post(
    "/user/create",
    openapi_extra={
        "responses": {
            "200": {
                "links": {
                    "deleteUserById": {
                        "operationId": "deleteUser",
                        "parameters": {"id": "$response.body#/id"},
                    },
                    "getUserById": {
                        "operationId": "getUser",
                        "parameters": {"id": "$response.body#/id"},
                    },
                }
            }
        }
    },
)
def create_user(user: User) -> UserResponse:
    id = user_db.add(user)
    return UserResponse(id=id)


@app.delete("/user/delete/{id}", operation_id="deleteUser")
def delete_user(id: int):
    try:
        user_db.remove(id)
    except KeyError:
        raise HTTPException(status_code=404, detail="User not found")
