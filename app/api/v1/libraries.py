from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from ...domain.services import LibraryService
from ...domain.repositories import InMemoryRepo

router = APIRouter(prefix="/libraries", tags=["libraries"])
_SERVICE = LibraryService(InMemoryRepo())   # singleton for demo

class CreateLibraryDTO(BaseModel):
    name: str

class BuildIndexDTO(BaseModel):
    algo: str = "linear"         # linear | kd | lsh

class QueryDTO(BaseModel):
    embedding: list[float]
    k: int = 5

class UpdateLibraryDTO(BaseModel):
    name: str

@router.post("/", status_code=201)
async def create(dto: CreateLibraryDTO):
    return await _SERVICE.create_library(dto.name)

@router.post("/{lib_id}/index")
async def build_index(lib_id: UUID, body: BuildIndexDTO):
    await _SERVICE.build_index(lib_id, body.algo)
    return {"status": "indexed", "algorithm": body.algo}

@router.post("/{lib_id}/query")
async def query(lib_id: UUID, body: QueryDTO):
    chunks = await _SERVICE.query(lib_id, body.embedding, body.k)
    return chunks

@router.get("/")
async def list_libraries():
    return await _SERVICE.list_libraries()

@router.get("/{lib_id}")
async def get_library(lib_id: UUID):
    try:
        return await _SERVICE.get_library(lib_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.patch("/{lib_id}")
async def update_library(lib_id: UUID, body: UpdateLibraryDTO):
    try:
        return await _SERVICE.update_library(lib_id, body.name)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/{lib_id}", status_code=204)
async def delete_library(lib_id: UUID):
    try:
        await _SERVICE.delete_library(lib_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/{lib_id}/chunks")
async def list_chunks(lib_id: UUID):
    return await _SERVICE.list_chunks(lib_id)
