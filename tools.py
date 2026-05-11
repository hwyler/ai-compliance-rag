# tools.py — Compliance Knowledge Base Tools
import re
from pathlib import Path

NOTES_DIR = (Path(__file__).parent / "notes").resolve()

def list_files() -> str:
    """
    Lists all compliance documents in the knowledge base.
    Always call this first to discover available documents
    before searching or reading. Returns relative filenames.
    """
    try:
        files = sorted(NOTES_DIR.glob("*.md"))
        if not files:
            return "No compliance documents found."
        return "\n".join(str(f.relative_to(NOTES_DIR)) for f in files)
    except Exception as e:
        return f"Error listing files: {str(e)}"


def grab(pattern: str) -> str:
    """
    Searches all compliance documents for a keyword or phrase.
    Use to find controls, article references, system names,
    risk levels, owners, or status keywords like OPEN or MISSING.
    Pattern matching is case-insensitive.
    Returns filename, line number, and matching content.
    """
    try:
        compiled = re.compile(pattern, re.IGNORECASE)
        results = []
        for filepath in sorted(NOTES_DIR.glob("*.md")):
            lines = filepath.read_text(encoding="utf-8").splitlines()
            for i, line in enumerate(lines, start=1):
                if compiled.search(line):
                    rel_name = filepath.relative_to(NOTES_DIR)
                    results.append(f"{rel_name} | Line {i}: {line.strip()}")
        if not results:
            return f"No matches found for: '{pattern}'"
        return "\n".join(results)
    except Exception as e:
        return f"Search error: {str(e)}"


def read_file(filename: str) -> str:
    """
    Reads the full content of a specific compliance document.
    Use after identifying the file via list_files or grab.
    Only files within the compliance knowledge base are accessible.
    Refuses access to files outside the designated notes directory.
    """
    try:
        target = (NOTES_DIR / filename).resolve()
        if not target.is_relative_to(NOTES_DIR):
            return f"Access denied: {filename} is outside compliance knowledge base."
        if not target.exists():
            return f"File not found: {filename}. Use list_files to see available documents."
        return target.read_text(encoding="utf-8")
    except Exception as e:
        return f"Read error: {str(e)}"
