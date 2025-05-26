from uuid import UUID
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from .libraries import _SERVICE  # reuse same service

router = APIRouter(prefix="/chunks", tags=["chunks"])

class AddChunkDTO(BaseModel):
    lib_id: UUID
    text: str

class UpdateChunkDTO(BaseModel):
    text: str

@router.post("/")
async def add(dto: AddChunkDTO):
    return await _SERVICE.add_chunk(dto.lib_id, dto.text)

@router.get("/{chunk_id}")
async def get_chunk(chunk_id: UUID):
    try:
        return await _SERVICE.get_chunk(chunk_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.patch("/{chunk_id}")
async def update_chunk(chunk_id: UUID, body: UpdateChunkDTO):
    try:
        return await _SERVICE.update_chunk(chunk_id, body.text)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/{chunk_id}", status_code=204)
async def delete_chunk(chunk_id: UUID):
    try:
        await _SERVICE.delete_chunk(chunk_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
