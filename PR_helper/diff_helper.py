import os
import subprocess
import re
from html import escape
from collections import defaultdict

HTML_OUTPUT_DIR = "PR_helper/html_reports"  # Define a centralized folder for all HTML files


def ensure_output_dir():
    """Ensure the output directory exists."""
    os.makedirs(HTML_OUTPUT_DIR, exist_ok=True)


def run_git_command(command):
    """Run a Git command and return its output."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Git command failed:\nCommand: {command}\nError: {result.stderr}")
    return result.stdout


def parse_git_diff(diff_output):
    """Parse git diff output to extract file paths and changed lines with content."""
    changes = {}
    current_file = None
    hunk_pattern = re.compile(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")

    for line in diff_output.splitlines():
        if line.startswith("diff --git"):
            match = re.search(r'diff --git a/(.+) b/(.+)', line)
            if match:
                current_file = match.group(2)
                changes[current_file] = {'added': [], 'removed': []}
        elif current_file:
            hunk_match = hunk_pattern.search(line)
            if hunk_match:
                start_line = int(hunk_match.group(1))
                current_line = start_line
                changes[current_file]['current_line'] = current_line
            elif line.startswith("+") and not line.startswith("+++"):
                content = line[1:]
                line_number = changes[current_file].get('current_line', 0)
                changes[current_file]['added'].append((line_number, content))
                changes[current_file]['current_line'] += 1
            elif line.startswith("-") and not line.startswith("---"):
                content = line[1:]
                changes[current_file]['removed'].append(content)
    return changes


def parse_git_blame(blame_output):
    """Parse git blame output to map line numbers to authors."""
    blame_data = {}
    for line in blame_output.splitlines():
        match = re.match(r".*\((.*?)\s+\d{4}-\d{2}-\d{2}.*?\s+(\d+)\)", line)
        if match:
            author = match.group(1)
            line_num = int(match.group(2))
            blame_data[line_num] = author.strip()
    return blame_data


def load_template(template_path):
    """Load the HTML template from the given path."""
    with open(template_path, 'r') as file:
        return file.read()

def generate_file_html(file, changes, blame_data, username, template_path="PR_helper/file_template.html"):
    """
    Generate HTML output for a single file using a pre-saved template.
    
    Args:
        file: The file name.
        changes: A dictionary with changes (e.g., {'added': [(line_num, line_content), ...], 'removed': [...]}).
        blame_data: A dictionary mapping line numbers to authors.
        username: The username of the current user.
        template_path: Path to the HTML template file.
    
    Returns:
        A string containing the generated HTML.
    """
    # Load the template
    template = load_template(template_path)
    
    # Gather authors and assign colors
    authors = set(blame_data.values())
    author_colors = {author: f"hsl({index * 360 // len(authors)}, 70%, 90%)" 
                     for index, author in enumerate(authors)}
    
    # Create a set for quick lookup of change line numbers
    added_lines = {line_number for line_number, _ in changes.get('added', [])}
    
    # Generate content for the entire file
    content_lines = []
    with open(file, 'r') as f:
        for line_number, line in enumerate(f, start=1):
            blame_author = blame_data.get(line_number, "Unknown")
            css_class = "mine" if blame_author == username else "other"
            color = author_colors.get(blame_author, "#ffffff")
            author_label = f"[{blame_author}]"
            
            # Highlight only the lines that are in changes
            if line_number in added_lines:
                content_lines.append(
                    f"<div class='line {css_class}' style='background-color: {color};'>"
                    f"<span class='line-number'>{author_label}{line_number}</span>"
                    f"<span class='line-content'>{escape(line)}</span>"
                    f"</div>"
                )
            else:
                content_lines.append(
                    f"<div class='line'>"
                    f"<span class='line-number'>{author_label} {line_number}</span>"

                    f"<span class='line-content'>{escape(line)}</span>"
                    f"</div>"
                )

    
    # Generate author key
    author_key = "\n".join(
        f"<li style='background-color: {color};'>{escape(author)}</li>"
        for author, color in author_colors.items()
    )
    
    # Replace placeholders in the template
    html_output = template.replace("{{ file_name }}", escape(file))
    html_output = html_output.replace("{{ content }}", "\n".join(content_lines))
    html_output = html_output.replace("{{ author_key }}", author_key)
    
    return html_output


def generate_index_html(summary, template_path, output_path):
    """
    Generate an index HTML file by populating a template with summaries and links to file HTML pages.
    """
    try:
        with open(template_path, 'r') as file:
            template = file.read()
    except FileNotFoundError:
        raise Exception(f"Template file not found: {template_path}")

    rows = []
    for file, stats in summary.items():
        path = file.replace("/", "__") + ".html"
        rows.append(
            f"<tr><td><a href='{path}'>{escape(file)}</a></td>"
            f"<td>{stats['total']}</td><td>{stats['new']}</td><td>{stats['old']}</td></tr>"
        )

    html_content = template.replace(
        "<!-- Dynamic rows will be inserted here -->",
        "\n".join(rows)
    )

    try:
        with open(output_path, 'w') as output_file:
            output_file.write(html_content)
    except Exception as e:
        raise Exception(f"Error writing to output file: {output_path}\n{e}")


def main():
    ensure_output_dir()
    username = "Joey Rubas"
    try:
        diff_output = run_git_command("git diff master")
        diff_data = parse_git_diff(diff_output)

        summary = {}
        for file, changes in diff_data.items():
            blame_output = run_git_command(f"git blame -C -C -C {file}")
            blame_data = parse_git_blame(blame_output)

            #total lines = all lines in current saved version of the file
            #old lines = lines who's blame author is not the current user
            #new lines = lines who's blame author is the current user
            total_lines = len(blame_data)
            old_lines = len([line for line in blame_data.values() if line != username])
            new_lines = total_lines - old_lines
            summary[file] = {'new': new_lines, 'old': old_lines, 'total': total_lines}

            file_html = generate_file_html(file, changes, blame_data, username)
            output_path = os.path.join(HTML_OUTPUT_DIR, f"{file.replace('/', '__' )}.html")
            with open(output_path, "w") as f:
                f.write(file_html)

        generate_index_html(summary, "PR_helper/index_template.html", os.path.join(HTML_OUTPUT_DIR, "index.html"))
        print(f"HTML files and index generated in the '{HTML_OUTPUT_DIR}' directory.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
