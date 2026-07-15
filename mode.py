"""
Data models for the media catalog application.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class MediaItem:
    """Represents a media item in the catalog."""
    id: Optional[int] = None
    title: str = ""
    category: str = ""
    status: str = "Unwatched"  # Unwatched/Watched/In Progress
    rating: float = 0.0  # 0-10
    notes: str = ""
    image_path: str = ""
    created_at: str = None
    updated_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.now().isoformat()
    
    def update_timestamp(self):
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self):
        """Convert to dictionary for storage."""
        return {
            'id': self.id,
            'title': self.title,
            'category': self.category,
            'status': self.status,
            'rating': self.rating,
            'notes': self.notes,
            'image_path': self.image_path,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create MediaItem from dictionary."""
        return cls(
            id=data.get('id'),
            title=data.get('title', ''),
            category=data.get('category', ''),
            status=data.get('status', 'Unwatched'),
            rating=float(data.get('rating', 0.0)),
            notes=data.get('notes', ''),
            image_path=data.get('image_path', ''),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
