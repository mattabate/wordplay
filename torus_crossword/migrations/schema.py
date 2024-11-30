from sqlalchemy import create_engine, Column, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import Enum as SQLEnum
import enum

# Database configuration
DATABASE_FILE = "database.db"
engine = create_engine(f"sqlite:///{DATABASE_FILE}", echo=False)

# Base class for ORM models
Base = declarative_base()


# Define the ReviewStatus enum class
class ReviewStatus(enum.Enum):
    NOT_REVIEWED = "not_reviewed"
    APPROVED = "approved"
    REJECTED = "rejected"


# Define the Word table
class Word(Base):
    __tablename__ = "words"
    word = Column(String, primary_key=True, unique=True, nullable=False)
    review_status = Column(
        SQLEnum(ReviewStatus), default=ReviewStatus.NOT_REVIEWED, nullable=False
    )
    matt_score = Column(Float, nullable=True)
    world_score = Column(Float, nullable=True)
    clues = Column(String, nullable=True)
    last_updated = Column(DateTime, nullable=True)


from sqlalchemy import Boolean


# Define the InitialCondition table
class InitialCondition(Base):
    __tablename__ = "initial_conditions"
    initial_condition = Column(
        String(120), primary_key=True, unique=True, nullable=False
    )
    contains_bad_words = Column(Boolean, nullable=True)
    created_at = Column(DateTime, nullable=True)
