from sqlalchemy import String, ForeignKey, text, ARRAY, BigInteger, Float, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from database import Base
from typing import Optional, List, Annotated
from datetime import datetime

bigintPk = Annotated[int, mapped_column(BigInteger, primary_key=True)]
tsIdFk = Annotated[int, mapped_column(ForeignKey("time_series.id", ondelete="CASCADE"))]
listFloat = Annotated[List[float], mapped_column(ARRAY(Float))]
listBigint = Annotated[List[int], mapped_column(ARRAY(BigInteger))]


class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id: Mapped[bigintPk]
    login: Mapped[str] = mapped_column(String, unique=True)
    hashed_password: Mapped[str] = mapped_column(String)
    mail: Mapped[str] = mapped_column(unique=True)


class Project(Base):
    __tablename__ = "projects"
    __table_args__ = {'extend_existing': True}

    id: Mapped[bigintPk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    ts_ids: Mapped[Optional[listBigint]]
    dim: Mapped[Optional[int]]
    name: Mapped[str] = mapped_column(String(50))
    create_date: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))
    description: Mapped[Optional[str]]


class TimeSeries(Base):
    __tablename__ = "time_series"
    __table_args__ = {'extend_existing': True}

    id: Mapped[bigintPk]
    project_id: Mapped[Optional[int]] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    name: Mapped[str]
    stamp: Mapped[List[datetime]] = mapped_column(ARRAY(TIMESTAMP))
    value: Mapped[listFloat]
    len: Mapped[int]
    description: Mapped[Optional[str]]


class MatrixProfile(Base):
    __tablename__ = "matrix_profiles"
    __table_args__ = {'extend_existing': True}

    id: Mapped[bigintPk]
    ts_id: Mapped[tsIdFk]
    nnDist: Mapped[listFloat]
    nnIdx: Mapped[listBigint]
    left_nnIdx: Mapped[listBigint]
    right_nnIdx: Mapped[listBigint]
    subseqLen: Mapped[int]


class Discord(Base):
    __tablename__ = "discords"
    __table_args__ = {'extend_existing': True}

    id: Mapped[bigintPk]
    ts_id: Mapped[tsIdFk]
    indexes: Mapped[listBigint]
    nnDist: Mapped[listFloat]
    subseqLen: Mapped[int]
    k: Mapped[int]


class Snippet(Base):
    __tablename__ = "snippets"
    __table_args__ = {'extend_existing': True}

    id: Mapped[bigintPk]
    ts_id: Mapped[tsIdFk]
    indexes: Mapped[listBigint]
    freq: Mapped[listFloat]
    subseqLen: Mapped[int]
    k: Mapped[int]


class Motif(Base):
    __tablename__ = "motifs"
    __table_args__ = {'extend_existing': True}

    id: Mapped[bigintPk]
    ts_id: Mapped[tsIdFk]
    indexes_left: Mapped[listBigint]
    indexes_right: Mapped[listBigint]
    nnDist: Mapped[listFloat]
    subseqLen: Mapped[int]
    k: Mapped[int]


class Chain(Base):
    __tablename__ = "chains"
    __table_args__ = {'extend_existing': True}

    id: Mapped[bigintPk]
    ts_id: Mapped[tsIdFk]
    indexes: Mapped[listBigint]
    numElements: Mapped[listBigint]
    subseqLen: Mapped[int]
    k: Mapped[int]


class FoundPrimitive(Base):
    __tablename__ = "found_primitives"
    __table_args__ = {'extend_existing': True}

    id: Mapped[bigintPk]
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    matrix_pr_ids: Mapped[listBigint]
    discord_ids: Mapped[listBigint]
    motif_ids: Mapped[listBigint]
    snippet_ids: Mapped[listBigint]
    chain_ids: Mapped[listBigint]
