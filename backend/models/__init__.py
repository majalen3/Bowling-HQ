"""SQLAlchemy ORM models — mirrors the PostgreSQL schema exactly."""
from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from db import Base


def _uuid() -> uuid.UUID:
    return uuid.uuid4()


# ─── Users ───────────────────────────────────────────────────────────────────


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_uuid
    )
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(Text, nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(100))
    hand: Mapped[str] = mapped_column(String(5), nullable=False, default="right")
    ball_speed_avg: Mapped[float | None] = mapped_column(Numeric(4, 1))
    rev_rate_avg: Mapped[int | None] = mapped_column(Integer)
    axis_rotation: Mapped[float | None] = mapped_column(Numeric(5, 2))
    axis_tilt: Mapped[float | None] = mapped_column(Numeric(5, 2))
    experience_level: Mapped[str] = mapped_column(
        String(20), nullable=False, default="beginner"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(), onupdate=func.now()
    )

    arsenal: Mapped[list[UserArsenal]] = relationship(back_populates="user")
    sessions: Mapped[list[BowlingSession]] = relationship(back_populates="user")


# ─── Bowling Centers ──────────────────────────────────────────────────────────


class BowlingCenter(Base):
    __tablename__ = "bowling_centers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_uuid
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    address: Mapped[str | None] = mapped_column(String(255))
    city: Mapped[str | None] = mapped_column(String(100))
    state: Mapped[str | None] = mapped_column(String(50))
    country: Mapped[str] = mapped_column(String(50), nullable=False, default="USA")
    lanes_count: Mapped[int | None] = mapped_column(Integer)
    year_built: Mapped[int | None] = mapped_column(Integer)
    last_renovated: Mapped[int | None] = mapped_column(Integer)
    rating: Mapped[float | None] = mapped_column(Numeric(3, 2))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )


# ─── Lane Patterns ────────────────────────────────────────────────────────────


class LanePattern(Base):
    __tablename__ = "lane_patterns"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_uuid
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    pattern_type: Mapped[str] = mapped_column(String(20), nullable=False, default="house")
    oil_volume: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    length_feet: Mapped[int | None] = mapped_column(Integer)
    difficulty_score: Mapped[float | None] = mapped_column(Numeric(4, 2))
    board_distribution: Mapped[dict | None] = mapped_column(JSONB)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )


# ─── Bowling Balls ────────────────────────────────────────────────────────────


class BowlingBall(Base):
    __tablename__ = "bowling_balls"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_uuid
    )
    brand: Mapped[str] = mapped_column(String(80), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    weight_oz: Mapped[float] = mapped_column(Numeric(4, 1), nullable=False)
    core_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="symmetrical"
    )
    rg_min: Mapped[float | None] = mapped_column(Numeric(5, 3))
    differential: Mapped[float | None] = mapped_column(Numeric(5, 3))
    coverstock_type: Mapped[str] = mapped_column(
        String(30), nullable=False, default="reactive"
    )
    finish: Mapped[str | None] = mapped_column(String(50))
    release_year: Mapped[int | None] = mapped_column(Integer)
    best_conditions: Mapped[str] = mapped_column(
        String(20), nullable=False, default="medium"
    )
    hook_potential: Mapped[float | None] = mapped_column(Numeric(3, 1))
    length_score: Mapped[float | None] = mapped_column(Numeric(3, 1))
    backend_score: Mapped[float | None] = mapped_column(Numeric(3, 1))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )

    __table_args__ = (UniqueConstraint("brand", "name", "weight_oz"),)

    arsenal_entries: Mapped[list[UserArsenal]] = relationship(back_populates="ball")


# ─── User Arsenal ─────────────────────────────────────────────────────────────


class UserArsenal(Base):
    __tablename__ = "user_arsenal"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_uuid
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    ball_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bowling_balls.id"), nullable=False
    )
    layout: Mapped[str | None] = mapped_column(String(50))
    purchase_date: Mapped[date | None] = mapped_column(Date)
    games_thrown: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_retired: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    personal_notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(), onupdate=func.now()
    )

    user: Mapped[User] = relationship(back_populates="arsenal")
    ball: Mapped[BowlingBall] = relationship(back_populates="arsenal_entries")


# ─── Bowling Sessions ─────────────────────────────────────────────────────────


class BowlingSession(Base):
    __tablename__ = "bowling_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_uuid
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    center_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bowling_centers.id")
    )
    pattern_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lane_patterns.id")
    )
    session_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="practice"
    )
    session_date: Mapped[date] = mapped_column(Date, nullable=False)
    duration_min: Mapped[int | None] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(), onupdate=func.now()
    )

    user: Mapped[User] = relationship(back_populates="sessions")
    games: Mapped[list[Game]] = relationship(back_populates="session")


# ─── Games ───────────────────────────────────────────────────────────────────


class Game(Base):
    __tablename__ = "games"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_uuid
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("bowling_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    lane_number: Mapped[int | None] = mapped_column(Integer)
    primary_ball_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bowling_balls.id")
    )
    total_score: Mapped[int | None] = mapped_column(Integer)
    strike_count: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    spare_count: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    open_count: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    game_number: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )

    session: Mapped[BowlingSession] = relationship(back_populates="games")
    frames: Mapped[list[Frame]] = relationship(back_populates="game")


# ─── Frames ──────────────────────────────────────────────────────────────────


class Frame(Base):
    __tablename__ = "frames"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_uuid
    )
    game_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("games.id", ondelete="CASCADE"),
        nullable=False,
    )
    frame_number: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    ball_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bowling_balls.id")
    )
    first_ball_pins: Mapped[int | None] = mapped_column(SmallInteger)
    second_ball_pins: Mapped[int | None] = mapped_column(SmallInteger)
    third_ball_pins: Mapped[int | None] = mapped_column(SmallInteger)
    result_type: Mapped[str] = mapped_column(String(10), nullable=False, default="open")
    board_number: Mapped[int | None] = mapped_column(SmallInteger)
    speed_mph: Mapped[float | None] = mapped_column(Numeric(4, 1))
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )

    __table_args__ = (UniqueConstraint("game_id", "frame_number"),)

    game: Mapped[Game] = relationship(back_populates="frames")


# ─── Commander Recommendations ────────────────────────────────────────────────


class CommanderRecommendation(Base):
    __tablename__ = "commander_recommendations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_uuid
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bowling_sessions.id")
    )
    frame_number: Mapped[int | None] = mapped_column(SmallInteger)
    recommended_ball_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bowling_balls.id")
    )
    confidence_score: Mapped[float | None] = mapped_column(Numeric(5, 4))
    reasoning: Mapped[dict | None] = mapped_column(JSONB)
    was_followed: Mapped[bool | None] = mapped_column(Boolean)
    actual_result: Mapped[int | None] = mapped_column(SmallInteger)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )


# ─── Tournament Bag Lineups ───────────────────────────────────────────────────


class TournamentBagLineup(Base):
    __tablename__ = "tournament_bag_lineups"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_uuid
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    target_pattern_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lane_patterns.id")
    )
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(), onupdate=func.now()
    )

    balls: Mapped[list[LineupBall]] = relationship(back_populates="lineup")


class LineupBall(Base):
    __tablename__ = "lineup_balls"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_uuid
    )
    lineup_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tournament_bag_lineups.id", ondelete="CASCADE"),
        nullable=False,
    )
    arsenal_entry_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user_arsenal.id"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="primary")
    ball_order: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)

    lineup: Mapped[TournamentBagLineup] = relationship(back_populates="balls")
