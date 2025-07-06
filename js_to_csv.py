import re
import json
import csv

# Path to the JS file
js_file = 'myPeople.js'
# Output CSV file
csv_file = 'hofMembers.csv'

# Read the JS file
with open(js_file, 'r', encoding='utf-8') as f:
    js_content = f.read()

# Extract the hofMember array using regex (greedy match between brackets)
match = re.search(r'export const hofMember = (\[.*\]);', js_content, re.DOTALL)
if not match:
    raise ValueError('hofMember array not found in JS file!')

hof_data = match.group(1)

# Replace JS-style null with Python None
hof_data = hof_data.replace('null', 'None')
# Replace JS-style comments (// ...) with nothing
hof_data = re.sub(r'//.*', '', hof_data)
# Remove JS block comments (/* ... */)
hof_data = re.sub(r'/\*.*?\*/', '', hof_data, flags=re.DOTALL)

# Convert unquoted JS object keys to quoted keys (e.g., firstName: to "firstName":)
hof_data = re.sub(r'(\{|,|\[)\s*([a-zA-Z0-9_]+)\s*:', r'\1 "\2":', hof_data)

# Replace single trailing commas in objects/arrays (Python doesn't allow them)
hof_data = re.sub(r',([ \n\r\t]*[}\]])', r'\1', hof_data)

# Evaluate the array as Python data
hof_list = eval(hof_data)

# List of fields to include in CSV
fields = [
    'firstName', 'lastName', 'teams', 'primaryTeam', 'position', 'nationality', 'race',
    'yearsActive', 'batHand', 'throwHand', 'awards', 'birthDay', 'deathDay',
    'realName', 'nickNames', 'yearInducted', 'commentOne', 'commentTwo'
]

def to_csv_value(val):
    if isinstance(val, (list, dict)):
        return json.dumps(val, ensure_ascii=False)
    if val is None:
        return ''
    return str(val)

with open(csv_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    for person in hof_list:
        row = {field: to_csv_value(person.get(field)) for field in fields}
        writer.writerow(row)

print(f'CSV file created: {csv_file}') 