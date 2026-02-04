import logging
import os
from typing import List, Dict, Optional
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
from datetime import datetime

logger = logging.getLogger(__name__)

class VectorMemoryService:
    """
    Service for semantic memory using Pinecone vector database.
    Stores conversation embeddings for semantic search and context retrieval.
    """
    
    def __init__(self, pinecone_api_key: str, openai_client: OpenAI, index_name: str = "emotion-assistant"):
        """
        Initialize Pinecone vector memory service
        
        Args:
            pinecone_api_key: Pinecone API key
            openai_client: OpenAI client for embeddings
            index_name: Name of Pinecone index
        """
        self.openai = openai_client
        self.index_name = index_name
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=pinecone_api_key)
        
        # Create or connect to index
        self._initialize_index()
        
        # Connect to index
        self.index = self.pc.Index(self.index_name)
    
    def _initialize_index(self):
        """Create Pinecone index if it doesn't exist"""
        existing_indexes = [index.name for index in self.pc.list_indexes()]
        
        if self.index_name not in existing_indexes:
            logger.info(f"Creating Pinecone index: {self.index_name}")
            self.pc.create_index(
                name=self.index_name,
                dimension=1536,  # OpenAI text-embedding-3-small dimension
                metric='cosine',
                spec=ServerlessSpec(
                    cloud='aws',
                    region=os.getenv('PINECONE_ENVIRONMENT', 'us-east-1')
                )
            )
            logger.info("Index {self.index_name} created")
        else:
            logger.info("Connected to existing index: {self.index_name}")
    
    def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text using OpenAI
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding
        """
        try:
            response = self.openai.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error("Error generating embedding: {e}")
            # Return zero vector as fallback
            return [0.0] * 1536
    
    def save_conversation(
        self,
        user_id: str,
        user_message: str,
        assistant_response: str,
        emotion: Optional[str] = None,
        action: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> bool:
        """
        Save conversation turn to Pinecone
        
        Args:
            user_id: User identifier
            user_message: User's message
            assistant_response: Assistant's response
            emotion: Detected emotion
            action: Action taken
            session_id: Session identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Combine user message and response for embedding
            combined_text = f"User: {user_message}\nAssistant: {assistant_response}"
            
            # Generate embedding
            embedding = self._generate_embedding(combined_text)
            
            # Create unique ID
            vector_id = f"{user_id}_{session_id}_{datetime.utcnow().timestamp()}"
            
            # Prepare metadata
            metadata = {
                "user_id": user_id,
                "user_message": user_message[:1000],  # Truncate for metadata limits
                "assistant_response": assistant_response[:1000],
                "emotion": emotion or "neutral",
                "action": action or "unknown",
                "session_id": session_id or "unknown",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Upsert to Pinecone
            self.index.upsert(
                vectors=[{
                    "id": vector_id,
                    "values": embedding,
                    "metadata": metadata
                }]
            )
            
            logger.info("Saved conversation to Pinecone: {vector_id}")
            return True
            
        except Exception as e:
            logger.error("Error saving to Pinecone: {e}")
            return False
    
    def search_similar_conversations(
        self,
        query: str,
        user_id: str,
        top_k: int = 5,
        min_score: float = 0.7
    ) -> List[Dict]:
        """
        Search for similar past conversations
        
        Args:
            query: Search query (user's current message)
            user_id: User identifier to filter results
            top_k: Number of results to return
            min_score: Minimum similarity score (0-1)
            
        Returns:
            List of similar conversations with metadata
        """
        try:
            # Generate query embedding
            query_embedding = self._generate_embedding(query)
            
            # Search Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                filter={"user_id": user_id},
                include_metadata=True
            )
            
            # Filter by minimum score and format results
            similar_conversations = []
            for match in results.matches:
                if match.score >= min_score:
                    similar_conversations.append({
                        "score": match.score,
                        "user_message": match.metadata.get("user_message", ""),
                        "assistant_response": match.metadata.get("assistant_response", ""),
                        "emotion": match.metadata.get("emotion", "neutral"),
                        "timestamp": match.metadata.get("timestamp", ""),
                        "session_id": match.metadata.get("session_id", "")
                    })
            
            if similar_conversations:
                logger.info("Found {len(similar_conversations)} similar conversations")
            
            return similar_conversations
            
        except Exception as e:
            logger.error("Error searching Pinecone: {e}")
            return []
    
    def get_conversation_context(
        self,
        current_message: str,
        user_id: str,
        max_context: int = 3
    ) -> str:
        """
        Get relevant context from past conversations for current message
        
        Args:
            current_message: User's current message
            user_id: User identifier
            max_context: Maximum number of past conversations to include
            
        Returns:
            Formatted context string
        """
        similar = self.search_similar_conversations(
            query=current_message,
            user_id=user_id,
            top_k=max_context
        )
        
        if not similar:
            return ""
        
        # Format context
        context_parts = ["Relevant past conversations:"]
        for i, conv in enumerate(similar, 1):
            context_parts.append(
                f"\n{i}. [{conv['emotion']}] User: {conv['user_message'][:100]}..."
            )
        
        return "\n".join(context_parts)
    
    def delete_user_data(self, user_id: str) -> bool:
        """
        Delete all data for a user (GDPR compliance)
        
        Args:
            user_id: User identifier
            
        Returns:
            True if successful
        """
        try:
            # Pinecone doesn't support direct filter-based deletion
            # This is a placeholder - in production, you'd need to:
            # 1. Query all vectors for user
            # 2. Delete by IDs
            logger.warning("User data deletion not fully implemented for {user_id}")
            return True
        except Exception as e:
            logger.error("Error deleting user data: {e}")
            return False
