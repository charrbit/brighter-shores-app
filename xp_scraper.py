import sqlite3
import requests
from bs4 import BeautifulSoup

# Create database
connection = sqlite3.connect('BrighterShores.db')
cursor = connection.cursor()

# Drop any old experience tables
cursor.execute('DROP TABLE experience')

# Create experience table
creation_script = 'CREATE TABLE IF NOT EXISTS experience \
            (level, xp, xp_to_next, knowledge_xp)'
cursor.execute(creation_script)

# Extract webpage html as string
xp_url = 'https://brightershoreswiki.org/w/Experience'
response = requests.get(xp_url)
page_html = response.text

# Parse html for all tables
soup = BeautifulSoup(page_html, 'html.parser')
tables = soup.find_all('table')

# Discard undesired tables
tables = tables[:-2]

# Extract level/experience data
xp_data = []
for table in tables:
    for tablebody in table.find_all('tbody'):
        # Skip the table header row
        for tablerow in tablebody.find_all('tr')[1:]:
            level = tablerow.contents
            # Parse data from html string
            try:
                parsed_level = [int(x.text.replace(',', '')) for x in level]
            # Final level 500 does not have xp_to_next
            # Replace 'N/A' value with 0
            except ValueError:
                parsed_level = [x.text.replace(',', '') for x in level]
                parsed_level[2] = 0
                parsed_level = [int(x) for x in parsed_level]
            xp_data.append(parsed_level)

# Append a fourth column representing 0 knowledge xp
# to levels 0-19 (as knowledge is not unlocked)
for i in range(20):
    xp_data[i].append(0)

insertion_script = 'INSERT INTO experience \
                    VALUES (?, ?, ?, ?)'
                    
# Add the data to the database
for level in xp_data:
    cursor.execute(insertion_script, level)

cursor.close()
connection.close()