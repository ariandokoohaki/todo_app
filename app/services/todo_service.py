from typing import List
from sqlalchemy.orm import Session
from app.models.todo import Todo

async def create_todo(db: Session, title: str, description: str, owner_id: int) -> Todo:
    db_todo = Todo(title=title, description=description, owner_id=owner_id)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

async def get_todos_by_owner(db: Session, owner_id: int) -> List[Todo]:
    return db.query(Todo).filter(Todo.owner_id == owner_id).all()

async def get_todo_by_id(db: Session, todo_id: int) -> Todo | None:
    return db.query(Todo).filter(Todo.id == todo_id).first()

async def delete_todo(db: Session, todo: Todo):
    db.delete(todo)
    db.commit()

async def update_todo(db: Session, todo: Todo, title: str | None, description: str | None) -> Todo:
    if title is not None:
        todo.title = title
    if description is not None:
        todo.description = description
    db.commit()
    db.refresh(todo)
    return todo
