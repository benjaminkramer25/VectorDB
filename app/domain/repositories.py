import asyncio
from uuid import UUID
from typing import Dict, List
from .models import Library, Document, Chunk

class InMemoryRepo:
    """Single-node demo storage; guarded by a reader–writer lock."""

    def __init__(self) -> None:
        self.libraries: Dict[UUID, Library] = {}
        self.documents: Dict[UUID, Document] = {}
        self.chunks: Dict[UUID, Chunk] = {}
        self.indices = {}                 # lib_id → BaseIndex
        self._write_lock = asyncio.Lock()
        self._readers = 0
        self._readers_lock = asyncio.Lock()

    # ----------  helpers for concurrency  ----------
    async def _acquire_read(self):
        async with self._readers_lock:
            self._readers += 1
            if self._readers == 1:
                await self._write_lock.acquire()

    async def _release_read(self):
        async with self._readers_lock:
            self._readers -= 1
            if self._readers == 0:
                self._write_lock.release()

    # ----------  CRUD (simplest possible)  ----------
    async def save_library(self, lib: Library):
        async with self._write_lock:
            self.libraries[lib.id] = lib

    async def get_library(self, lib_id: UUID) -> Library | None:
        await self._acquire_read()
        lib = self.libraries.get(lib_id)
        await self._release_read()
        return lib

    # ---------- documents ----------
    async def save_document(self, doc: Document):
        async with self._write_lock:
            self.documents[doc.id] = doc

    async def get_document(self, doc_id: UUID) -> Document | None:
        await self._acquire_read()
        doc = self.documents.get(doc_id)
        await self._release_read()
        return doc

    # ---------- chunks ----------
    async def save_chunk(self, chunk: Chunk):
        async with self._write_lock:
            self.chunks[chunk.id] = chunk

    async def get_chunk(self, chunk_id: UUID) -> Chunk | None:
        await self._acquire_read()
        chunk = self.chunks.get(chunk_id)
        await self._release_read()
        return chunk

    # …analogous methods for documents / chunks …

    async def list_libraries(self) -> List[Library]:
        await self._acquire_read()
        libs = list(self.libraries.values())
        await self._release_read()
        return libs

    # ---------- delete ----------
    async def delete_library(self, lib_id: UUID):
        async with self._write_lock:
            lib = self.libraries.pop(lib_id, None)
            if lib is None:
                return None
            # cascade delete docs & chunks
            for doc_id in lib.documents:
                doc = self.documents.pop(doc_id, None)
                if doc:
                    for cid in doc.chunks:
                        self.chunks.pop(cid, None)
            # remove index
            self.indices.pop(lib_id, None)
            return lib

    async def delete_chunk(self, chunk_id: UUID):
        async with self._write_lock:
            return self.chunks.pop(chunk_id, None)

    async def list_chunks(self, lib_id: UUID) -> List[Chunk]:
        await self._acquire_read()
        lib = self.libraries.get(lib_id)
        if lib is None:
            await self._release_read()
            return []
        chunk_ids: List[UUID] = []
        for doc_id in lib.documents:
            doc = self.documents.get(doc_id)
            if doc:
                chunk_ids.extend(doc.chunks)
        chunks = [self.chunks[cid] for cid in chunk_ids if cid in self.chunks]
        await self._release_read()
        return chunks
