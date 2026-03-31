from datetime import datetime
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import app, run_scheduled_weekly_followup


def main() -> int:
    with app.app_context():
        result = run_scheduled_weekly_followup(now=datetime.now(), force=False)
        print(f"{result['status']}: {result['message']}")
        return 0 if result["status"] in {"success", "skipped"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
