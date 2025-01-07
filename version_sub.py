from bs4 import BeautifulSoup
import git
from datetime import datetime

def update_release_table(markdown_file):
    # Read the markdown file
    with open(markdown_file, 'r') as f:
        content = f.read()

    # Parse the HTML table within the markdown
    soup = BeautifulSoup(content, 'html.parser')
    
    # Get git repository information
    repo = git.Repo('.')
    latest_commit = repo.head.commit
    
    # Get the latest tag
    tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)
    latest_tag = tags[-1] if tags else "No tags"

    # Find all cells with 'current' in their id
    current_cells = soup.find_all(lambda tag: tag.get('id', '').startswith('current_'))
    
    # Create a mapping of current values
    current_values = {}
    for cell in current_cells:
        id_suffix = cell.get('id').replace('current_', '')
        current_values[id_suffix] = cell.string

    # Update 'previous' cells with 'current' values
    previous_cells = soup.find_all(lambda tag: tag.get('id', '').startswith('previous_'))
    for cell in previous_cells:
        id_suffix = cell.get('id').replace('previous_', '')
        if id_suffix in current_values:
            cell.string = current_values[id_suffix]

    # Update 'current' cells with new git information
    for cell in current_cells:
        id_suffix = cell.get('id').replace('current_', '')
        if id_suffix == 'hash':
            cell.string = latest_commit.hexsha
        elif id_suffix == 'tag':
            cell.string = str(latest_tag)
        elif id_suffix == 'timestamp':
            cell.string = latest_commit.committed_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')

    # Convert the modified soup back to string
    table_html = str(soup.find('table'))
    
    # Replace the old table in the markdown content
    start_table = content.find('<table>')
    end_table = content.find('</table>') + 8
    new_content = content[:start_table] + table_html + content[end_table:]

    # Write the updated content back to the file
    with open(markdown_file, 'w') as f:
        f.write(new_content)

# Usage
if __name__ == "__main__":
    update_release_table('README.md')

