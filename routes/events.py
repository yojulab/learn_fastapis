import json
from typing import List
import psycopg2
from psycopg2.extras import DictCursor
from fastapi import APIRouter, Depends, HTTPException, status
from models.events import Event, EventUpdate
from database.connection import get_db_connection
from auth.authenticate import authenticate

event_router = APIRouter(
    tags=["Events"]
)

@event_router.get("/", response_model=List[Event])
def retrieve_all_events(conn=Depends(get_db_connection)) -> List[Event]:
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("SELECT * FROM event")
        events = cur.fetchall()
    return [Event(**row) for row in events]

@event_router.get("/{id}", response_model=Event)
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

@event_router.post("/new", response_model=Event)
def create_event(body: Event, user: str = Depends(authenticate), conn=Depends(get_db_connection)) -> Event:
    body.creator = user
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

@event_router.put("/{id}", response_model=Event)
def update_event(id: int, body: EventUpdate, user: str = Depends(authenticate), conn=Depends(get_db_connection)) -> Event:
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("SELECT * FROM event WHERE id = %s", (id,))
        event = cur.fetchone()
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        if event["creator"] != user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Operation not allowed"
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

@event_router.delete("/{id}")
def delete_event(id: int, user: str = Depends(authenticate), conn=Depends(get_db_connection)) -> dict:
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("SELECT * FROM event WHERE id = %s", (id,))
        event = cur.fetchone()
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        if event["creator"] != user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Operation not allowed"
            )
        
        cur.execute("DELETE FROM event WHERE id = %s", (id,))
        conn.commit()

    return {
        "message": "Event deleted successfully."
    }