import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRoute

logger = logging.getLogger(__name__)


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
        logger.info("Add user %s", user)
        id = self.max_id
        self.db[id] = user
        self.max_id += 1
        return id

    def remove(self, id: int) -> None:
        logger.info("remove user %s", id)
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


@app.get("/user/{id}", responses={404: {"model": None}})
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
                        "operationId": "delete_user",
                        "parameters": {"id": "$response.body#/id"},
                    },
                    "getUserById": {
                        "operationId": "get_user",
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


@app.delete("/user/delete/{id}", responses={404: {"model": None}})
def delete_user(id: int) -> None:
    try:
        user_db.remove(id)
    except KeyError:
        raise HTTPException(status_code=404, detail="User not found")


def _use_route_names_as_operation_ids(app: FastAPI) -> None:
    """
    Simplify operation IDs so that generated API clients have simpler function
    names.

    Should be called only after all routes have been added.
    """
    for route in app.routes:
        if isinstance(route, APIRoute):
            route.operation_id = route.name


_use_route_names_as_operation_ids(app)
