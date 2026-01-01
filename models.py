from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import relationship, sessionmaker, DeclarativeBase
from dotenv import load_dotenv
from typing import Optional
from pydantic import BaseModel
import os

load_dotenv()

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

class Bracket(Base):
    __tablename__ = "bracket"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tournament_id = Column(Integer, ForeignKey("tournament.id"), nullable=False)
    name = Column(String(50), nullable=False)

    # Relationships
    tournament = relationship("Tournament", back_populates="brackets")
    bracket_players = relationship("BracketPlayer", back_populates="bracket")
    matchups = relationship("Matchup", back_populates="bracket")

    def __repr__(self):
        return f"<Bracket(id={self.id}, name='{self.name}')>"

class Matchup(Base):
    __tablename__ = "matchup"

    id = Column(Integer, primary_key=True, autoincrement=True)
    bracket_id = Column(Integer, ForeignKey("bracket.id"), nullable=False)
    player1_id = Column(Integer, ForeignKey("player.id"))
    player2_id = Column(Integer, ForeignKey("player.id"))
    player1_partner_id = Column(Integer, ForeignKey("player.id"))
    player2_partner_id = Column(Integer, ForeignKey("player.id"))
    winner_id = Column(Integer, ForeignKey("player.id"))
    round = Column(Integer, nullable=True)
    score = Column(String(50))
    status = Column(String(20), nullable=False)

    # Relationships
    bracket = relationship("Bracket", back_populates="matchups")
    player1 = relationship("Player", foreign_keys=[player1_id])
    player2 = relationship("Player", foreign_keys=[player2_id])
    player1_partner = relationship("Player", foreign_keys=[player1_partner_id])
    player2_partner = relationship("Player", foreign_keys=[player2_partner_id])
    winner = relationship("Player", foreign_keys=[winner_id])

    def __repr__(self):
        return f"<Matchup(id={self.id}, status='{self.status}')>"

class Player(Base):
    __tablename__ = "player"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(80), nullable=False)
    gender = Column(String(10), nullable=False)
    phone_number = Column(String(15), nullable=False)

    # Relationships
    matchups = relationship("Matchup", back_populates="player1", foreign_keys="Matchup.player1_id")
    tournament_players = relationship("TournamentPlayer", back_populates="player")
    bracket_players = relationship("BracketPlayer", back_populates="player")

    def __repr__(self):
        return f"<Player(id={self.id}, name='{self.name}')>"

class Tournament(Base):
    __tablename__ = "tournament"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    start_date = Column(String, nullable=True)  # Using String for simplicity; can be Date if needed
    end_date = Column(String, nullable=True)    # Using String for simplicity; can be Date if needed
    format = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)

    # Relationships
    brackets = relationship("Bracket", back_populates="tournament")
    tournament_players = relationship("TournamentPlayer", back_populates="tournament")

    def __repr__(self):
        return f"<Tournament(id={self.id}, name='{self.name}')>"

class TournamentPlayer(Base):
    __tablename__ = "tournament_player"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tournament_id = Column(Integer, ForeignKey("tournament.id"), nullable=False)
    player_id = Column(Integer, ForeignKey("player.id"), nullable=False)

    # Relationships
    tournament = relationship("Tournament", back_populates="tournament_players")
    player = relationship("Player", back_populates="tournament_players")

    def __repr__(self):
        return f"<TournamentPlayer(id={self.id}, tournament_id={self.tournament_id}, player_id={self.player_id})>"

class BracketPlayer(Base):
    __tablename__ = "bracket_player"

    id = Column(Integer, primary_key=True, autoincrement=True)
    bracket_id = Column(Integer, ForeignKey("bracket.id"), nullable=False)
    player_id = Column(Integer, ForeignKey("player.id"), nullable=False)

    # Relationships
    bracket = relationship("Bracket", back_populates="bracket_players")
    player = relationship("Player", back_populates="bracket_players")

    def __repr__(self):
        return f"<BracketPlayer(id={self.id}, bracket_id={self.bracket_id}, player_id={self.player_id})>"

# Pydantic models
class BracketType(BaseModel):
    id: Optional[int]
    tournament_id: int
    name: str

class MatchupType(BaseModel):
    id: Optional[int]
    bracket_id: int
    player1_id: Optional[int]
    player2_id: Optional[int]
    player1_partner_id: Optional[int]
    player2_partner_id: Optional[int]
    winner_id: Optional[int]
    score: Optional[str]
    status: str

class PlayerType(BaseModel):
    id: Optional[int]
    name: str
    gender: str
    phone_number: str

class TournamentType(BaseModel):
    id: Optional[int]
    name: str
    start_date: Optional[str]
    end_date: Optional[str]
    format: str
    status: str

class TournamentPlayerType(BaseModel):
    id: Optional[int]
    tournament_id: int
    player_id: int

class BracketPlayerType(BaseModel):
    id: Optional[int]
    bracket_id: int
    player_id: int


# Create all tables
Base.metadata.create_all(bind=engine)
