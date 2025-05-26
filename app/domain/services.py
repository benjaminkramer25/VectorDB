from uuid import UUID
from typing import List
from .models import Library, Document, Chunk
from .repositories import InMemoryRepo
from ..infrastructure.indexing import BaseIndex, LinearScan, KDTree, RandomProjection
from ..core.embedding import embed

class LibraryService:
    def __init__(self, repo: InMemoryRepo):
        self.repo = repo

    # ---------- libraries ----------
    async def create_library(self, name: str) -> Library:
        lib = Library(name=name)
        await self.repo.save_library(lib)
        return lib

    async def list_libraries(self) -> List[Library]:
        return await self.repo.list_libraries()

    async def get_library(self, lib_id: UUID) -> Library:
        lib = await self.repo.get_library(lib_id)
        if lib is None:
            raise ValueError("library not found")
        return lib

    async def update_library(self, lib_id: UUID, name: str) -> Library:
        lib = await self.get_library(lib_id)
        lib.name = name
        await self.repo.save_library(lib)
        return lib

    async def delete_library(self, lib_id: UUID) -> None:
        lib = await self.repo.delete_library(lib_id)
        if lib is None:
            raise ValueError("library not found")

    # ---------- chunks ----------
    async def add_chunk(self, lib_id: UUID, text: str) -> Chunk:
        lib = await self.repo.get_library(lib_id)
        if lib is None:
            raise ValueError("library not found")
        vec = embed(text)
        chunk = Chunk(text=text, embedding=vec)
        await self.repo.save_chunk(chunk)            # add to global store
        # attach to a single synthetic document:
        doc = Document(title="default")
        doc.chunks.append(chunk.id)
        await self.repo.save_document(doc)
        lib.documents.append(doc.id)
        await self.repo.save_library(lib)
        return chunk

    # ---------- chunks (CRUD) ----------
    async def list_chunks(self, lib_id: UUID) -> List[Chunk]:
        return await self.repo.list_chunks(lib_id)

    async def get_chunk(self, chunk_id: UUID) -> Chunk:
        chunk = await self.repo.get_chunk(chunk_id)
        if chunk is None:
            raise ValueError("chunk not found")
        return chunk

    async def update_chunk(self, chunk_id: UUID, text: str) -> Chunk:
        chunk = await self.get_chunk(chunk_id)
        chunk.text = text
        chunk.embedding = embed(text)
        await self.repo.save_chunk(chunk)
        return chunk

    async def delete_chunk(self, chunk_id: UUID) -> None:
        removed = await self.repo.delete_chunk(chunk_id)
        if removed is None:
            raise ValueError("chunk not found")

    # ---------- indexing ----------
    async def build_index(self, lib_id: UUID, algo: str = "linear") -> None:
        lib = await self.repo.get_library(lib_id)
        if lib is None:
            raise ValueError("library not found")
        vecs, ids = [], []
        for doc_id in lib.documents:
            doc = await self.repo.get_document(doc_id)
            for cid in doc.chunks:
                chunk = await self.repo.get_chunk(cid)
                vecs.append(chunk.embedding)
                ids.append(chunk.id)
        if algo == "kd":
            index: BaseIndex = KDTree(vecs, ids)
        elif algo == "lsh":
            index = RandomProjection(vecs, ids)
        else:
            index = LinearScan(vecs, ids)
        self.repo.indices[lib_id] = index

    async def query(self, lib_id: UUID, query_vec: List[float], k: int = 5) -> List[Chunk]:
        index = self.repo.indices.get(lib_id)
        if index is None:
            raise ValueError("library not indexed")
        ids = index.knn(query_vec, k)
        return [await self.repo.get_chunk(cid) for cid in ids]
