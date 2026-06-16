import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime, timedelta

# Define the qualifying window (between 3 months and 5 years ago)
today = datetime.now()
five_years_ago = today - timedelta(days=5*365)
three_months_ago = today - timedelta(days=90)

print(f"Querying papers published between {five_years_ago.strftime('%Y-%m-%d')} and {three_months_ago.strftime('%Y-%m-%d')}...")

# Namespaces used by arXiv API
ns = {
    'atom': 'http://www.w3.org/2005/Atom',
    'arxiv': 'http://arxiv.org/schemas/atom'
}

# We will retrieve the most recent 1000 papers in plasm-ph. 
# You can increase max_results up to 2000 or implement paging for a larger dataset.
url = "http://export.arxiv.org/api/query?search_query=cat:physics.plasm-ph&max_results=1000&sortBy=submittedDate&sortOrder=descending"

author_data = defaultdict(lambda: {"count": 0, "institutions": set(), "topics": set()})

try:
    response = urllib.request.urlopen(url)
    xml_data = response.read()
    root = ET.fromstring(xml_data)
    
    for entry in root.findall('atom:entry', ns):
        # Extract and parse publication date
        published_str = entry.find('atom:published', ns).text
        published_dt = datetime.strptime(published_str[:10], "%Y-%m-%d")
        
        # Filter by the 3-month to 5-year window
        if five_years_ago <= published_dt <= three_months_ago:
            title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
            
            # Extract authors and their affiliations
            for author in entry.findall('atom:author', ns):
                name = author.find('atom:name', ns).text.strip()
                
                # Check for optional affiliation tag
                affiliation_tag = author.find('arxiv:affiliation', ns)
                affiliation = affiliation_tag.text.strip() if affiliation_tag is not None else "Not Listed"
                
                author_data[name]["count"] += 1
                if affiliation != "Not Listed":
                    author_data[name]["institutions"].add(affiliation)
                author_data[name]["topics"].add(title)

    # Filter for authors with 2 or more qualifying papers
    qualified_authors = {k: v for k, v in author_data.items() if v["count"] >= 2}
    
    # Write to a CSV file
    csv_file = "qualified_arxiv_endorsers.csv"
    with open(csv_file, "w", encoding="utf-8") as f:
        f.write("Author Name,Paper Count,Institutions,Sample Topics/Titles\n")
        for author, data in sorted(qualified_authors.items(), key=lambda x: x[1]["count"], reverse=True):
            insts = "; ".join(data["institutions"]) if data["institutions"] else "Not Listed"
            # Limit to printing 2 sample topics to keep the CSV clean
            topics = " | ".join(list(data["topics"])[:2]).replace('"', "'")
            f.write(f'"{author}",{data["count"]},"{insts}","{topics}"\n')
            
    print(f"Successfully generated '{csv_file}' with {len(qualified_authors)} potential endorsers.")

except Exception as e:
    print(f"An error occurred: {e}")
