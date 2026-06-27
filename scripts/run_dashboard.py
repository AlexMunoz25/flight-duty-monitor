import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from app import build_dashboard

if __name__ == "__main__":
    build_dashboard().run(debug=True, host="127.0.0.1", port=8050)
