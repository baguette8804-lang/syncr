from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from passlib.context import CryptContext
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# database setup
engine = create_engine("sqlite:///syncr.db")
Base = declarative_base()
Session = sessionmaker(bind=engine)

# user table
class UserTable(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)

# create the table if it doesn't exist
Base.metadata.create_all(engine)

app = FastAPI()
pwd = CryptContext(schemes=["bcrypt"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class User(BaseModel):
    name: str
    email: str
    password: str

class Login(BaseModel):
    email: str
    password: str

@app.get("/")
def home():
    return {"message": "Syncr is alive! 🔥"}

@app.post("/api/register")
def register(user: User):
    db = Session()
    existing = db.query(UserTable).filter_by(email=user.email).first()
    if existing:
        db.close()
        raise HTTPException(status_code=400, detail="Email already taken 😭")
    new_user = UserTable(
        name=user.name,
        email=user.email,
        password=pwd.hash(user.password)
    )
    db.add(new_user)
    db.commit()
    db.close()
    return {"message": f"Welcome to Syncr {user.name}! 🔥"}

@app.post("/api/login")
def login(data: Login):
    db = Session()
    user = db.query(UserTable).filter_by(email=data.email).first()
    db.close()
    if not user:
        raise HTTPException(status_code=400, detail="User not found 😭")
    if not pwd.verify(data.password, user.password):
        raise HTTPException(status_code=400, detail="Wrong password 💀")
    return {"message": f"Welcome back {user.name}! 🫡"}

@app.get("/api/matches")
def get_matches():
    return {
        "matches": [
            {"name": "Alex", "compatibility": "92%", "reason": "You both love music and coding"},
            {"name": "Jordan", "compatibility": "87%", "reason": "Same goals and communication style"},
            {"name": "Sam", "compatibility": "81%", "reason": "Shared interests in fitness and travel"},
        ]
    }

@app.get("/api/users")
def get_users():
    db = Session()
    users = db.query(UserTable).all()
    db.close()
    return {"users": [{"id": u.id, "name": u.name, "email": u.email} for u in users]}

