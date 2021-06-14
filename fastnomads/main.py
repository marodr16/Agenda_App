from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Boolean, Column, Float, String, Integer
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from typing import Optional, List

app = FastAPI()

# sqlAlchemy database engine
SQLALCHEMY_DATABASE_URL = 'sqlite+pysqlite:///./db.sqlite3:'
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# creates db session


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class DBPlace(Base):
    __tablename__ = 'places'

    # table columns
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    description = Column(String, nullable=True)
    coffee = Column(Boolean)
    wifi = Column(Boolean)
    food = Column(Boolean)
    lat = Column(Float)
    lng = Column(Float)


# object used to fetch and insert rows into database
Base.metadata.create_all(bind=engine)


class Place(BaseModel):
    # a pydantic base model to store fields related to a place
    name: str
    description: Optional[str] = None
    coffee: bool
    wifi: bool
    food: bool
    lat: float
    lng: float

    class Config:
        orm_mode = True

# methods to interact with the database


def get_place(db: Session, place_id: int):
    # returns a specific place
    return db.query(DBPlace).where(DBPlace.id == place_id).first()


def get_places(db: Session):
    # returns all places
    return db.query(DBPlace).all()


def create_place(db: Session, place: Place):
    # creates a place and stores in the db
    db_place = DBPlace(**place.dict())
    db.add(db_place)
    db.commit()
    db.refresh(db_place)

    return db_place

# routes for interacting with the api


@app.post('/places/', response_model=Place)
def create_places_view(place: Place, db: Session = Depends(get_db)):
    db_place = create_place(db, place)
    return db_place


@app.get('/places/', response_model=List[Place])
def get_places_view(db: Session = Depends(get_db)):
    return get_places(db)


@app.get('/place/{place_id}')
def get_place_view(place_id: int, db: Session = Depends(get_db)):
    return get_place(db, place_id)


@app.get('/')
async def root():
    return {'message': 'Molto Bene!'}

# start : uvicorn main:app --reload
# browser interaction : http://127.0.0.1:8000/docs#/default/create_place_view_places__post
