import sqlite3
from typing import List, Dict, Optional

class Database:
    """Database handler for P.R.I.S.M application"""
    
    def __init__(self, db_name: str = "prism.db"):
        """Initialize database connection"""
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            print(f"Connected to database: {self.db_name}")
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
    
    def create_tables(self):
        """Create all necessary tables with proper relationships"""
        try:
            # Playlists table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS playlists (
                    playlist_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    icon_color TEXT DEFAULT '#8B5CF6',
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Songs table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS songs (
                    song_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    artist TEXT NOT NULL,
                    duration TEXT NOT NULL,
                    file_path TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Playlist_Songs junction table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS playlist_songs (
                    ps_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    playlist_id INTEGER NOT NULL,
                    song_id INTEGER NOT NULL,
                    position INTEGER NOT NULL,
                    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (playlist_id) REFERENCES playlists(playlist_id) ON DELETE CASCADE,
                    FOREIGN KEY (song_id) REFERENCES songs(song_id) ON DELETE CASCADE,
                    UNIQUE(playlist_id, song_id)
                )
            ''')
            
            # Recently played table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS recently_played (
                    rp_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    song_id INTEGER NOT NULL,
                    played_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (song_id) REFERENCES songs(song_id) ON DELETE CASCADE
                )
            ''')
            
            self.conn.commit()
            print("Database tables created/verified successfully")
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")
    
    # Playlist Operations
    def create_playlist(self, name: str, description: str = "", icon_color: str = "#8B5CF6") -> Optional[int]:
        """Create a new playlist"""
        try:
            self.cursor.execute('''
                INSERT INTO playlists (name, description, icon_color)
                VALUES (?, ?, ?)
            ''', (name, description, icon_color))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            print(f"Playlist '{name}' already exists")
            return None
        except sqlite3.Error as e:
            print(f"Error creating playlist: {e}")
            return None
    
    def get_all_playlists(self) -> List[Dict]:
        """Retrieve all playlists with song count"""
        try:
            self.cursor.execute('''
                SELECT p.playlist_id, p.name, p.description, p.icon_color, 
                       p.created_date, COUNT(ps.song_id) as song_count
                FROM playlists p
                LEFT JOIN playlist_songs ps ON p.playlist_id = ps.playlist_id
                GROUP BY p.playlist_id
                ORDER BY p.modified_date DESC
            ''')
            
            columns = [desc[0] for desc in self.cursor.description]
            return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error retrieving playlists: {e}")
            return []
    
    def get_playlist_by_id(self, playlist_id: int) -> Optional[Dict]:
        """Get a specific playlist by ID"""
        try:
            self.cursor.execute('''
                SELECT p.*, COUNT(ps.song_id) as song_count
                FROM playlists p
                LEFT JOIN playlist_songs ps ON p.playlist_id = ps.playlist_id
                WHERE p.playlist_id = ?
                GROUP BY p.playlist_id
            ''', (playlist_id,))
            
            row = self.cursor.fetchone()
            if row:
                columns = [desc[0] for desc in self.cursor.description]
                return dict(zip(columns, row))
            return None
        except sqlite3.Error as e:
            print(f"Error retrieving playlist: {e}")
            return None
    
    def update_playlist(self, playlist_id: int, name: str = None, 
                       description: str = None, icon_color: str = None) -> bool:
        """Update playlist information"""
        try:
            updates = []
            params = []
            
            if name:
                updates.append("name = ?")
                params.append(name)
            if description is not None:
                updates.append("description = ?")
                params.append(description)
            if icon_color:
                updates.append("icon_color = ?")
                params.append(icon_color)
            
            if not updates:
                return False
            
            updates.append("modified_date = CURRENT_TIMESTAMP")
            params.append(playlist_id)
            
            query = f"UPDATE playlists SET {', '.join(updates)} WHERE playlist_id = ?"
            self.cursor.execute(query, params)
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error updating playlist: {e}")
            return False
    
    def delete_playlist(self, playlist_id: int) -> bool:
        """Delete a playlist"""
        try:
            self.cursor.execute("DELETE FROM playlists WHERE playlist_id = ?", (playlist_id,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error deleting playlist: {e}")
            return False
    
    # Song Operations
    def create_song(self, title: str, artist: str, duration: str, file_path: str = "") -> Optional[int]:
        """Add a new song"""
        try:
            self.cursor.execute('''
                INSERT INTO songs (title, artist, duration, file_path)
                VALUES (?, ?, ?, ?)
            ''', (title, artist, duration, file_path))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error creating song: {e}")
            return None
    
    def get_all_songs(self) -> List[Dict]:
        """Retrieve all songs"""
        try:
            self.cursor.execute("SELECT * FROM songs ORDER BY title")
            columns = [desc[0] for desc in self.cursor.description]
            return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error retrieving songs: {e}")
            return []
    
    def get_song_by_id(self, song_id: int) -> Optional[Dict]:
        """Get a specific song by ID"""
        try:
            self.cursor.execute("SELECT * FROM songs WHERE song_id = ?", (song_id,))
            row = self.cursor.fetchone()
            if row:
                columns = [desc[0] for desc in self.cursor.description]
                return dict(zip(columns, row))
            return None
        except sqlite3.Error as e:
            print(f"Error retrieving song: {e}")
            return None
    
    def delete_song(self, song_id: int) -> bool:
        """Delete a song"""
        try:
            self.cursor.execute("DELETE FROM songs WHERE song_id = ?", (song_id,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error deleting song: {e}")
            return False
    
    # Playlist-Song Relationship Operations
    def add_song_to_playlist(self, playlist_id: int, song_id: int) -> bool:
        """Add a song to a playlist"""
        try:
            # Get the next position
            self.cursor.execute('''
                SELECT COALESCE(MAX(position), 0) + 1 
                FROM playlist_songs 
                WHERE playlist_id = ?
            ''', (playlist_id,))
            position = self.cursor.fetchone()[0]
            
            self.cursor.execute('''
                INSERT INTO playlist_songs (playlist_id, song_id, position)
                VALUES (?, ?, ?)
            ''', (playlist_id, song_id, position))
            self.conn.commit()
            
            # Update playlist modified date
            self.cursor.execute('''
                UPDATE playlists SET modified_date = CURRENT_TIMESTAMP 
                WHERE playlist_id = ?
            ''', (playlist_id,))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            print("Song already in playlist")
            return False
        except sqlite3.Error as e:
            print(f"Error adding song to playlist: {e}")
            return False
    
    def remove_song_from_playlist(self, playlist_id: int, song_id: int) -> bool:
        """Remove a song from a playlist"""
        try:
            self.cursor.execute('''
                DELETE FROM playlist_songs 
                WHERE playlist_id = ? AND song_id = ?
            ''', (playlist_id, song_id))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error removing song from playlist: {e}")
            return False
    
    def get_playlist_songs(self, playlist_id: int) -> List[Dict]:
        """Get all songs in a playlist"""
        try:
            self.cursor.execute('''
                SELECT s.*, ps.position, ps.added_date
                FROM songs s
                JOIN playlist_songs ps ON s.song_id = ps.song_id
                WHERE ps.playlist_id = ?
                ORDER BY ps.position
            ''', (playlist_id,))
            
            columns = [desc[0] for desc in self.cursor.description]
            return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error retrieving playlist songs: {e}")
            return []
    
    # Recently Played Operations
    def add_to_recently_played(self, song_id: int) -> bool:
        """Add a song to recently played"""
        try:
            self.cursor.execute('''
                INSERT INTO recently_played (song_id)
                VALUES (?)
            ''', (song_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error adding to recently played: {e}")
            return False
    
    def get_recently_played(self, limit: int = 10) -> List[Dict]:
        """Get recently played songs"""
        try:
            self.cursor.execute('''
                SELECT s.*, rp.played_date
                FROM songs s
                JOIN recently_played rp ON s.song_id = rp.song_id
                ORDER BY rp.played_date DESC
                LIMIT ?
            ''', (limit,))
            
            columns = [desc[0] for desc in self.cursor.description]
            return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error retrieving recently played: {e}")
            return []
    
    # Search Operations
    def search_songs(self, query: str) -> List[Dict]:
        """Search songs by title or artist"""
        try:
            search_pattern = f"%{query}%"
            self.cursor.execute('''
                SELECT * FROM songs
                WHERE title LIKE ? OR artist LIKE ?
                ORDER BY title
            ''', (search_pattern, search_pattern))
            
            columns = [desc[0] for desc in self.cursor.description]
            return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error searching songs: {e}")
            return []
    
    def search_playlists(self, query: str) -> List[Dict]:
        """Search playlists by name"""
        try:
            search_pattern = f"%{query}%"
            self.cursor.execute('''
                SELECT p.*, COUNT(ps.song_id) as song_count
                FROM playlists p
                LEFT JOIN playlist_songs ps ON p.playlist_id = ps.playlist_id
                WHERE p.name LIKE ?
                GROUP BY p.playlist_id
                ORDER BY p.name
            ''', (search_pattern,))
            
            columns = [desc[0] for desc in self.cursor.description]
            return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error searching playlists: {e}")
            return []
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("Database connection closed")
    
    def __del__(self):
        """Destructor to ensure connection is closed"""
        try:
            self.close()
        except:
            pass
