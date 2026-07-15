"""
GUI for the media catalog application using tkinter.
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from typing import List, Optional
import os
from models import MediaItem
from media_catalog import MediaCatalog

class MediaCatalogGUI:
    """Main GUI class for the media catalog application."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Media Catalog")
        self.root.geometry("1200x700")
        
        self.catalog = MediaCatalog()
        self.current_items: List[MediaItem] = []
        self.selected_item_id: Optional[int] = None
        
        # Categories for dropdown
        self.categories = ["Book", "Movie", "Game", "Music", "TV Show", "Other"]
        
        self.setup_ui()
        self.refresh_display()
    
    def setup_ui(self):
        """Setup the main user interface."""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # ========== Top Frame: Search and Filters ==========
        search_frame = ttk.LabelFrame(main_frame, text="Search & Filter", padding="10")
        search_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.columnconfigure(1, weight=1)
        
        # Search
        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        self.search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        self.search_entry.bind('<KeyRelease>', lambda e: self.perform_search())
        
        # Search field dropdown
        ttk.Label(search_frame, text="Field:").grid(row=0, column=2, padx=(5, 5))
        self.search_field = ttk.Combobox(search_frame, values=["all", "title", "category", "status"], 
                                         state="readonly", width=10)
        self.search_field.set("all")
        self.search_field.grid(row=0, column=3, padx=(0, 5))
        self.search_field.bind('<<ComboboxSelected>>', lambda e: self.perform_search())
        
        # Category filter
        ttk.Label(search_frame, text="Category:").grid(row=0, column=4, padx=(5, 5))
        self.category_filter = ttk.Combobox(search_frame, values=["All"] + self.categories, 
                                            state="readonly", width=12)
        self.category_filter.set("All")
        self.category_filter.grid(row=0, column=5, padx=(0, 5))
        self.category_filter.bind('<<ComboboxSelected>>', lambda e: self.apply_filters())
        
        # Status filter
        ttk.Label(search_frame, text="Status:").grid(row=0, column=6, padx=(5, 5))
        self.status_filter = ttk.Combobox(search_frame, values=["All", "Unwatched", "Watched", "In Progress"], 
                                          state="readonly", width=12)
        self.status_filter.set("All")
        self.status_filter.grid(row=0, column=7, padx=(0, 5))
        self.status_filter.bind('<<ComboboxSelected>>', lambda e: self.apply_filters())
        
        # Sort by
        ttk.Label(search_frame, text="Sort:").grid(row=1, column=0, padx=(0, 5), pady=(5, 0))
        self.sort_var = tk.StringVar(value="title")
        sort_combo = ttk.Combobox(search_frame, textvariable=self.sort_var, 
                                 values=["title", "category", "status", "rating", "created_at"],
                                 state="readonly", width=12)
        sort_combo.grid(row=1, column=1, sticky=(tk.W), pady=(5, 0))
        sort_combo.bind('<<ComboboxSelected>>', lambda e: self.apply_filters())
        
        # Sort order checkbox
        self.sort_reverse = tk.BooleanVar(value=False)
        ttk.Checkbutton(search_frame, text="Reverse", variable=self.sort_reverse,
                       command=self.apply_filters).grid(row=1, column=2, pady=(5, 0))
        
        # Clear button
        ttk.Button(search_frame, text="Clear Filters", command=self.clear_filters).grid(
            row=1, column=7, pady=(5, 0))
        
        # ========== Left Frame: Item List ==========
        list_frame = ttk.LabelFrame(main_frame, text="Media Items", padding="10")
        list_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Treeview for items
        columns = ("ID", "Title", "Category", "Status", "Rating")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # Define headings
        self.tree.heading("ID", text="ID")
        self.tree.heading("Title", text="Title")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Rating", text="Rating")
        
        # Define column widths
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Title", width=250)
        self.tree.column("Category", width=100, anchor="center")
        self.tree.column("Status", width=100, anchor="center")
        self.tree.column("Rating", width=80, anchor="center")
        
        # Scrollbars
        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(list_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        vsb.grid(row=0, column=1, sticky=(tk.N, tk.S))
        hsb.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Bind selection event
        self.tree.bind('<<TreeviewSelect>>', self.on_item_select)
        
        # ========== Right Frame: Item Details ==========
        detail_frame = ttk.LabelFrame(main_frame, text="Item Details", padding="10")
        detail_frame.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0), pady=(0, 10))
        detail_frame.columnconfigure(1, weight=1)
        
        # Title
        ttk.Label(detail_frame, text="Title:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.title_var = tk.StringVar()
        self.title_entry = ttk.Entry(detail_frame, textvariable=self.title_var, width=30)
        self.title_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5), padx=(5, 0))
        
        # Category
        ttk.Label(detail_frame, text="Category:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(detail_frame, textvariable=self.category_var,
                                           values=self.categories, state="readonly", width=28)
        self.category_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 5), padx=(5, 0))
        
        # Status
        ttk.Label(detail_frame, text="Status:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.status_var = tk.StringVar()
        self.status_combo = ttk.Combobox(detail_frame, textvariable=self.status_var,
                                         values=["Unwatched", "Watched", "In Progress"],
                                         state="readonly", width=28)
        self.status_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(0, 5), padx=(5, 0))
        
        # Rating
        ttk.Label(detail_frame, text="Rating (0-10):").grid(row=3, column=0, sticky=tk.W, pady=(0, 5))
        self.rating_var = tk.StringVar()
        self.rating_entry = ttk.Entry(detail_frame, textvariable=self.rating_var, width=30)
        self.rating_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=(0, 5), padx=(5, 0))
        
        # Notes
        ttk.Label(detail_frame, text="Notes:").grid(row=4, column=0, sticky=(tk.W, tk.N), pady=(0, 5))
        self.notes_text = scrolledtext.ScrolledText(detail_frame, height=5, width=30, wrap=tk.WORD)
        self.notes_text.grid(row=4, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5), padx=(5, 0))
        detail_frame.rowconfigure(4, weight=1)
        
        # Image path
        ttk.Label(detail_frame, text="Image Path:").grid(row=5, column=0, sticky=tk.W, pady=(0, 5))
        self.image_path_var = tk.StringVar()
        self.image_path_entry = ttk.Entry(detail_frame, textvariable=self.image_path_var, width=25)
        self.image_path_entry.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=(0, 5), padx=(5, 0))
        ttk.Button(detail_frame, text="Browse", command=self.browse_image).grid(
            row=5, column=2, padx=(2, 0), pady=(0, 5))
        
        # ========== Bottom Frame: Action Buttons ==========
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Add/Update/Delete buttons
        self.add_btn = ttk.Button(button_frame, text="Add Item", command=self.add_item)
        self.add_btn.grid(row=0, column=0, padx=(0, 5))
        
        self.update_btn = ttk.Button(button_frame, text="Update Item", command=self.update_item, state="disabled")
        self.update_btn.grid(row=0, column=1, padx=(0, 5))
        
        self.delete_btn = ttk.Button(button_frame, text="Delete Item", command=self.delete_item, state="disabled")
        self.delete_btn.grid(row=0, column=2, padx=(0, 5))
        
        self.toggle_btn = ttk.Button(button_frame, text="Toggle Status", command=self.toggle_status, state="disabled")
        self.toggle_btn.grid(row=0, column=3, padx=(0, 5))
        
        # Export/Import buttons
        self.export_btn = ttk.Button(button_frame, text="Export CSV", command=self.export_csv)
        self.export_btn.grid(row=0, column=4, padx=(0, 5))
        
        self.import_btn = ttk.Button(button_frame, text="Import CSV", command=self.import_csv)
        self.import_btn.grid(row=0, column=5, padx=(0, 5))
        
        # Refresh button
        ttk.Button(button_frame, text="Refresh", command=self.refresh_display).grid(row=0, column=6, padx=(0, 5))
        
        # Clear form button
        ttk.Button(button_frame, text="Clear Form", command=self.clear_form).grid(row=0, column=7)
        
        # ========== Statistics Frame ==========
        stats_frame = ttk.LabelFrame(main_frame, text="Statistics", padding="10")
        stats_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E))
        stats_frame.columnconfigure(0, weight=1)
        
        self.stats_label = ttk.Label(stats_frame, text="Loading statistics...")
        self.stats_label.grid(row=0, column=0, sticky=tk.W)
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-n>', lambda e: self.add_item())
        self.root.bind('<Control-s>', lambda e: self.update_item())
        self.root.bind('<Delete>', lambda e: self.delete_item())
        
        # Update statistics
        self.update_statistics()
    
    def refresh_display(self):
        """Refresh the treeview with current items."""
        # Get current items with filters
        self.apply_filters()
    
    def apply_filters(self):
        """Apply search, category, and status filters."""
        # Get search query
        query = self.search_var.get().strip()
        search_field = self.search_field.get()
        
        # Perform search
        if query:
            self.current_items = self.catalog.search_items(query, search_field)
        else:
            self.current_items = self.catalog.current_items.copy()
        
        # Apply category filter
        category = self.category_filter.get()
        if category and category != "All":
            self.current_items = [item for item in self.current_items if item.category == category]
        
        # Apply status filter
        status = self.status_filter.get()
        if status and status != "All":
            self.current_items = [item for item in self.current_items if item.status == status]
        
        # Apply sorting
        sort_field = self.sort_var.get()
        reverse = self.sort_reverse.get()
        self.current_items = self.catalog.sort_items(self.current_items, sort_field, reverse)
        
        # Update treeview
        self.update_treeview()
    
    def update_treeview(self):
        """Update the treeview with current items."""
        # Clear treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add items
        for item in self.current_items:
            rating_str = f"{item.rating:.1f}" if item.rating > 0 else "-"
            self.tree.insert("", "end", values=(
                item.id, item.title, item.category, item.status, rating_str
            ), tags=(item.id,))
        
        # Update statistics
        self.update_statistics()
    
    def on_item_select(self, event):
        """Handle item selection in treeview."""
        selected = self.tree.selection()
        if selected:
            item_data = self.tree.item(selected[0])
            item_id = item_data['values'][0]
            self.selected_item_id = item_id
            
            # Load item details
            item = self.catalog.db.get_item_by_id(item_id)
            if item:
                self.title_var.set(item.title)
                self.category_var.set(item.category)
                self.status_var.set(item.status)
                self.rating_var.set(str(item.rating) if item.rating > 0 else "")
                self.notes_text.delete("1.0", tk.END)
                self.notes_text.insert("1.0", item.notes)
                self.image_path_var.set(item.image_path)
                
                # Enable update/delete buttons
                self.update_btn.config(state="normal")
                self.delete_btn.config(state="normal")
                self.toggle_btn.config(state="normal")
        else:
            self.clear_form()
            self.update_btn.config(state="disabled")
            self.delete_btn.config(state="disabled")
            self.toggle_btn.config(state="disabled")
            self.selected_item_id = None
    
    def clear_form(self):
        """Clear all form fields."""
        self.title_var.set("")
        self.category_var.set("")
        self.status_var.set("Unwatched")
        self.rating_var.set("")
        self.notes_text.delete("1.0", tk.END)
        self.image_path_var.set("")
        self.selected_item_id = None
        self.update_btn.config(state="disabled")
        self.delete_btn.config(state="disabled")
        self.toggle_btn.config(state="disabled")
        
        # Deselect treeview
        for item in self.tree.selection():
            self.tree.selection_remove(item)
    
    def clear_filters(self):
        """Clear all filter fields."""
        self.search_var.set("")
        self.search_field.set("all")
        self.category_filter.set("All")
        self.status_filter.set("All")
        self.sort_var.set("title")
        self.sort_reverse.set(False)
        self.perform_search()
    
    def perform_search(self):
        """Perform search and update display."""
        self.apply_filters()
    
    def add_item(self):
        """Add a new media item."""
        try:
            title = self.title_var.get().strip()
            category = self.category_var.get()
            status = self.status_var.get()
            rating = float(self.rating_var.get()) if self.rating_var.get() else 0.0
            notes = self.notes_text.get("1.0", tk.END).strip()
            image_path = self.image_path_var.get().strip()
            
            if not title:
                messagebox.showerror("Error", "Title is required")
                return
            
            if not category:
                messagebox.showerror("Error", "Category is required")
                return
            
            item_id = self.catalog.add_item(title, category, status, rating, notes, image_path)
            if item_id:
                messagebox.showinfo("Success", f"Item '{title}' added successfully!")
                self.clear_form()
                self.refresh_display()
            else:
                messagebox.showerror("Error", "Failed to add item")
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
    
    def update_item(self):
        """Update the selected media item."""
        if not self.selected_item_id:
            messagebox.showwarning("Warning", "Please select an item first")
            return
        
        try:
            title = self.title_var.get().strip()
            category = self.category_var.get()
            status = self.status_var.get()
            rating = float(self.rating_var.get()) if self.rating_var.get() else 0.0
            notes = self.notes_text.get("1.0", tk.END).strip()
            image_path = self.image_path_var.get().strip()
            
            if not title:
                messagebox.showerror("Error", "Title is required")
                return
            
            if not category:
                messagebox.showerror("Error", "Category is required")
                return
            
            success = self.catalog.update_item(
                self.selected_item_id,
                title=title,
                category=category,
                status=status,
                rating=rating,
                notes=notes,
                image_path=image_path
            )
            
            if success:
                messagebox.showinfo("Success", "Item updated successfully!")
                self.clear_form()
                self.refresh_display()
            else:
                messagebox.showerror("Error", "Failed to update item")
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
    
    def delete_item(self):
        """Delete the selected item."""
        if not self.selected_item_id:
            messagebox.showwarning("Warning", "Please select an item first")
            return
        
        confirm = messagebox.askyesno("Confirm Delete", 
                                      "Are you sure you want to delete this item?")
        if confirm:
            success = self.catalog.delete_item(self.selected_item_id)
            if success:
                messagebox.showinfo("Success", "Item deleted successfully!")
                self.clear_form()
                self.refresh_display()
            else:
                messagebox.showerror("Error", "Failed to delete item")
    
    def toggle_status(self):
        """Toggle the status of the selected item."""
        if not self.selected_item_id:
            messagebox.showwarning("Warning", "Please select an item first")
            return
        
        success = self.catalog.toggle_status(self.selected_item_id)
        if success:
            item = self.catalog.db.get_item_by_id(self.selected_item_id)
            if item:
                self.status_var.set(item.status)
            self.refresh_display()
            messagebox.showinfo("Success", "Status toggled successfully!")
        else:
            messagebox.showerror("Error", "Failed to toggle status")
    
    def export_csv(self):
        """Export filtered items to CSV."""
        if not self.current_items:
            messagebox.showwarning("Warning", "No items to export")
            return
        
        # Ask for file location
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export to CSV"
        )
        
        if filename:
            success = self.catalog.export_to_csv(self.current_items, filename)
            if success:
                messagebox.showinfo("Success", f"Items exported to {filename}")
            else:
                messagebox.showerror("Error", "Failed to export items")
    
    def import_csv(self):
        """Import items from CSV file."""
        filename = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Import from CSV"
        )
        
        if filename:
            try:
                # Preview the file
                import csv
                with open(filename, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    header = next(reader)
                    sample = [next(reader) for _ in range(min(3, sum(1 for _ in f)))]
                
                confirm = messagebox.askyesno(
                    "Confirm Import", 
                    f"Import from '{os.path.basename(filename)}'?\n\n"
                    f"First few items:\n" + "\n".join([f"• {row[1] if len(row) > 1 else 'Untitled'}" 
                                                       for row in sample])
                )
                
                if confirm:
                    success = self.catalog.import_from_csv(filename)
                    if success:
                        messagebox.showinfo("Success", "Items imported successfully!")
                        self.clear_form()
                        self.refresh_display()
                    else:
                        messagebox.showerror("Error", "No items were imported")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import file: {e}")
    
    def browse_image(self):
        """Browse for an image file."""
        filename = filedialog.askopenfilename(
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("All files", "*.*")
            ],
            title="Select Image"
        )
        if filename:
            self.image_path_var.set(filename)
    
    def update_statistics(self):
        """Update the statistics display."""
        try:
            stats = self.catalog.get_statistics()
            
            # Build statistics string
            stats_text = f"Total: {stats['total']} items | "
            stats_text += f"Average Rating: {stats['average_rating']} | "
            
            if stats.get('category_counts'):
                cat_str = ", ".join([f"{cat}: {count}" for cat, count in stats['category_counts'].items()])
                stats_text += f"Categories: {cat_str} | "
            
            if stats.get('status_counts'):
                status_str = ", ".join([f"{status}: {count}" for status, count in stats['status_counts'].items()])
                stats_text += f"Status: {status_str}"
            
            self.stats_label.config(text=stats_text)
        except Exception as e:
            self.stats_label.config(text="Error loading statistics")
