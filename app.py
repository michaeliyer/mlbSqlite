#!/usr/bin/env python3
"""
MLB Hall of Fame Database Web Application
A Flask-based web interface for browsing MLB Hall of Fame data
"""

import sqlite3
import os
from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

def get_db_connection():
    """Create a database connection"""
    conn = sqlite3.connect('mlbSql.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    """Home page with database statistics"""
    conn = get_db_connection()
    
    # Get basic statistics
    stats = {}
    
    # Total players
    cursor = conn.execute('SELECT COUNT(*) as count FROM hof_members')
    stats['total_players'] = cursor.fetchone()['count']
    
    # Total teams
    cursor = conn.execute('SELECT COUNT(*) as count FROM teams')
    stats['total_teams'] = cursor.fetchone()['count']
    
    # Total awards
    cursor = conn.execute('SELECT COUNT(*) as count FROM awards')
    stats['total_awards'] = cursor.fetchone()['count']
    
    # Recent inductees (last 10 years)
    cursor = conn.execute('''
        SELECT id, firstName, lastName, position, yearInducted 
        FROM hof_members 
        WHERE yearInducted IS NOT NULL 
        ORDER BY yearInducted DESC 
        LIMIT 10
    ''')
    stats['recent_inductees'] = cursor.fetchall()
    
    conn.close()
    return render_template('index.html', stats=stats)

@app.route('/players')
def players():
    """Players listing page"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page
    
    search = request.args.get('search', '')
    position_filter = request.args.get('position', '')
    year_filter = request.args.get('year', '')
    
    conn = get_db_connection()
    
    # Build query with filters
    query = '''
        SELECT id, firstName, lastName, position, nationality, 
               yearInducted, yearsActive, birthDay, deathDay, photoUrl
        FROM hof_members 
        WHERE 1=1
    '''
    params = []
    
    if search:
        query += ' AND (firstName LIKE ? OR lastName LIKE ? OR realName LIKE ?)'
        search_term = f'%{search}%'
        params.extend([search_term, search_term, search_term])
    
    if position_filter:
        query += ' AND position LIKE ?'
        params.append(f'%{position_filter}%')
    
    if year_filter:
        query += ' AND yearInducted = ?'
        params.append(year_filter)
    
    # Get total count - use a simpler approach
    count_params = []
    count_where = []
    
    if search:
        count_where.append('(firstName LIKE ? OR lastName LIKE ? OR realName LIKE ?)')
        search_term = f'%{search}%'
        count_params.extend([search_term, search_term, search_term])
    
    if position_filter:
        count_where.append('position LIKE ?')
        count_params.append(f'%{position_filter}%')
    
    if year_filter:
        count_where.append('yearInducted = ?')
        count_params.append(year_filter)
    
    where_clause = ' AND '.join(count_where) if count_where else '1=1'
    count_query = f'SELECT COUNT(*) as count FROM hof_members WHERE {where_clause}'
    
    cursor = conn.execute(count_query, count_params)
    result = cursor.fetchone()
    total_count = result['count'] if result else 0
    
    # Get paginated results
    query += ' ORDER BY lastName, firstName LIMIT ? OFFSET ?'
    params.extend([per_page, offset])
    
    cursor = conn.execute(query, params)
    players = cursor.fetchall()
    
    # Get unique positions for filter dropdown
    cursor = conn.execute('SELECT DISTINCT position FROM hof_members WHERE position IS NOT NULL ORDER BY position')
    positions = [row['position'] for row in cursor.fetchall()]
    
    # Get unique years for filter dropdown
    cursor = conn.execute('SELECT DISTINCT yearInducted FROM hof_members WHERE yearInducted IS NOT NULL ORDER BY yearInducted DESC')
    years = [row['yearInducted'] for row in cursor.fetchall()]
    
    conn.close()
    
    total_pages = (total_count + per_page - 1) // per_page
    
    return render_template('players.html', 
                         players=players, 
                         page=page, 
                         total_pages=total_pages,
                         total_count=total_count,
                         search=search,
                         position_filter=position_filter,
                         year_filter=year_filter,
                         positions=positions,
                         years=years)

@app.route('/player/<int:player_id>')
def player_detail(player_id):
    """Individual player detail page"""
    conn = get_db_connection()
    
    # Get player info
    cursor = conn.execute('''
        SELECT * FROM hof_members WHERE id = ?
    ''', (player_id,))
    player = cursor.fetchone()
    
    if not player:
        conn.close()
        return "Player not found", 404
    
    # Get teams
    cursor = conn.execute('''
        SELECT t.name, pt.is_primary
        FROM teams t
        JOIN player_teams pt ON t.id = pt.team_id
        WHERE pt.player_id = ?
        ORDER BY pt.is_primary DESC, t.name
    ''', (player_id,))
    teams = cursor.fetchall()
    
    # Get awards
    cursor = conn.execute('''
        SELECT a.name
        FROM awards a
        JOIN player_awards pa ON a.id = pa.award_id
        WHERE pa.player_id = ?
        ORDER BY a.name
    ''', (player_id,))
    awards = cursor.fetchall()
    
    # Get batting/throwing hands
    cursor = conn.execute('''
        SELECT bat_hand, throw_hand
        FROM player_hands
        WHERE player_id = ?
    ''', (player_id,))
    hands = cursor.fetchone()
    
    conn.close()
    
    return render_template('player_detail.html', 
                         player=player, 
                         teams=teams, 
                         awards=awards, 
                         hands=hands)

@app.route('/teams')
def teams():
    """Teams listing page"""
    conn = get_db_connection()
    
    cursor = conn.execute('''
        SELECT t.name, COUNT(DISTINCT pt.player_id) as player_count
        FROM teams t
        JOIN player_teams pt ON t.id = pt.team_id
        GROUP BY t.id, t.name
        ORDER BY player_count DESC, t.name
    ''')
    teams = cursor.fetchall()
    
    conn.close()
    return render_template('teams.html', teams=teams)

@app.route('/team/<team_name>')
def team_detail(team_name):
    """Team detail page"""
    conn = get_db_connection()
    
    # Get team info and players
    cursor = conn.execute('''
        SELECT h.id, h.firstName, h.lastName, h.position, h.yearInducted,
               pt.is_primary
        FROM hof_members h
        JOIN player_teams pt ON h.id = pt.player_id
        JOIN teams t ON pt.team_id = t.id
        WHERE t.name = ?
        ORDER BY h.lastName, h.firstName
    ''', (team_name,))
    players = cursor.fetchall()
    
    conn.close()
    return render_template('team_detail.html', team_name=team_name, players=players)

@app.route('/awards')
def awards():
    """Awards listing page"""
    conn = get_db_connection()
    
    cursor = conn.execute('''
        SELECT a.name, COUNT(DISTINCT pa.player_id) as player_count
        FROM awards a
        JOIN player_awards pa ON a.id = pa.award_id
        GROUP BY a.id, a.name
        ORDER BY player_count DESC, a.name
    ''')
    awards = cursor.fetchall()
    
    conn.close()
    return render_template('awards.html', awards=awards)

@app.route('/search')
def search():
    """Search functionality"""
    query = request.args.get('q', '')
    if not query:
        return render_template('search.html', results=None)
    
    conn = get_db_connection()
    
    # Search in players
    cursor = conn.execute('''
        SELECT id, firstName, lastName, position, yearInducted
        FROM hof_members
        WHERE firstName LIKE ? OR lastName LIKE ? OR realName LIKE ? OR position LIKE ?
        ORDER BY lastName, firstName
        LIMIT 50
    ''', (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
    players = cursor.fetchall()
    
    # Search in teams
    cursor = conn.execute('''
        SELECT DISTINCT t.name
        FROM teams t
        WHERE t.name LIKE ?
        ORDER BY t.name
        LIMIT 20
    ''', (f'%{query}%',))
    teams = cursor.fetchall()
    
    # Search in awards
    cursor = conn.execute('''
        SELECT DISTINCT a.name
        FROM awards a
        WHERE a.name LIKE ?
        ORDER BY a.name
        LIMIT 20
    ''', (f'%{query}%',))
    awards = cursor.fetchall()
    
    conn.close()
    
    return render_template('search.html', 
                         query=query, 
                         players=players, 
                         teams=teams, 
                         awards=awards)

@app.route('/api/players')
def api_players():
    """API endpoint for players data"""
    conn = get_db_connection()
    
    cursor = conn.execute('''
        SELECT id, firstName, lastName, position, yearInducted
        FROM hof_members
        ORDER BY lastName, firstName
    ''')
    players = cursor.fetchall()
    
    conn.close()
    
    return jsonify([dict(player) for player in players])

@app.route('/award/<award_name>')
def award_detail(award_name):
    conn = get_db_connection()
    cursor = conn.execute('SELECT id FROM awards WHERE name = ?', (award_name,))
    award = cursor.fetchone()
    if not award:
        conn.close()
        return f"Award '{award_name}' not found", 404
    cursor = conn.execute('''
        SELECT h.id, h.firstName, h.lastName, h.photoUrl
        FROM hof_members h
        JOIN player_awards pa ON h.id = pa.player_id
        WHERE pa.award_id = ?
        ORDER BY h.lastName, h.firstName
    ''', (award['id'],))
    players = cursor.fetchall()
    conn.close()
    return render_template('award_detail.html', award_name=award_name, players=players)

def run_server():
    """Run the Flask application"""
    app.run(host='0.0.0.0', port=8000, debug=True)

if __name__ == '__main__':
    run_server() 