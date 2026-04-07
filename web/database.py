import sqlite3
import os

DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "leaderboard.db"))

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS PlayerStats (
                in_game_name TEXT PRIMARY KEY,
                frags INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0,
                matches_played INTEGER DEFAULT 0
            )
        ''')
        try:
            c.execute('ALTER TABLE PlayerStats ADD COLUMN deaths INTEGER DEFAULT 0')
        except sqlite3.OperationalError:
            pass
            
        # Phase 1: Modern Temporal Event-Sourcing Database
        c.execute('''
            CREATE TABLE IF NOT EXISTS PlayerMatchLogs (
                session_id TEXT PRIMARY KEY,
                in_game_name TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                frags INTEGER DEFAULT 0,
                deaths INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0,
                play_time_seconds INTEGER DEFAULT 0,
                opponents INTEGER DEFAULT 0
            )
        ''')
        
        # Seamless migration protecting older matches dynamically into the new engine matrix
        c.execute("SELECT COUNT(*) FROM PlayerMatchLogs")
        if c.fetchone()[0] == 0:
            c.execute("""
                INSERT INTO PlayerMatchLogs (session_id, in_game_name, frags, deaths, wins, play_time_seconds)
                SELECT in_game_name || '_legacy', in_game_name, frags, deaths, wins, 0 FROM PlayerStats
            """)

def start_player_session(session_id: str, name: str, base_frags: int, opponents: int):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO PlayerMatchLogs (session_id, in_game_name, frags, opponents)
            VALUES (?, ?, ?, ?)
        ''', (session_id, name, base_frags, opponents))

def update_live_session(session_id: str, delta_frags: int, delta_time_sec: int):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''
            UPDATE PlayerMatchLogs SET 
                frags = frags + ?,
                play_time_seconds = play_time_seconds + ?
            WHERE session_id = ?
        ''', (delta_frags, delta_time_sec, session_id))

def update_session_match_end(session_id: str, deaths: int, is_win: bool):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        win_val = 1 if is_win else 0
        c.execute('''
            UPDATE PlayerMatchLogs SET 
                deaths = deaths + ?,
                wins = wins + ?
            WHERE session_id = ?
        ''', (deaths, win_val, session_id))

def get_leaderboard(timeframe: str = "all_time"):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        
        query = """
            SELECT in_game_name, 
                   SUM(frags) as t_frags, 
                   SUM(deaths) as t_deaths, 
                   SUM(wins) as t_wins, 
                   COUNT(*) as t_matches,
                   SUM(play_time_seconds) as t_time,
                   MAX(opponents) as t_opps
            FROM PlayerMatchLogs
        """
        
        if timeframe == "day":
            query += " WHERE timestamp > datetime('now', '-1 day')"
        elif timeframe == "week":
            query += " WHERE timestamp > datetime('now', '-7 days')"
        elif timeframe == "month":
            query += " WHERE timestamp > datetime('now', '-30 days')"
        elif timeframe == "year":
            query += " WHERE timestamp > datetime('now', '-365 days')"
            
        query += " GROUP BY in_game_name ORDER BY t_frags DESC LIMIT 50"
        
        c.execute(query)
        results = c.fetchall()
    
    output = []
    for row in results:
        f = row[1] if row[1] else 0
        secs = row[5] if row[5] else 0
        minutes = secs / 60.0
        eff = 0
        if minutes > 0:
            eff = round(f / minutes, 2)
            
        output.append({
            "name": row[0], 
            "frags": f, 
            "deaths": row[2] if row[2] else 0, 
            "wins": row[3] if row[3] else 0, 
            "matches": row[4] if row[4] else 0,
            "play_time": secs,
            "efficiency": eff
        })
    return output
