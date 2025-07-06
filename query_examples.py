import sqlite3

def run_queries():
    """Run example queries on the Hall of Fame database"""
    conn = sqlite3.connect('mlbSql.db')
    cursor = conn.cursor()
    
    print("=== Hall of Fame Database Query Examples ===\n")
    
    # Query 1: Find all players inducted in a specific year
    print("1. Players inducted in 1982:")
    cursor.execute('''
        SELECT firstName, lastName, position, yearInducted
        FROM hof_members 
        WHERE yearInducted = 1982
        ORDER BY lastName
    ''')
    for row in cursor.fetchall():
        print(f"   {row[0]} {row[1]} - {row[2]}")
    print()
    
    # Query 2: Find players by position
    print("2. All pitchers in the Hall of Fame:")
    cursor.execute('''
        SELECT firstName, lastName, yearInducted
        FROM hof_members 
        WHERE position LIKE '%Pitcher%'
        ORDER BY yearInducted
        LIMIT 10
    ''')
    for row in cursor.fetchall():
        print(f"   {row[0]} {row[1]} ({row[2]})")
    print()
    
    # Query 3: Find players by team
    print("3. Players who played for the New York Yankees:")
    cursor.execute('''
        SELECT DISTINCT h.firstName, h.lastName, h.position, h.yearInducted
        FROM hof_members h
        JOIN player_teams pt ON h.id = pt.player_id
        JOIN teams t ON pt.team_id = t.id
        WHERE t.name LIKE '%Yankees%'
        ORDER BY h.lastName
        LIMIT 10
    ''')
    for row in cursor.fetchall():
        print(f"   {row[0]} {row[1]} - {row[2]} ({row[3]})")
    print()
    
    # Query 4: Find players with specific awards
    print("4. Players who won MVP awards:")
    cursor.execute('''
        SELECT DISTINCT h.firstName, h.lastName, a.name
        FROM hof_members h
        JOIN player_awards pa ON h.id = pa.player_id
        JOIN awards a ON pa.award_id = a.id
        WHERE a.name LIKE '%MVP%'
        ORDER BY h.lastName
        LIMIT 10
    ''')
    for row in cursor.fetchall():
        print(f"   {row[0]} {row[1]} - {row[2]}")
    print()
    
    # Query 5: Find players by nationality
    print("5. International players in the Hall of Fame:")
    cursor.execute('''
        SELECT firstName, lastName, nationality, position, yearInducted
        FROM hof_members 
        WHERE nationality != 'American'
        ORDER BY nationality, lastName
        LIMIT 10
    ''')
    for row in cursor.fetchall():
        print(f"   {row[0]} {row[1]} ({row[2]}) - {row[3]} ({row[4]})")
    print()
    
    # Query 6: Find players by era (using yearInducted as proxy)
    print("6. Players inducted in the 1960s:")
    cursor.execute('''
        SELECT firstName, lastName, position, yearInducted
        FROM hof_members 
        WHERE yearInducted BETWEEN 1960 AND 1969
        ORDER BY yearInducted
    ''')
    for row in cursor.fetchall():
        print(f"   {row[0]} {row[1]} - {row[2]} ({row[3]})")
    print()
    
    # Query 7: Count players by position
    print("7. Number of players by position:")
    cursor.execute('''
        SELECT position, COUNT(*) as count
        FROM hof_members 
        WHERE position IS NOT NULL
        GROUP BY position
        ORDER BY count DESC
        LIMIT 10
    ''')
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]} players")
    print()
    
    # Query 8: Find players with multiple teams
    print("8. Players who played for 5 or more teams:")
    cursor.execute('''
        SELECT h.firstName, h.lastName, COUNT(pt.team_id) as team_count
        FROM hof_members h
        JOIN player_teams pt ON h.id = pt.player_id
        GROUP BY h.id, h.firstName, h.lastName
        HAVING team_count >= 5
        ORDER BY team_count DESC
        LIMIT 10
    ''')
    for row in cursor.fetchall():
        print(f"   {row[0]} {row[1]}: {row[2]} teams")
    print()
    
    # Query 9: Find players by batting hand
    print("9. Left-handed batters:")
    cursor.execute('''
        SELECT h.firstName, h.lastName, ph.bat_hand
        FROM hof_members h
        JOIN player_hands ph ON h.id = ph.player_id
        WHERE ph.bat_hand LIKE '%Left%'
        ORDER BY h.lastName
        LIMIT 10
    ''')
    for row in cursor.fetchall():
        print(f"   {row[0]} {row[1]} - {row[2]}")
    print()
    
    # Query 10: Find players with specific nicknames
    print("10. Players with interesting nicknames:")
    cursor.execute('''
        SELECT firstName, lastName, nickNames
        FROM hof_members 
        WHERE nickNames IS NOT NULL AND nickNames != ''
        ORDER BY lastName
        LIMIT 10
    ''')
    for row in cursor.fetchall():
        print(f"   {row[0]} {row[1]} - \"{row[2]}\"")
    print()
    
    conn.close()

if __name__ == "__main__":
    run_queries() 