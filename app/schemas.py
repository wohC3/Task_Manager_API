from sqlmodel import SQLModel


class TaskCreate(SQLModel):
    title: str
    description: str
    completed: bool = False

class TaskUpdate(SQLModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None

class TaskRead(SQLModel):
    id: int
    title: str
    description: str | None
    completed: bool