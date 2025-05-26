from __future__ import annotations
from uuid import uuid4, UUID
from datetime import datetime
from typing import List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class Chunk(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    text: str
    embedding: List[float] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Document(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    title: str
    chunks: List[UUID] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Library(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    documents: List[UUID] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
