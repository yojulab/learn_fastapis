import json
from typing import List
import psycopg2
from psycopg2.extras import DictCursor
from fastapi import APIRouter, Depends, HTTPException, status
from models.events import Event, EventUpdate
from database.connection import get_db_connection

router = APIRouter(
    tags=["Events"]
)

@router.get("/", response_model=List[Event])
def retrieve_all_events(conn=Depends(get_db_connection)) -> List[Event]:
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("SELECT * FROM event")
        events = cur.fetchall()
    return [Event(**row) for row in events]

@router.get("/{id}", response_model=Event)
def retrieve_event(id: int, conn=Depends(get_db_connection)) -> Event:
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("SELECT * FROM event WHERE id = %s", (id,))
        event = cur.fetchone()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event with supplied ID does not exist"
        )
    return Event(**event)

@router.post("/new", response_model=Event)
def create_event(body: Event, conn=Depends(get_db_connection)) -> Event:
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute(
            """
            INSERT INTO event (creator, title, image, description, tags, location)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING *
            """,
            (body.creator, body.title, body.image, body.description, json.dumps(body.tags), body.location)
        )
        new_event = cur.fetchone()
        conn.commit()
        
    return Event(**new_event)

@router.put("/{id}", response_model=Event)
def update_event(id: int, body: EventUpdate, conn=Depends(get_db_connection)) -> Event:
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("SELECT * FROM event WHERE id = %s", (id,))
        event = cur.fetchone()
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        update_data = body.dict(exclude_unset=True)
        set_clause = []
        params = []
        
        for key, value in update_data.items():
            set_clause.append(f"{key} = %s")
            if key == "tags":
                params.append(json.dumps(value))
            else:
                params.append(value)
        
        if not set_clause:
            return Event(**event) # No changes
            
        params.append(id)
        
        cur.execute(
            f"UPDATE event SET {', '.join(set_clause)} WHERE id = %s RETURNING *",
            tuple(params)
        )
        updated_event = cur.fetchone()
        conn.commit()

    return Event(**updated_event)

@router.delete("/{id}")
def delete_event(id: int, conn=Depends(get_db_connection)) -> dict:
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("SELECT id FROM event WHERE id = %s", (id,))
        event = cur.fetchone()
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        cur.execute("DELETE FROM event WHERE id = %s", (id,))
        conn.commit()

    return {
        "message": "Event deleted successfully."
    }