from bs4 import BeautifulSoup
import json

def extract_headings_hierarchy(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    hierarchy = []

    current_level = {i: None for i in range(1, 7)}

    for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        print("heading",heading.get_text(strip=True))
        level = int(heading.name[1])
        heading_text = heading.get_text(strip=True)
        heading_dict = {'text': heading_text, 'children': []}

        if level == 1:
            hierarchy.append(heading_dict)
            current_level[1] = heading_dict
        else:
            parent = current_level[level - 1]
            if parent:
                parent['children'].append(heading_dict)
            current_level[level] = heading_dict

        # Reset lower levels
        for i in range(level + 1, 7):
            current_level[i] = None

    return hierarchy

# Example usage
html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Sample HTML</title>
</head>
<body>
    <h1>1 Main Title</h1>
    <h2>1.1Subheading 1</h2>
    <h3>1.1.1Sub-subheading 1.1</h3>
    <h2>1.2Subheading 2</h2>
    <h3>1.2.1Sub-subheading 2.1</h3>
    <h4>1.2.1.1Sub-sub-subheading 2.1.1</h4>
    <h1>2 Another Main Title</h1>
    <h2>2.1 Subheading 1</h2>
    <h3>2.1.1 Sub-subheading 1.1</h3>
</body>
</html>
"""

headings_hierarchy = extract_headings_hierarchy(html_content)
print(json.dumps(headings_hierarchy, indent=4))