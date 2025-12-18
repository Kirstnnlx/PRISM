import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from database import Database
from datetime import datetime

class PRISMApp:
    """Main GUI Application for P.R.I.S.M"""
    
    def __init__(self, root, db: Database):
        self.root = root
        self.db = db
        self.current_playlist_id = None
        
        # Configure root window
        self.root.title("P.R.I.S.M - Playlist Repository & Index for Sonic Media")
        self.root.geometry("1200x700")
        self.root.configure(bg='#0f172a')
        
        # Color scheme
        self.colors = {
            'bg_primary': '#0f172a',
            'bg_secondary': '#1e293b',
            'bg_card': '#1e293b',
            'text_primary': '#ffffff',
            'text_secondary': '#94a3b8',
            'accent': '#8B5CF6',
            'hover': '#334155',
            'border': '#334155'
        }
        
        self.setup_ui()
        self.create_menu_bar()
        self.load_playlists()
    
    def format_date(self, date_str):
        """Format timestamp for display"""
        try:
            if not date_str:
                return "N/A"
            # Parse SQLite timestamp format
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%b %d, %Y %I:%M %p")
        except:
            return date_str
    
    def setup_ui(self):
        """Setup the main user interface"""
        main_container = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_container.pack(fill=tk.BOTH, expand=True)
        
        self.create_header(main_container)
        
        content_frame = tk.Frame(main_container, bg=self.colors['bg_primary'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.create_sidebar(content_frame)
        self.create_main_content(content_frame)
    
    def create_menu_bar(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Playlist", command=self.create_playlist_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="All Playlists", command=self.show_all_playlists)
        view_menu.add_command(label="All Songs", command=self.show_all_songs_view)
        view_menu.add_command(label="Recent", command=self.show_recent)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def create_header(self, parent):
        """Create header with logo, search, and new playlist button"""
        header = tk.Frame(parent, bg='#1e3a8a', height=90)
        header.pack(fill=tk.X, padx=20, pady=10)
        header.pack_propagate(False)
        
        # Logo and title
        logo_frame = tk.Frame(header, bg='#1e3a8a')
        logo_frame.pack(side=tk.LEFT, padx=15, pady=20)
        
        title_label = tk.Label(logo_frame, text="🎵 P.R.I.S.M", font=('Arial', 24, 'bold'),
                              fg='#ffffff', bg='#1e3a8a')
        title_label.pack(side=tk.LEFT)
        
        subtitle_label = tk.Label(logo_frame, text="Playlist Repository & Index for Sonic Media",
                                 font=('Arial', 10), fg='#93c5fd', bg='#1e3a8a')
        subtitle_label.pack(side=tk.LEFT, padx=10)
        
        # Search bar
        search_outer = tk.Frame(header, bg='#1e3a8a')
        search_outer.pack(side=tk.LEFT, padx=50, fill=tk.X, expand=True, pady=20)
        
        search_frame = tk.Frame(search_outer, bg='#0c1e42', highlightbackground='#3b82f6', 
                               highlightthickness=1)
        search_frame.pack(fill=tk.BOTH, expand=True)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search)
        
        search_icon = tk.Label(search_frame, text="🔍", font=('Arial', 12),
                              bg='#0c1e42', fg='#3b82f6')
        search_icon.pack(side=tk.LEFT, padx=(10, 5))
        
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=('Arial', 12),
                               bg='#0c1e42', fg='#9ca3af', insertbackground='#3b82f6',
                               relief=tk.FLAT, bd=0)
        self.search_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15), pady=10)
        self.search_entry.insert(0, "Search playlists...")
        
        def on_focus_in(e):
            if self.search_entry.get() == "Search playlists...":
                self.search_entry.delete(0, tk.END)
                self.search_entry.config(fg='#ffffff')
        
        def on_focus_out(e):
            if not self.search_entry.get():
                self.search_entry.insert(0, "Search playlists...")
                self.search_entry.config(fg='#9ca3af')
        
        self.search_entry.bind('<FocusIn>', on_focus_in)
        self.search_entry.bind('<FocusOut>', on_focus_out)
        
        # New Playlist button
        button_frame = tk.Frame(header, bg='#1e3a8a')
        button_frame.pack(side=tk.RIGHT, padx=15, pady=20)
        
        new_btn = tk.Button(button_frame, text="+ New Playlist", font=('Arial', 12, 'bold'),
                           bg='#3b82f6', fg='#ffffff', activebackground='#2563eb',
                           activeforeground='#ffffff', relief=tk.FLAT, bd=0, padx=25, pady=12,
                           cursor='hand2', command=self.create_playlist_dialog)
        new_btn.pack()
        
        new_btn.bind('<Enter>', lambda e: new_btn.config(bg='#2563eb'))
        new_btn.bind('<Leave>', lambda e: new_btn.config(bg='#3b82f6'))
    
    def create_sidebar(self, parent):
        """Create sidebar with navigation"""
        sidebar = tk.Frame(parent, bg=self.colors['bg_secondary'], width=220)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        sidebar.pack_propagate(False)
        
        # Library section
        library_label = tk.Label(sidebar, text="Library", font=('Arial', 16, 'bold'),
                                bg=self.colors['bg_secondary'], fg=self.colors['text_primary'],
                                anchor='w')
        library_label.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        # Navigation buttons
        nav_items = [
            ("📋 All Playlists", self.show_all_playlists),
            ("🎵 All Songs", self.show_all_songs_view),
            ("🕐 Recent", self.show_recent)
        ]
        
        for text, command in nav_items:
            btn = tk.Button(sidebar, text=text, font=('Arial', 11),
                           bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'],
                           relief=tk.FLAT, bd=0, anchor='w', padx=20, pady=10,
                           cursor='hand2', command=command)
            btn.pack(fill=tk.X)
            btn.bind('<Enter>', lambda e, b=btn: b.config(bg=self.colors['hover']))
            btn.bind('<Leave>', lambda e, b=btn: b.config(bg=self.colors['bg_secondary']))
        
        # Recently Played section
        recent_label = tk.Label(sidebar, text="Recently Played", font=('Arial', 14, 'bold'),
                               bg=self.colors['bg_secondary'], fg=self.colors['text_primary'],
                               anchor='w')
        recent_label.pack(fill=tk.X, padx=20, pady=(30, 10))
        
        self.recent_frame = tk.Frame(sidebar, bg=self.colors['bg_secondary'])
        self.recent_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        
        self.load_recently_played()
    
    def create_main_content(self, parent):
        """Create main content area with playlist grid"""
        content = tk.Frame(parent, bg=self.colors['bg_primary'])
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Title section
        title_frame = tk.Frame(content, bg=self.colors['bg_primary'])
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.content_title = tk.Label(title_frame, text="Your Playlists",
                                      font=('Arial', 28, 'bold'),
                                      bg=self.colors['bg_primary'],
                                      fg=self.colors['text_primary'], anchor='w')
        self.content_title.pack(side=tk.LEFT)
        
        self.content_subtitle = tk.Label(title_frame, text="Organize and explore your sonic collections",
                                         font=('Arial', 12), bg=self.colors['bg_primary'],
                                         fg=self.colors['text_secondary'], anchor='w')
        self.content_subtitle.pack(side=tk.LEFT, padx=20)
        
        # Scrollable content area
        canvas_frame = tk.Frame(content, bg=self.colors['bg_primary'])
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(canvas_frame, bg=self.colors['bg_primary'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        
        self.main_content_frame = tk.Frame(canvas, bg=self.colors['bg_primary'])
        
        canvas.create_window((0, 0), window=self.main_content_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.main_content_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    
    def create_playlist_card(self, parent, playlist_data, row, col):
        """Create a playlist card widget"""
        card = tk.Frame(parent, bg=self.colors['bg_card'], width=200, height=250, cursor='hand2')
        card.grid(row=row, column=col, padx=15, pady=15, sticky='nsew')
        card.grid_propagate(False)
        card.pack_propagate(False)
        
        # Icon
        icon_colors = ['#ec4899', '#f59e0b', '#3b82f6', '#10b981', '#8b5cf6', '#ef4444']
        color = playlist_data.get('icon_color', icon_colors[playlist_data['playlist_id'] % len(icon_colors)])
        
        icon_frame = tk.Frame(card, bg=color, width=120, height=120)
        icon_frame.pack(pady=20)
        icon_frame.pack_propagate(False)
        
        icons = ['🎵', '🎸', '🎧', '🎹', '🎺', '🎼', '🎤', '🥁']
        icon_emoji = icons[playlist_data['playlist_id'] % len(icons)]
        
        icon_label = tk.Label(icon_frame, text=icon_emoji, font=('Arial', 48), bg=color, fg='white')
        icon_label.pack(expand=True)
        
        # Playlist name
        name_label = tk.Label(card, text=playlist_data['name'], font=('Arial', 14, 'bold'),
                             bg=self.colors['bg_card'], fg=self.colors['text_primary'],
                             wraplength=180)
        name_label.pack(pady=(5, 2))
        
        # Song count
        count_label = tk.Label(card, text=f"{playlist_data['song_count']} songs",
                              font=('Arial', 10), bg=self.colors['bg_card'],
                              fg=self.colors['text_secondary'])
        count_label.pack()
        
        # Bind click events
        playlist_id = playlist_data['playlist_id']
        for widget in [card, icon_frame, icon_label, name_label, count_label]:
            widget.bind('<Button-1>', lambda e, pid=playlist_id: self.open_playlist(pid))
            widget.bind('<Button-3>', lambda e, pid=playlist_id: self.show_playlist_menu(e, pid))
        
        # Hover effect
        def on_enter(e):
            card.config(bg=self.colors['hover'])
            name_label.config(bg=self.colors['hover'])
            count_label.config(bg=self.colors['hover'])
        
        def on_leave(e):
            card.config(bg=self.colors['bg_card'])
            name_label.config(bg=self.colors['bg_card'])
            count_label.config(bg=self.colors['bg_card'])
        
        card.bind('<Enter>', on_enter)
        card.bind('<Leave>', on_leave)
    
    def load_playlists(self):
        """Load and display all playlists"""
        for widget in self.main_content_frame.winfo_children():
            widget.destroy()
        
        playlists = self.db.get_all_playlists()
        
        if not playlists:
            no_data_label = tk.Label(self.main_content_frame,
                                     text="No playlists yet. Click '+ New Playlist' to create one!",
                                     font=('Arial', 14), bg=self.colors['bg_primary'],
                                     fg=self.colors['text_secondary'])
            no_data_label.pack(pady=50)
            return
        
        for idx, playlist in enumerate(playlists):
            row = idx // 3
            col = idx % 3
            self.create_playlist_card(self.main_content_frame, playlist, row, col)
    
    def load_recently_played(self):
        """Load recently played songs in sidebar"""
        for widget in self.recent_frame.winfo_children():
            widget.destroy()
        
        recent_songs = self.db.get_recently_played(3)
        
        if not recent_songs:
            no_recent = tk.Label(self.recent_frame, text="No recent songs", font=('Arial', 9),
                                bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'])
            no_recent.pack(pady=10)
            return
        
        for song in recent_songs:
            song_frame = tk.Frame(self.recent_frame, bg=self.colors['bg_secondary'], cursor='hand2')
            song_frame.pack(fill=tk.X, pady=5, padx=10)
            
            play_label = tk.Label(song_frame, text="▶", font=('Arial', 10),
                                 bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'])
            play_label.pack(side=tk.LEFT, padx=5)
            
            info_frame = tk.Frame(song_frame, bg=self.colors['bg_secondary'])
            info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            title_text = song['title']
            if len(title_text) > 18:
                title_text = title_text[:18] + '...'
            
            title_label = tk.Label(info_frame, text=title_text, font=('Arial', 10),
                                  bg=self.colors['bg_secondary'], fg=self.colors['text_primary'],
                                  anchor='w')
            title_label.pack(anchor='w')
            
            artist_label = tk.Label(info_frame, text=song['artist'][:18] + ('...' if len(song['artist']) > 18 else ''),
                                   font=('Arial', 8), bg=self.colors['bg_secondary'],
                                   fg=self.colors['text_secondary'], anchor='w')
            artist_label.pack(anchor='w')
            
            song_id = song['song_id']
            song_frame.bind('<Button-1>', lambda e, sid=song_id: self.play_song(sid))
    
    def show_all_songs_view(self):
        """Display all songs in the main content area"""
        self.content_title.config(text="All Songs")
        self.content_subtitle.config(text="Browse your complete music library")
        
        for widget in self.main_content_frame.winfo_children():
            widget.destroy()
        
        all_songs = self.db.get_all_songs()
        
        if not all_songs:
            no_songs = tk.Label(self.main_content_frame,
                               text="No songs in library. Add songs through playlists!",
                               font=('Arial', 14), bg=self.colors['bg_primary'],
                               fg=self.colors['text_secondary'])
            no_songs.pack(pady=50)
            return
        
        # Control bar
        control_frame = tk.Frame(self.main_content_frame, bg=self.colors['bg_primary'])
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        count_label = tk.Label(control_frame, text=f"Total: {len(all_songs)} songs",
                              font=('Arial', 12, 'bold'), bg=self.colors['bg_primary'],
                              fg=self.colors['text_secondary'])
        count_label.pack(side=tk.LEFT)
        
        # Search bar for songs
        search_frame = tk.Frame(control_frame, bg=self.colors['bg_card'],
                               highlightbackground=self.colors['border'], highlightthickness=1)
        search_frame.pack(side=tk.RIGHT)
        
        song_search_var = tk.StringVar()
        
        search_icon = tk.Label(search_frame, text="🔍", font=('Arial', 10),
                              bg=self.colors['bg_card'], fg=self.colors['text_secondary'])
        search_icon.pack(side=tk.LEFT, padx=(8, 3))
        
        search_entry = tk.Entry(search_frame, textvariable=song_search_var, font=('Arial', 11),
                               bg=self.colors['bg_card'], fg=self.colors['text_primary'],
                               insertbackground=self.colors['accent'], relief=tk.FLAT, bd=0, width=25)
        search_entry.pack(side=tk.LEFT, padx=(0, 8), pady=6)
        
        # Table frame
        table_frame = tk.Frame(self.main_content_frame, bg=self.colors['bg_primary'])
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Style configuration
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Songs.Treeview",
                       background=self.colors['bg_card'],
                       foreground=self.colors['text_primary'],
                       fieldbackground=self.colors['bg_card'],
                       borderwidth=0,
                       rowheight=35)
        style.configure("Songs.Treeview.Heading",
                       background=self.colors['bg_secondary'],
                       foreground=self.colors['text_primary'],
                       borderwidth=0,
                       relief='flat')
        style.map('Songs.Treeview',
                 background=[('selected', self.colors['accent'])])
        
        # Create treeview with created_date column
        columns = ('ID', 'Title', 'Artist', 'Duration', 'Added')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings',
                           style="Songs.Treeview")
        
        tree.heading('ID', text='ID')
        tree.heading('Title', text='Title')
        tree.heading('Artist', text='Artist')
        tree.heading('Duration', text='Duration')
        tree.heading('Added', text='Date Added')
        
        tree.column('ID', width=60, anchor='center')
        tree.column('Title', width=300)
        tree.column('Artist', width=200)
        tree.column('Duration', width=100, anchor='center')
        tree.column('Added', width=180, anchor='center')
        
        def populate_tree(songs):
            tree.delete(*tree.get_children())
            for song in songs:
                formatted_date = self.format_date(song.get('created_date', ''))
                tree.insert('', tk.END,
                           values=(song['song_id'], song['title'],
                                  song['artist'], song['duration'], formatted_date),
                           tags=(song['song_id'],))
        
        def search_songs(*args):
            query = song_search_var.get().strip()
            if query:
                results = self.db.search_songs(query)
                populate_tree(results)
            else:
                populate_tree(all_songs)
        
        song_search_var.trace('w', search_songs)
        
        populate_tree(all_songs)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Context menu
        def show_context_menu(event):
            row_id = tree.identify_row(event.y)
            if row_id:
                tree.selection_set(row_id)
                item = tree.selection()
                if item:
                    menu = tk.Menu(self.root, tearoff=0)
                    song_id = int(tree.item(item)['tags'][0])
                    menu.add_command(label="▶ Play Song", command=lambda: self.play_song(song_id))
                    menu.add_separator()
                    menu.add_command(label="🗑 Delete Song", command=lambda: self.delete_song_confirm(song_id))
                    menu.post(event.x_root, event.y_root)
        
        tree.bind('<Button-3>', show_context_menu)
        tree.bind('<Double-Button-1>',
                 lambda e: self.play_song(int(tree.item(tree.selection()[0])['tags'][0])) if tree.selection() else None)
    
    def create_playlist_dialog(self):
        """Dialog to create a new playlist"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Create New Playlist")
        dialog.geometry("400x250")
        dialog.configure(bg=self.colors['bg_secondary'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        title_label = tk.Label(dialog, text="Create New Playlist", font=('Arial', 16, 'bold'),
                              bg=self.colors['bg_secondary'], fg=self.colors['text_primary'])
        title_label.pack(pady=20)
        
        # Name input
        name_label = tk.Label(dialog, text="Playlist Name:", font=('Arial', 11),
                             bg=self.colors['bg_secondary'], fg=self.colors['text_primary'])
        name_label.pack(anchor='w', padx=30)
        
        name_entry = tk.Entry(dialog, font=('Arial', 12), bg=self.colors['bg_primary'],
                             fg=self.colors['text_primary'], insertbackground=self.colors['text_primary'])
        name_entry.pack(fill=tk.X, padx=30, pady=5)
        name_entry.focus()
        
        # Description input
        desc_label = tk.Label(dialog, text="Description (optional):", font=('Arial', 11),
                             bg=self.colors['bg_secondary'], fg=self.colors['text_primary'])
        desc_label.pack(anchor='w', padx=30, pady=(10, 0))
        
        desc_entry = tk.Entry(dialog, font=('Arial', 12), bg=self.colors['bg_primary'],
                             fg=self.colors['text_primary'], insertbackground=self.colors['text_primary'])
        desc_entry.pack(fill=tk.X, padx=30, pady=5)
        
        # Buttons
        btn_frame = tk.Frame(dialog, bg=self.colors['bg_secondary'])
        btn_frame.pack(pady=20)
        
        def create():
            name = name_entry.get().strip()
            description = desc_entry.get().strip()
            
            if not name:
                messagebox.showwarning("Invalid Input", "Please enter a playlist name")
                return
            
            playlist_id = self.db.create_playlist(name, description)
            if playlist_id:
                messagebox.showinfo("Success", f"Playlist '{name}' created successfully!")
                self.load_playlists()
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to create playlist. Name might already exist.")
        
        create_btn = tk.Button(btn_frame, text="Create", font=('Arial', 11, 'bold'),
                              bg=self.colors['accent'], fg=self.colors['text_primary'],
                              padx=20, pady=5, command=create, cursor='hand2')
        create_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(btn_frame, text="Cancel", font=('Arial', 11),
                              bg=self.colors['bg_card'], fg=self.colors['text_primary'],
                              padx=20, pady=5, command=dialog.destroy, cursor='hand2')
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        dialog.bind('<Return>', lambda e: create())
    
    def open_playlist(self, playlist_id):
        """Open a playlist and show its songs"""
        self.current_playlist_id = playlist_id
        playlist = self.db.get_playlist_by_id(playlist_id)
        
        if not playlist:
            messagebox.showerror("Error", "Playlist not found")
            return
        
        playlist_window = tk.Toplevel(self.root)
        playlist_window.title(f"P.R.I.S.M - {playlist['name']}")
        playlist_window.geometry("1050x650")
        playlist_window.configure(bg=self.colors['bg_primary'])
        
        # Center window
        playlist_window.update_idletasks()
        x = (playlist_window.winfo_screenwidth() // 2) - (playlist_window.winfo_width() // 2)
        y = (playlist_window.winfo_screenheight() // 2) - (playlist_window.winfo_height() // 2)
        playlist_window.geometry(f"+{x}+{y}")
        
        # Header
        header = tk.Frame(playlist_window, bg=self.colors['bg_secondary'])
        header.pack(fill=tk.X, padx=20, pady=20)
        
        # Left side - Title and info
        title_container = tk.Frame(header, bg=self.colors['bg_secondary'])
        title_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        title = tk.Label(title_container, text=playlist['name'], font=('Arial', 24, 'bold'),
                        bg=self.colors['bg_secondary'], fg=self.colors['text_primary'],
                        anchor='w')
        title.pack(anchor='w', padx=10)
        
        # Description and metadata in a sub-frame
        info_frame = tk.Frame(title_container, bg=self.colors['bg_secondary'])
        info_frame.pack(anchor='w', padx=10, pady=(5, 0))
        
        if playlist['description']:
            desc = tk.Label(info_frame, text=playlist['description'],
                           font=('Arial', 11), bg=self.colors['bg_secondary'],
                           fg=self.colors['text_secondary'], anchor='w')
            desc.pack(side=tk.LEFT, padx=(0, 15))
            
            separator = tk.Label(info_frame, text="•", font=('Arial', 11),
                                bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'])
            separator.pack(side=tk.LEFT, padx=5)
        
        count = tk.Label(info_frame, text=f"{playlist['song_count']} songs",
                        font=('Arial', 11), bg=self.colors['bg_secondary'],
                        fg=self.colors['text_secondary'])
        count.pack(side=tk.LEFT)
        
        # Show created and modified dates
        date_info_frame = tk.Frame(title_container, bg=self.colors['bg_secondary'])
        date_info_frame.pack(anchor='w', padx=10, pady=(3, 0))
        
        created_text = f"Created: {self.format_date(playlist.get('created_date', ''))}"
        modified_text = f"Modified: {self.format_date(playlist.get('modified_date', ''))}"
        
        dates_label = tk.Label(date_info_frame, 
                              text=f"{created_text}  •  {modified_text}",
                              font=('Arial', 9), bg=self.colors['bg_secondary'],
                              fg=self.colors['text_secondary'])
        dates_label.pack(side=tk.LEFT)
        
        # Right side - Add button
        add_song_btn = tk.Button(header, text="+ Add Song", font=('Arial', 11),
                                bg=self.colors['accent'], fg=self.colors['text_primary'],
                                cursor='hand2', padx=20, pady=8,
                                command=lambda: self.add_song_dialog(playlist_id, playlist_window))
        add_song_btn.pack(side=tk.RIGHT, padx=5)
        
        # Songs list - Container with consistent background
        songs_container = tk.Frame(playlist_window, bg=self.colors['bg_card'])
        songs_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        songs_frame = tk.Frame(songs_container, bg=self.colors['bg_card'])
        songs_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure style for this specific treeview
        style = ttk.Style()
        style.theme_use('default')
        
        # Create unique style name to avoid conflicts
        playlist_style = f"Playlist{playlist_id}.Treeview"
        
        style.configure(playlist_style,
                       background=self.colors['bg_card'],
                       foreground=self.colors['text_primary'],
                       fieldbackground=self.colors['bg_card'],
                       borderwidth=0,
                       rowheight=35)
        style.configure(f"{playlist_style}.Heading",
                       background=self.colors['bg_secondary'],
                       foreground=self.colors['text_primary'],
                       borderwidth=0,
                       relief='flat')
        style.map(playlist_style,
                 background=[('selected', self.colors['accent'])],
                 foreground=[('selected', self.colors['text_primary'])])
        
        style.layout(playlist_style, [('Treeview.treearea', {'sticky': 'nswe'})])
        
        columns = ('ID', 'Title', 'Artist', 'Duration', 'Date Added')
        tree = ttk.Treeview(songs_frame, columns=columns, show='headings',
                           height=15, style=playlist_style)
        
        tree.heading('ID', text='ID')
        tree.heading('Title', text='Title')
        tree.heading('Artist', text='Artist')
        tree.heading('Duration', text='Duration')
        tree.heading('Date Added', text='Date Added')
        
        tree.column('ID', width=50, anchor='center')
        tree.column('Title', width=300)
        tree.column('Artist', width=200)
        tree.column('Duration', width=100, anchor='center')
        tree.column('Date Added', width=180, anchor='center')
        
        songs = self.db.get_playlist_songs(playlist_id)
        
        if not songs:
            no_songs = tk.Label(songs_container, text="No songs in this playlist yet. Click '+ Add Song' to add some!",
                              font=('Arial', 12), bg=self.colors['bg_card'],
                              fg=self.colors['text_secondary'])
            no_songs.pack(pady=50, fill=tk.BOTH, expand=True)
        else:
            for song in songs:
                formatted_date = self.format_date(song.get('added_date', ''))
                tree.insert('', tk.END, values=(song['song_id'], song['title'],
                                               song['artist'], song['duration'], formatted_date),
                           tags=(song['song_id'],))
            
            scrollbar = ttk.Scrollbar(songs_frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            def show_song_context_menu(event):
                item = tree.selection()
                if item:
                    menu = tk.Menu(playlist_window, tearoff=0)
                    menu.add_command(label="Play Song",
                                   command=lambda: self.play_song(int(tree.item(item)['tags'][0])))
                    menu.add_separator()
                    menu.add_command(label="Remove from Playlist",
                                   command=lambda: self.remove_song_from_playlist(
                                       playlist_id, int(tree.item(item)['tags'][0]), playlist_window))
                    menu.post(event.x_root, event.y_root)
            
            tree.bind('<Button-3>', show_song_context_menu)
            tree.bind('<Double-Button-1>', lambda e: self.play_song(int(tree.item(tree.selection()[0])['tags'][0])) if tree.selection() else None)
    
    def add_song_dialog(self, playlist_id, parent_window):
        """Dialog to add a song to playlist"""
        dialog = tk.Toplevel(parent_window)
        dialog.title("Add Song")
        dialog.geometry("450x350")
        dialog.configure(bg=self.colors['bg_secondary'])
        dialog.transient(parent_window)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        title_label = tk.Label(dialog, text="Add New Song", font=('Arial', 16, 'bold'),
                              bg=self.colors['bg_secondary'], fg=self.colors['text_primary'])
        title_label.pack(pady=20)
        
        fields = [
            ("Song Title:", "title"),
            ("Artist:", "artist"),
            ("Duration (MM:SS):", "duration"),
            ("File Path (optional):", "path")
        ]
        
        entries = {}
        for label_text, key in fields:
            label = tk.Label(dialog, text=label_text, font=('Arial', 11),
                           bg=self.colors['bg_secondary'], fg=self.colors['text_primary'])
            label.pack(anchor='w', padx=30, pady=(5, 0))
            
            entry = tk.Entry(dialog, font=('Arial', 11), bg=self.colors['bg_primary'],
                           fg=self.colors['text_primary'], insertbackground=self.colors['text_primary'])
            entry.pack(fill=tk.X, padx=30, pady=3)
            entries[key] = entry
        
        entries['title'].focus()
        
        def add_song():
            title = entries['title'].get().strip()
            artist = entries['artist'].get().strip()
            duration = entries['duration'].get().strip()
            path = entries['path'].get().strip()
            
            if not all([title, artist, duration]):
                messagebox.showwarning("Invalid Input", "Please fill in all required fields")
                return
            
            song_id = self.db.create_song(title, artist, duration, path)
            if song_id:
                if self.db.add_song_to_playlist(playlist_id, song_id):
                    messagebox.showinfo("Success", f"Song added successfully!")
                    dialog.destroy()
                    parent_window.destroy()
                    self.open_playlist(playlist_id)
                else:
                    messagebox.showerror("Error", "Failed to add song to playlist")
            else:
                messagebox.showerror("Error", "Failed to create song")
        
        btn_frame = tk.Frame(dialog, bg=self.colors['bg_secondary'])
        btn_frame.pack(pady=15)
        
        add_btn = tk.Button(btn_frame, text="Add Song", font=('Arial', 11, 'bold'),
                           bg=self.colors['accent'], fg=self.colors['text_primary'],
                           padx=20, pady=5, command=add_song, cursor='hand2')
        add_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(btn_frame, text="Cancel", font=('Arial', 11),
                              bg=self.colors['bg_card'], fg=self.colors['text_primary'],
                              padx=20, pady=5, command=dialog.destroy, cursor='hand2')
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        dialog.bind('<Return>', lambda e: add_song())
    
    def play_song(self, song_id):
        """Play a song (add to recently played)"""
        song = self.db.get_song_by_id(song_id)
        if song:
            self.db.add_to_recently_played(song_id)
            self.load_recently_played()
            messagebox.showinfo("Now Playing", f"🎵 {song['title']}\n🎤 {song['artist']}\n⏱ {song['duration']}")
    
    def remove_song_from_playlist(self, playlist_id, song_id, parent_window):
        """Remove a song from playlist"""
        if messagebox.askyesno("Confirm", "Remove this song from the playlist?"):
            if self.db.remove_song_from_playlist(playlist_id, song_id):
                messagebox.showinfo("Success", "Song removed from playlist")
                parent_window.destroy()
                self.open_playlist(playlist_id)
            else:
                messagebox.showerror("Error", "Failed to remove song")
    
    def delete_song_confirm(self, song_id):
        """Delete a song from the database"""
        if messagebox.askyesno("Confirm Delete", "Delete this song? It will be removed from all playlists."):
            if self.db.delete_song(song_id):
                messagebox.showinfo("Success", "Song deleted successfully!")
                self.show_all_songs_view()
            else:
                messagebox.showerror("Error", "Failed to delete song")
    
    def show_playlist_menu(self, event, playlist_id):
        """Show context menu for playlist"""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Open", command=lambda: self.open_playlist(playlist_id))
        menu.add_command(label="Rename", command=lambda: self.rename_playlist(playlist_id))
        menu.add_separator()
        menu.add_command(label="Delete", command=lambda: self.delete_playlist(playlist_id))
        menu.post(event.x_root, event.y_root)
    
    def rename_playlist(self, playlist_id):
        """Rename a playlist"""
        playlist = self.db.get_playlist_by_id(playlist_id)
        if not playlist:
            return
        
        new_name = simpledialog.askstring("Rename Playlist", "Enter new name:",
                                         initialvalue=playlist['name'])
        if new_name and new_name.strip():
            if self.db.update_playlist(playlist_id, name=new_name.strip()):
                messagebox.showinfo("Success", "Playlist renamed successfully!")
                self.load_playlists()
            else:
                messagebox.showerror("Error", "Failed to rename playlist")
    
    def delete_playlist(self, playlist_id):
        """Delete a playlist"""
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this playlist?"):
            if self.db.delete_playlist(playlist_id):
                messagebox.showinfo("Success", "Playlist deleted successfully!")
                self.load_playlists()
            else:
                messagebox.showerror("Error", "Failed to delete playlist")
    
    def on_search(self, *args):
        """Handle search input"""
        query = self.search_var.get()
        if query and query != "Search playlists...":
            playlists = self.db.search_playlists(query)
            self.display_search_results(playlists)
        else:
            self.load_playlists()
    
    def display_search_results(self, playlists):
        """Display search results"""
        for widget in self.main_content_frame.winfo_children():
            widget.destroy()
        
        if not playlists:
            no_results = tk.Label(self.main_content_frame, text="No playlists found",
                                 font=('Arial', 14), bg=self.colors['bg_primary'],
                                 fg=self.colors['text_secondary'])
            no_results.pack(pady=50)
            return
        
        for idx, playlist in enumerate(playlists):
            row = idx // 3
            col = idx % 3
            self.create_playlist_card(self.main_content_frame, playlist, row, col)
    
    def show_all_playlists(self):
        """Show all playlists"""
        self.content_title.config(text="Your Playlists")
        self.content_subtitle.config(text="Organize and explore your sonic collections")
        self.load_playlists()
    
    def show_recent(self):
        """Show recently modified playlists"""
        self.content_title.config(text="Recent Activity")
        self.content_subtitle.config(text="Recently updated playlists")
        
        for widget in self.main_content_frame.winfo_children():
            widget.destroy()
        
        playlists = self.db.get_all_playlists()
        recent = playlists[:6]
        
        if not recent:
            no_data = tk.Label(self.main_content_frame, text="No recent activity",
                              font=('Arial', 14), bg=self.colors['bg_primary'],
                              fg=self.colors['text_secondary'])
            no_data.pack(pady=50)
            return
        
        for idx, playlist in enumerate(recent):
            row = idx // 3
            col = idx % 3
            self.create_playlist_card(self.main_content_frame, playlist, row, col)
    
    def show_about(self):
        """Show about dialog"""
        about_window = tk.Toplevel(self.root)
        about_window.title("About P.R.I.S.M")
        about_window.geometry("450x350")
        about_window.configure(bg=self.colors['bg_primary'])
        about_window.resizable(False, False)
        
        about_window.update_idletasks()
        x = (about_window.winfo_screenwidth() // 2) - (about_window.winfo_width() // 2)
        y = (about_window.winfo_screenheight() // 2) - (about_window.winfo_height() // 2)
        about_window.geometry(f"+{x}+{y}")
        
        logo_label = tk.Label(about_window, text="🎵", font=('Arial', 60),
                             bg=self.colors['bg_primary'])
        logo_label.pack(pady=20)
        
        title = tk.Label(about_window, text="P.R.I.S.M", font=('Arial', 24, 'bold'),
                        bg=self.colors['bg_primary'], fg=self.colors['text_primary'])
        title.pack()
        
        subtitle = tk.Label(about_window,
                           text="Playlist Repository & Index for Sonic Media",
                           font=('Arial', 11), bg=self.colors['bg_primary'],
                           fg=self.colors['text_secondary'])
        subtitle.pack(pady=5)
        
        version = tk.Label(about_window, text="Version 1.0.0", font=('Arial', 10),
                          bg=self.colors['bg_primary'], fg=self.colors['text_secondary'])
        version.pack(pady=10)
        
        desc = tk.Label(about_window,
                       text="A modern playlist management system\n"
                            "for organizing your music collection.\n\n"
                            "Built with Python and Tkinter\n"
                            "Database: SQLite3",
                       font=('Arial', 10), bg=self.colors['bg_primary'],
                       fg=self.colors['text_secondary'], justify='center')
        desc.pack(pady=10)
        
        close_btn = tk.Button(about_window, text="Close", font=('Arial', 11),
                             bg=self.colors['accent'], fg=self.colors['text_primary'],
                             padx=30, pady=8, cursor='hand2',
                             command=about_window.destroy)
        close_btn.pack(pady=20)
