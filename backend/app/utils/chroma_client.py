import chromadb
from chromadb.config import Settings as ChromaSettings
import numpy as np
from typing import List, Dict, Any, Optional
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)

class ChromaDBClient:
    """ChromaDB client for vector storage and retrieval."""

    def __init__(self):
        self.client = None
        self.collection = None

    async def initialize(self):
        """Initialize ChromaDB client and collection."""
        try:
            self.client = chromadb.PersistentClient(
                path=settings.chroma_persist_directory,
                settings=ChromaSettings(
                    allow_reset=True,
                    anonymized_telemetry=False
                )
            )

            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=settings.chroma_collection_name,
                metadata={"description": "Design analysis embeddings"}
            )

            logger.info("ChromaDB initialized", collection_name=settings.chroma_collection_name)

        except Exception as e:
            logger.error("Failed to initialize ChromaDB", error=str(e))
            raise

    async def store_analysis(self, analysis_id: str, embeddings: List[float], metadata: Dict[str, Any]):
        """Store analysis results with embeddings."""
        try:
            self.collection.add(
                documents=[metadata.get("description", "")],
                embeddings=[embeddings],
                metadatas=[metadata],
                ids=[analysis_id]
            )
            logger.info("Stored analysis in vector DB", analysis_id=analysis_id)

        except Exception as e:
            logger.error("Failed to store analysis", analysis_id=analysis_id, error=str(e))

    async def find_similar(self, embeddings: List[float], n_results: int = 5) -> List[Dict[str, Any]]:
        """Find similar designs based on embeddings."""
        try:
            results = self.collection.query(
                query_embeddings=[embeddings],
                n_results=n_results
            )
            return results

        except Exception as e:
            logger.error("Failed to find similar designs", error=str(e))
            return []
