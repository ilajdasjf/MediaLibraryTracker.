"""
Main media catalog application using OOP principles.
"""
import csv
import os
from typing import List, Optional, Dict, Any
from models import MediaItem
from database import Database

class MediaCatalog:
    """Main controller class for the media catalog application."""
    
    def __init__(self):
        self.db = Database()
        self.current_items: List[MediaItem] = []
        self.load_items()
    
    def load_items(self):
        """Load all items from the database."""
        self.current_items = self.db.get_all_items()
    
    def add_item(self, title: str, category: str, status: str = "Unwatched",
                 rating: float = 0.0, notes: str = "", image_path: str = "") -> Optional[int]:
        """Add a new media item."""
        try:
            # Validate inputs
            if not title or not category:
                raise ValueError("Title and category are required")
            
            if rating < 0 or rating > 10:
                raise ValueError("Rating must be between 0 and 10")
            
            item = MediaItem(
                title=title.strip(),
                category=category.strip(),
                status=status,
                rating=rating,
                notes=notes.strip(),
                image_path=image_path.strip()
            )
            
            item_id = self.db.add_item(item)
            self.load_items()  # Refresh the list
            return item_id
        except Exception as e:
            print(f"Error adding item: {e}")
            return None
    
    def update_item(self, item_id: int, **kwargs) -> bool:
        """Update an existing media item."""
        try:
            item = self.db.get_item_by_id(item_id)
            if not item:
                return False
            
            # Update fields
            for key, value in kwargs.items():
                if hasattr(item, key):
                    if key == 'rating' and (value < 0 or value > 10):
                        raise ValueError("Rating must be between 0 and 10")
                    setattr(item, key, value)
            
            success = self.db.update_item(item)
            if success:
                self.load_items()
            return success
        except Exception as e:
            print(f"Error updating item: {e}")
            return False
    
    def delete_item(self, item_id: int) -> bool:
        """Delete a media item."""
        success = self.db.delete_item(item_id)
        if success:
            self.load_items()
        return success
    
    def toggle_status(self, item_id: int) -> bool:
        """Toggle the status between Watched and Unwatched."""
        item = self.db.get_item_by_id(item_id)
        if not item:
            return False
        
        new_status = "Watched" if item.status == "Unwatched" else "Unwatched"
        return self.update_item(item_id, status=new_status)
    
    def search_items(self, query: str, field: str = "all") -> List[MediaItem]:
        """Search for items."""
        if not query:
            self.load_items()
            return self.current_items
        return self.db.search_items(query, field)
    
    def get_items_by_category(self, category: Optional[str] = None) -> List[MediaItem]:
        """Get items filtered by category."""
        if category:
            return [item for item in self.current_items if item.category == category]
        return self.current_items
    
    def get_items_by_status(self, status: Optional[str] = None) -> List[MediaItem]:
        """Get items filtered by status."""
        if status:
            return [item for item in self.current_items if item.status == status]
        return self.current_items
    
    def sort_items(self, items: List[MediaItem], field: str, reverse: bool = False) -> List[MediaItem]:
        """Sort items by the specified field."""
        if not items:
            return []
        
        valid_fields = ['title', 'category', 'status', 'rating', 'created_at']
        if field not in valid_fields:
            field = 'title'
        
        return sorted(items, key=lambda x: getattr(x, field, ''), reverse=reverse)
    
    def export_to_csv(self, items: List[MediaItem], filename: str = "media_export.csv") -> bool:
        """Export items to CSV file."""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['id', 'title', 'category', 'status', 'rating', 'notes', 'image_path']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for item in items:
                    writer.writerow(item.to_dict())
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get catalog statistics."""
        return self.db.get_statistics()
    
    def import_from_csv(self, filename: str) -> bool:
        """Import items from CSV file."""
        try:
            with open(filename, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                imported = 0
                for row in reader:
                    item = MediaItem.from_dict(row)
                    if self.add_item(
                        title=item.title,
                        category=item.category,
                        status=item.status,
                        rating=float(item.rating),
                        notes=item.notes,
                        image_path=item.image_path
                    ):
                        imported += 1
            self.load_items()
            return imported > 0
        except Exception as e:
            print(f"Error importing from CSV: {e}")
            return False
