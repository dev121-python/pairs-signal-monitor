from dotenv import load_dotenv
import os

load_dotenv()

from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine(os.environ["DATABASE_URL"])
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)


class SignalHistory(Base):
    __tablename__ = "signal_history"

    id = Column(Integer, primary_key=True)
    date = Column(String)
    ticker_a = Column(String)
    ticker_b = Column(String)
    hedge_ratio = Column(Float)
    spread = Column(Float)
    zscore = Column(Float)
    position = Column(String)


Base.metadata.create_all(engine)


def save_signal(signal: dict) -> None:
    session = SessionLocal()
    try:
        existing = session.query(SignalHistory).filter_by(date=signal["date"]).first()
        if existing:
            existing.hedge_ratio = signal["hedge_ratio"]
            existing.spread = signal["spread"]
            existing.zscore = signal["zscore"]
            existing.position = signal["position"]
        else:
            row = SignalHistory(**signal)
            session.add(row)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_signal_history(limit: int = 30) -> list[dict]:
    session = SessionLocal()
    try:
        rows = session.query(SignalHistory).order_by(SignalHistory.id.desc()).limit(limit).all()
        return [
            {c.name: getattr(row, c.name) for c in SignalHistory.__table__.columns}
            for row in rows
        ]
    finally:
        session.close()