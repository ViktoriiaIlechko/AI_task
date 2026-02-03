from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from openai import OpenAI
from dotenv import load_dotenv
import datetime

load_dotenv()

app = FastAPI()
client = OpenAI()

DATABASE_URL = "sqlite:///./chat.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True)
    created_at = Column(String)
    total_tokens = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)

    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    role = Column(String)
    content = Column(String)
    tokens = Column(Integer)
    cost = Column(Float)
    created_at = Column(String)

    session = relationship("ChatSession", back_populates="messages")


Base.metadata.create_all(engine)

class MessageInput(BaseModel):
    message: str

@app.post("/chat/start")
def start_chat():
    db = SessionLocal()
    try:
        session = ChatSession(
            created_at=str(datetime.datetime.utcnow())
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return {"session_id": session.id}
    finally:
        db.close()

@app.post("/chat/{session_id}/message")
def send_message(session_id: int, data: MessageInput):
    db = SessionLocal()
    try:
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        messages = [
            {"role": m.role, "content": m.content}
            for m in session.messages
        ]
        messages.append({"role": "user", "content": data.message})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        reply = response.choices[0].message.content
        tokens = response.usage.total_tokens

        COST_PER_1K = 0.00015
        cost = (tokens / 1000) * COST_PER_1K

        db.add_all([
            Message(
                session_id=session.id,
                role="user",
                content=data.message,
                tokens=0,
                cost=0,
                created_at=str(datetime.datetime.utcnow())
            ),
            Message(
                session_id=session.id,
                role="assistant",
                content=reply,
                tokens=tokens,
                cost=cost,
                created_at=str(datetime.datetime.utcnow())
            )
        ])

        session.total_tokens += tokens
        session.total_cost += cost

        db.commit()
        return {"response": reply}
    finally:
        db.close()

@app.get("/chat/{session_id}/history")
def get_history(session_id: int):
    db = SessionLocal()

    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "messages": [
            {
                "role": m.role,
                "content": m.content,
                "tokens": m.tokens,
                "cost": m.cost
            } for m in session.messages
        ],
        "total_tokens": session.total_tokens,
        "total_cost": session.total_cost
    }
