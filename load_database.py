import sqlite3
import csv
import json
import re

def create_database():
    """Create the SQLite database and tables"""
    conn = sqlite3.connect('mlbSql.db')
    cursor = conn.cursor()
    
    # Create the main Hall of Fame members table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hof_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            firstName TEXT NOT NULL,
            lastName TEXT NOT NULL,
            realName TEXT,
            nickNames TEXT,
            position TEXT,
            nationality TEXT,
            race TEXT,
            yearsActive TEXT,
            birthDay TEXT,
            deathDay TEXT,
            yearInducted INTEGER,
            commentOne TEXT,
            commentTwo TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create teams table for many-to-many relationship
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')
    
    # Create player_teams junction table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS player_teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER,
            team_id INTEGER,
            is_primary BOOLEAN DEFAULT 0,
            FOREIGN KEY (player_id) REFERENCES hof_members (id),
            FOREIGN KEY (team_id) REFERENCES teams (id)
        )
    ''')
    
    # Create awards table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS awards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')
    
    # Create player_awards junction table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS player_awards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER,
            award_id INTEGER,
            FOREIGN KEY (player_id) REFERENCES hof_members (id),
            FOREIGN KEY (award_id) REFERENCES awards (id)
        )
    ''')
    
    # Create batting/fielding hands table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS player_hands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER,
            bat_hand TEXT,
            throw_hand TEXT,
            FOREIGN KEY (player_id) REFERENCES hof_members (id)
        )
    ''')
    
    conn.commit()
    return conn

def parse_list_field(field_value):
    """Parse a JSON array string into a Python list"""
    if not field_value or field_value == '':
        return []
    try:
        # Handle the case where the field is already a string representation of a list
        if field_value.startswith('[') and field_value.endswith(']'):
            return json.loads(field_value)
        return []
    except:
        return []

def load_data():
    """Load data from CSV into the database"""
    conn = create_database()
    cursor = conn.cursor()
    
    # Read CSV file
    with open('hofMembers.csv', 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        
        for row in csv_reader:
            # Insert main player data
            cursor.execute('''
                INSERT INTO hof_members 
                (firstName, lastName, realName, nickNames, position, nationality, 
                 race, yearsActive, birthDay, deathDay, yearInducted, commentOne, commentTwo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['firstName'],
                row['lastName'],
                row['realName'],
                row['nickNames'],
                row['position'],
                row['nationality'],
                row['race'],
                row['yearsActive'],
                row['birthDay'],
                row['deathDay'] if row['deathDay'] else None,
                int(row['yearInducted']) if row['yearInducted'] and row['yearInducted'].isdigit() else None,
                row['commentOne'],
                row['commentTwo']
            ))
            
            player_id = cursor.lastrowid
            
            # Handle teams
            teams = parse_list_field(row['teams'])
            primary_teams = parse_list_field(row['primaryTeam'])
            
            for team_name in teams:
                if team_name.strip():
                    # Insert team if it doesn't exist
                    cursor.execute('INSERT OR IGNORE INTO teams (name) VALUES (?)', (team_name.strip(),))
                    cursor.execute('SELECT id FROM teams WHERE name = ?', (team_name.strip(),))
                    team_id = cursor.fetchone()[0]
                    
                    # Check if this is a primary team
                    is_primary = team_name.strip() in primary_teams
                    
                    # Link player to team
                    cursor.execute('''
                        INSERT INTO player_teams (player_id, team_id, is_primary)
                        VALUES (?, ?, ?)
                    ''', (player_id, team_id, is_primary))
            
            # Handle awards
            awards = parse_list_field(row['awards'])
            for award in awards:
                if award.strip():
                    # Insert award if it doesn't exist
                    cursor.execute('INSERT OR IGNORE INTO awards (name) VALUES (?)', (award.strip(),))
                    cursor.execute('SELECT id FROM awards WHERE name = ?', (award.strip(),))
                    award_id = cursor.fetchone()[0]
                    
                    # Link player to award
                    cursor.execute('''
                        INSERT INTO player_awards (player_id, award_id)
                        VALUES (?, ?)
                    ''', (player_id, award_id))
            
            # Handle batting/throwing hands
            bat_hands = parse_list_field(row['batHand'])
            throw_hands = parse_list_field(row['throwHand'])
            
            bat_hand = ', '.join(bat_hands) if bat_hands else None
            throw_hand = ', '.join(throw_hands) if throw_hands else None
            
            if bat_hand or throw_hand:
                cursor.execute('''
                    INSERT INTO player_hands (player_id, bat_hand, throw_hand)
                    VALUES (?, ?, ?)
                ''', (player_id, bat_hand, throw_hand))
    
    conn.commit()
    conn.close()
    print("Database loaded successfully!")

def show_database_stats():
    """Show statistics about the loaded database"""
    conn = sqlite3.connect('mlbSql.db')
    cursor = conn.cursor()
    
    # Count records in each table
    cursor.execute('SELECT COUNT(*) FROM hof_members')
    player_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM teams')
    team_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM awards')
    award_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM player_teams')
    player_team_links = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM player_awards')
    player_award_links = cursor.fetchone()[0]
    
    print(f"\nDatabase Statistics:")
    print(f"Hall of Fame Members: {player_count}")
    print(f"Teams: {team_count}")
    print(f"Awards: {award_count}")
    print(f"Player-Team Relationships: {player_team_links}")
    print(f"Player-Award Relationships: {player_award_links}")
    
    # Show some sample data
    print(f"\nSample Hall of Fame Members:")
    cursor.execute('''
        SELECT firstName, lastName, position, yearInducted 
        FROM hof_members 
        ORDER BY yearInducted 
        LIMIT 5
    ''')
    for row in cursor.fetchall():
        print(f"  {row[0]} {row[1]} - {row[2]} (Inducted: {row[3]})")
    
    conn.close()

if __name__ == "__main__":
    load_data()
    show_database_stats() 