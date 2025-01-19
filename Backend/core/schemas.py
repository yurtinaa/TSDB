from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class DgTimeSeries(BaseModel):
    id: int
    name: str
    len: int
    description: Optional[str]
    model_config = ConfigDict(from_attributes=True)


class ProjectDTO(BaseModel):
    project_name: str
    description: Optional[str] = None


class PrimitiveDTO(BaseModel):
    ts_id: int
    primitive_name: str
    subseqLen: int
    topK: Optional[int]


class InputProjectAndPrimitives(BaseModel):
    project: ProjectDTO
    primitives: List[PrimitiveDTO] = []
    ts_ids: List[int] = []


class DgProject(BaseModel):
    id: int
    name: str
    create_date: datetime
    description: Optional[str]
    model_config = ConfigDict(from_attributes=True)


class TimeSeriesDTO(BaseModel):
    ts_name: str
    len: int
    ts_description: Optional[str] = None


class OutProjectAndTimeSeries(BaseModel):
    project: ProjectDTO
    time_series: List[TimeSeriesDTO] = []


class DgTimeSeriesToDisplay(BaseModel):
    id: int
    name: str
    stamp: Optional[List[datetime]]
    value: List[float]
    description: Optional[str]
    model_config = ConfigDict(from_attributes=True)


class DgPrimitiveToDisplay(BaseModel):
    name: str
    subseqLen: int
    ts_id: int
    key: str
    nnDist: List[float] = []
    indexes: List[int] = []
