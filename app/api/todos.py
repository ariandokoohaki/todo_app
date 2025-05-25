from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.dependencies import get_db, get_current_user
from app.api.schemas import TodoCreate, TodoRead, TodoUpdate
from app.models.user import User  # Your SQLAlchemy User model

# --- Import todo-related services from your todo_service.py ---
from app.services.todo_service import (
    create_todo as create_todo_service,
    get_todos_by_owner,
    get_todo_by_id,  # Using your existing service function
    delete_todo as delete_todo_service,
    update_todo as update_todo_service,
)

# --- End of service imports ---

router = APIRouter()


@router.post(
    "/",
    response_model=TodoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create New Todo",
)
async def create_new_todo_api(
    todo_data: TodoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_todo = await create_todo_service(
        db,
        title=todo_data.title,
        description=todo_data.description,
        owner_id=current_user.id,
    )
    return new_todo


@router.get("/", response_model=List[TodoRead], summary="Get Current User's Todos")
async def read_own_todos_api(  # Renamed
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
):
    todos = await get_todos_by_owner(
        db, owner_id=current_user.id
    )  # Assuming your service handles skip/limit or you add it here
    # If your service doesn't handle skip/limit, you'd do:
    # todos_query = db.query(Todo).filter(Todo.owner_id == current_user.id)
    # todos = todos_query.offset(skip).limit(limit).all()
    return todos


@router.get("/{todo_id}", response_model=TodoRead, summary="Get Specific Todo")
async def read_todo_by_id_api(  # Renamed
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_todo = await get_todo_by_id(
        db, todo_id=todo_id
    )  # Fetch by ID using your service

    # Perform ownership check in the API route
    if db_todo is None or db_todo.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found or not owned by user",
        )
    return db_todo


@router.patch("/{todo_id}", response_model=TodoRead, summary="Update Specific Todo")
async def update_existing_todo_api(  # Renamed
    todo_id: int,
    todo_update_data: TodoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_todo = await get_todo_by_id(db, todo_id=todo_id)  # Fetch by ID

    # Perform ownership check
    if not db_todo or db_todo.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found or not owned by user",
        )

    update_data = todo_update_data.model_dump(exclude_unset=True)

    # Call your update_todo service. It expects the todo object and individual fields.
    updated_todo = await update_todo_service(
        db,
        todo=db_todo,  # Pass the fetched todo object
        title=update_data.get("title"),  # Get title if present, else None
        description=update_data.get(
            "description"
        ),  # Get description if present, else None
    )
    return updated_todo


@router.delete(
    "/{todo_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Specific Todo"
)
async def delete_existing_todo_api(  # Renamed
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_todo = await get_todo_by_id(db, todo_id=todo_id)  # Fetch by ID

    # Perform ownership check
    if not db_todo or db_todo.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found or not owned by user",
        )

    await delete_todo_service(db, db_todo=db_todo)  # Pass the fetched todo object
    return None
