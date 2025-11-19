# Correct repository card function - copy this into main_window.py

    def _create_repo_card(self, repo):
        """Create a GitHub-style repository card"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {self.BG_LIGHTER};
                border: 1px solid {self.HOVER_COLOR};
                border-radius: 6px;
                padding: 16px;
            }}
            QFrame:hover {{
                border-color: {self.ACCENT_BLUE};
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Repo name and link
        name_layout = QHBoxLayout()
        repo_name = QLabel(f"<a href='{repo.get('url', '#')}' style='color: {self.ACCENT_BLUE}; text-decoration: none; font-weight: 600; font-size: 15px;'>📦 {repo.get('name', 'Unknown')}</a>")
        repo_name.setOpenExternalLinks(True)
        repo_name.setTextFormat(Qt.TextFormat.RichText)
        name_layout.addWidget(repo_name)
        
        # Visibility badge
        visibility = "Public" if repo.get('private', False) == False else "Private"
        visibility_badge = QLabel(visibility)
        visibility_badge.setStyleSheet(f"""
            background-color: {self.HOVER_COLOR};
            color: {self.TEXT_SECONDARY};
            border: 1px solid {self.HOVER_COLOR};
            border-radius: 12px;
            padding: 2px 8px;
            font-size: 11px;
        """)
        visibility_badge.setFixedHeight(20)
        name_layout.addWidget(visibility_badge)
        name_layout.addStretch()
        
        layout.addLayout(name_layout)
        
        # Description
        description = repo.get('description', '')
        if description:
            desc_label = QLabel(description[:150] + ('...' if len(description) > 150 else ''))
            desc_label.setStyleSheet(f"color: {self.TEXT_SECONDARY}; font-size: 13px;")
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)
        
        # Stats row
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)
        
        # Language
        language = repo.get('language', '')
        if language:
            lang_label = QLabel(f"🔵 {language}")
            lang_label.setStyleSheet(f"color: {self.TEXT_SECONDARY}; font-size: 12px;")
            stats_layout.addWidget(lang_label)
        
        # Stars
        stars = repo.get('stars', 0)
        star_label = QLabel(f"⭐ {stars}")
        star_label.setStyleSheet(f"color: {self.TEXT_SECONDARY}; font-size: 12px;")
        stats_layout.addWidget(star_label)
        
        # Forks
        forks = repo.get('forks', 0)
        fork_label = QLabel(f"🍴 {forks}")
        fork_label.setStyleSheet(f"color: {self.TEXT_SECONDARY}; font-size: 12px;")
        stats_layout.addWidget(fork_label)
        
        # Updated date
        updated = repo.get('updated_at', '')
        if updated:
            # Parse and format date
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(updated.replace('Z', '+00:00'))
                time_ago = self._time_ago(dt)
                updated_label = QLabel(f"Updated {time_ago}")
                updated_label.setStyleSheet(f"color: {self.TEXT_SECONDARY}; font-size: 12px;")
                stats_layout.addWidget(updated_label)
            except:
                pass
        
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
        
        return card
    
    def _time_ago(self, dt):
        """Calculate time ago from datetime"""
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        diff = now - dt
        
        seconds = diff.total_seconds()
        if seconds < 60:
            return "just now"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        else:
            days = int(seconds / 86400)
            return f"{days} day{'s' if days != 1 else ''} ago"
