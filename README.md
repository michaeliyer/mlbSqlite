# MLB Hall of Fame Database

This project contains a SQLite database with comprehensive information about Major League Baseball Hall of Fame members.

## Database Structure

The database consists of the following tables:

### Main Tables

1. **hof_members** - Core player information

   - `id` (PRIMARY KEY)
   - `firstName`, `lastName` - Player names
   - `realName` - Full legal name
   - `nickNames` - Player nicknames
   - `position` - Primary position played
   - `nationality` - Player's nationality
   - `race` - Player's race/ethnicity
   - `yearsActive` - Years of professional activity
   - `birthDay`, `deathDay` - Birth and death dates
   - `yearInducted` - Year inducted into Hall of Fame
   - `commentOne`, `commentTwo` - Additional comments
   - `created_at` - Record creation timestamp

2. **teams** - All teams players have been associated with

   - `id` (PRIMARY KEY)
   - `name` - Team name

3. **awards** - All awards and honors
   - `id` (PRIMARY KEY)
   - `name` - Award name

### Junction Tables

4. **player_teams** - Many-to-many relationship between players and teams

   - `id` (PRIMARY KEY)
   - `player_id` (FOREIGN KEY to hof_members)
   - `team_id` (FOREIGN KEY to teams)
   - `is_primary` - Boolean indicating if this was the player's primary team

5. **player_awards** - Many-to-many relationship between players and awards

   - `id` (PRIMARY KEY)
   - `player_id` (FOREIGN KEY to hof_members)
   - `award_id` (FOREIGN KEY to awards)

6. **player_hands** - Batting and throwing hand information
   - `id` (PRIMARY KEY)
   - `player_id` (FOREIGN KEY to hof_members)
   - `bat_hand` - Batting hand (Left, Right, Switch, Both)
   - `throw_hand` - Throwing hand (Left, Right)

## Database Statistics

- **349** Hall of Fame members
- **146** unique teams
- **351** unique awards
- **941** player-team relationships
- **593** player-award relationships

## Files

- `mlbSqlPlayers.js` - Original JavaScript data file
- `hofMembers.csv` - CSV version of the data
- `js_to_csv.py` - Script that converted JS to CSV
- `load_database.py` - Script that loads data into SQLite database
- `query_examples.py` - Example queries demonstrating database usage
- `mlbSql.db` - SQLite database file

## Usage

### Loading the Database

```bash
python3 load_database.py
```

### Running Example Queries

```bash
python3 query_examples.py
```

### Custom Queries

You can run custom SQL queries using the SQLite command line tool:

```bash
sqlite3 mlbSql.db
```

Example queries:

```sql
-- Find all players inducted in a specific year
SELECT firstName, lastName, position
FROM hof_members
WHERE yearInducted = 1982;

-- Find players by team
SELECT DISTINCT h.firstName, h.lastName, h.position
FROM hof_members h
JOIN player_teams pt ON h.id = pt.player_id
JOIN teams t ON pt.team_id = t.id
WHERE t.name LIKE '%Yankees%';

-- Find players with specific awards
SELECT DISTINCT h.firstName, h.lastName, a.name
FROM hof_members h
JOIN player_awards pa ON h.id = pa.player_id
JOIN awards a ON pa.award_id = a.id
WHERE a.name LIKE '%MVP%';
```

## Data Sources

The original data was compiled from various sources including:

- Baseball Hall of Fame official records
- Baseball Reference
- MLB historical data
- Various baseball encyclopedias and reference materials

## Notes

- Some players may have `yearInducted` as NULL if they haven't been officially inducted yet
- Team names include historical variations (e.g., "Brooklyn Dodgers" vs "Los Angeles Dodgers")
- Awards are stored as individual entries, so a player with "3× All-Star" would have one award entry
- Batting and throwing hands are stored as comma-separated values for players who used multiple hands

## License

This database is for educational and research purposes. Please respect the original sources when using this data.

To open:
source venv/bin/activate
python app.py

gunicorn --worker-class uvicorn.workers.UvicornWorker --bind '127.0.0.1:8000' --daemon main:app (name of app???)
