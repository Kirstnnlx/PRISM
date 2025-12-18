"""
P.R.I.S.M - Playlist Repository & Index for Sonic Media
Main Application Entry Point
"""

import tkinter as tk
from tkinter import messagebox
import sys
from database import Database
from gui import PRISMApp


def initialize_database():
    """Initialize the database and populate with sample data if empty"""
    try:
        db = Database("prism.db")
        
        playlists = db.get_all_playlists()
        
        if not playlists:
            print("Database is empty. Adding sample data...")
            
            # Create sample playlists
            sample_playlists = [
                ("Late Night Vibes", "Perfect for late night coding sessions", "#ec4899"),
                ("Morning Energy", "Start your day with energy", "#f59e0b"),
                ("Focus Flow", "Deep concentration music", "#3b82f6"),
                ("Weekend Mood", "Relaxing weekend tunes", "#10b981"),
                ("Chill Sundays", "Sunday relaxation playlist", "#8b5cf6"),
                ("Workout Beast", "High energy workout music", "#ef4444")
            ]
            
            playlist_ids = []
            for name, desc, color in sample_playlists:
                playlist_id = db.create_playlist(name, desc, color)
                if playlist_id:
                    playlist_ids.append(playlist_id)
                    print(f"Created playlist: {name}")
            
            # Create sample songs
            sample_songs = [
                ("Midnight City", "M83", "3:45"),
                ("Electric Feel", "MGMT", "4:02"),
                ("Intro", "The xx", "2:11"),
                ("Breathe", "Telepopmusik", "4:28"),
                ("Teardrop", "Massive Attack", "5:29"),
                ("Sleepwalking", "The Chain Gang of 1974", "3:47"),
                ("Sunset Lover", "Petit Biscuit", "3:36"),
                ("Feel Good Inc.", "Gorillaz", "3:41"),
                ("In the Flowers", "Animal Collective", "5:38"),
                ("House of Cards", "Radiohead", "5:28"),
                ("Crystalised", "The xx", "3:21"),
                ("Touch", "Daft Punk", "8:18"),
                ("Oblivion", "Grimes", "3:06"),
                ("Midnight", "Coldplay", "4:58"),
                ("Neon", "John Mayer", "4:03"),
                ("Strobe", "deadmau5", "10:37"),
                ("Time", "Hans Zimmer", "4:35"),
                ("Experience", "Ludovico Einaudi", "5:15"),
                ("Nuvole Bianche", "Ludovico Einaudi", "5:57"),
                ("River Flows in You", "Yiruma", "3:43"),
                ("Eye of the Tiger", "Survivor", "4:04"),
                ("Stronger", "Kanye West", "5:12"),
                ("Till I Collapse", "Eminem", "4:57"),
                ("Remember the Name", "Fort Minor", "3:50"),
                ("Thunder", "Imagine Dragons", "3:07")
            ]
            
            song_ids = []
            for title, artist, duration in sample_songs:
                song_id = db.create_song(title, artist, duration)
                if song_id:
                    song_ids.append(song_id)
                    print(f"Created song: {title} by {artist}")
            
            # Add songs to playlists
            if playlist_ids and song_ids:
                # Late Night Vibes
                for i in range(0, 4):
                    db.add_song_to_playlist(playlist_ids[0], song_ids[i])
                
                # Morning Energy
                for i in range(7, 10):
                    db.add_song_to_playlist(playlist_ids[1], song_ids[i])
                
                # Focus Flow
                for i in range(16, 20):
                    db.add_song_to_playlist(playlist_ids[2], song_ids[i])
                
                # Weekend Mood
                for i in range(4, 8):
                    db.add_song_to_playlist(playlist_ids[3], song_ids[i])
                
                # Chill Sundays
                for i in range(10, 13):
                    db.add_song_to_playlist(playlist_ids[4], song_ids[i])
                
                # Workout Beast
                for i in range(20, 25):
                    db.add_song_to_playlist(playlist_ids[5], song_ids[i])
                
                print("Sample songs added to playlists")
            
            # Add some songs to recently played
            for i in range(min(3, len(song_ids))):
                db.add_to_recently_played(song_ids[i])
            
            print("Sample data initialization complete!")
        
        return db
    
    except Exception as e:
        print(f"Error initializing database: {e}")
        messagebox.showerror("Database Error",
                           f"Failed to initialize database:\n{str(e)}")
        return None


def main():
    """Main application entry point"""
    print("=" * 60)
    print("P.R.I.S.M - Playlist Repository & Index for Sonic Media")
    print("=" * 60)
    print()
    
    # Initialize database
    print("Initializing database...")
    db = initialize_database()
    
    if not db:
        print("Failed to initialize database. Exiting...")
        sys.exit(1)
    
    print("Database initialized successfully!")
    print()
    
    # Create main window
    print("Launching GUI...")
    root = tk.Tk()
    
    # Initialize the application
    app = PRISMApp(root, db)
    
    print("Application launched successfully!")
    print("=" * 60)
    print()
    
    # Handle window close event
    def on_closing():
        """Handle application closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit P.R.I.S.M?"):
            print("Closing database connection...")
            db.close()
            print("Goodbye!")
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the GUI event loop
    root.mainloop()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        messagebox.showerror("Error", f"An unexpected error occurred:\n{str(e)}")
        sys.exit(1)
