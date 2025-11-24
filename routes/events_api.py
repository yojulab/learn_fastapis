from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import Session, select
from models.events import Event, EventUpdate
from database.connection import engine

router = APIRouter(
    tags=["Events"]
)

def get_session():
    with Session(engine) as session:
        yield session

@router.get("/", response_model=List[Event])
def retrieve_all_events(session: Session = Depends(get_session)) -> List[Event]:
    events = session.exec(select(Event)).all()
    return events

@router.get("/{id}", response_model=Event)
def retrieve_event(id: int, session: Session = Depends(get_session)) -> Event:
    event = session.get(Event, id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event with supplied ID does not exist"
        )
    return event

@router.post("/new")
def create_event(body: Event, session: Session = Depends(get_session)) -> dict:
    session.add(body)
    session.commit()
    session.refresh(body)
    return {
        "message": "Event created successfully",
        "datas": body
    }

@router.put("/{id}", response_model=Event)
def update_event(id: int, body: EventUpdate, session: Session = Depends(get_session)) -> Event:
    event = session.get(Event, id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    update_data = body.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(event, key, value)

    session.add(event)
    session.commit()
    session.refresh(event)
    return event

@router.delete("/{id}")
def delete_event(id: int, session: Session = Depends(get_session)) -> dict:
    event = session.get(Event, id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    session.delete(event)
    session.commit()

    return {
        "message": "Event deleted successfully."
    }