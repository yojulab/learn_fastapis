from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from models.events import Event, EventUpdate
from database.connection import engine
from auth.authenticate import authenticate

event_router = APIRouter(
    tags=["Events"]
)

def get_session():
    with Session(engine) as session:
        yield session

@event_router.get("/", response_model=List[Event])
def retrieve_all_events(session: Session = Depends(get_session)) -> List[Event]:
    events = session.exec(select(Event)).all()
    return events

@event_router.get("/{id}", response_model=Event)
def retrieve_event(id: int, session: Session = Depends(get_session)) -> Event:
    event = session.get(Event, id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event with supplied ID does not exist"
        )
    return event

@event_router.post("/new")
def create_event(body: Event, user: str = Depends(authenticate), session: Session = Depends(get_session)) -> dict:
    body.creator = user
    session.add(body)
    session.commit()
    session.refresh(body)
    return {
        "message": "Event created successfully"
    }

@event_router.put("/{id}", response_model=Event)
def update_event(id: int, body: EventUpdate, user: str = Depends(authenticate), session: Session = Depends(get_session)) -> Event:
    event = session.get(Event, id)
    if event.creator != user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Operation not allowed"
        )
    
    update_data = body.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(event, key, value)

    session.add(event)
    session.commit()
    session.refresh(event)
    return event

@event_router.delete("/{id}")
def delete_event(id: int, user: str = Depends(authenticate), session: Session = Depends(get_session)) -> dict:
    event = session.get(Event, id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    if event.creator != user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Operation not allowed"
        )
    session.delete(event)
    session.commit()

    return {
        "message": "Event deleted successfully."
    }