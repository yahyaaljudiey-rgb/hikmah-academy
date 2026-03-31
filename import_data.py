from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, Optional

import pandas as pd
from flask import Flask

from models import Student, db


TARGET_SHEETS = [
    "Qaeda-B",
    "Pri-Beg-B",
    "Pri-Int-B.",
    "Pri-Adv-B",
    "Sec-Beg-B1",
    "Sec-Beg-B2",
    "Sec-Int-B",
    "Sec-Adv-B",
]

NAME_COL = "Student Name"
STATUS_COL = "Status"
YEAR_COL = "Studen Year"


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///hikmah_academy.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    return app


def clean_text(value: object) -> Optional[str]:
    if value is None or pd.isna(value):
        return None

    text = str(value).strip()
    return text or None


def normalize_sheet_name(name: str) -> str:
    return name.strip()


def resolve_target_sheets(
    available_sheets: Iterable[str], target_sheets: Iterable[str]
) -> Dict[str, str]:
    normalized = {normalize_sheet_name(sheet): sheet for sheet in available_sheets}
    resolved: Dict[str, str] = {}

    for target in target_sheets:
        actual = normalized.get(normalize_sheet_name(target))
        if actual:
            resolved[target] = actual

    return resolved


def load_sheet(file_path: Path, sheet_name: str) -> pd.DataFrame:
    return pd.read_excel(file_path, sheet_name=sheet_name, header=4, dtype=str)


def get_next_code_number() -> int:
    prefix = "STD-"
    highest = 0

    existing_codes = db.session.query(Student.student_code).all()
    for (code,) in existing_codes:
        if not code or not code.startswith(prefix):
            continue

        suffix = code[len(prefix) :]
        if suffix.isdigit():
            highest = max(highest, int(suffix))

    return highest + 1


def make_student_code(next_number: int) -> str:
    return f"STD-{next_number:06d}"


def import_students(file_path: Path) -> None:
    excel_file = pd.ExcelFile(file_path)
    sheet_map = resolve_target_sheets(excel_file.sheet_names, TARGET_SHEETS)

    missing = [sheet for sheet in TARGET_SHEETS if sheet not in sheet_map]
    for sheet in missing:
        print(f"{sheet}: sheet not found, skipped")

    next_code_number = get_next_code_number()

    for target_sheet in TARGET_SHEETS:
        actual_sheet = sheet_map.get(target_sheet)
        if not actual_sheet:
            continue

        df = load_sheet(file_path, actual_sheet)
        imported_count = 0

        for _, row in df.iterrows():
            full_name = clean_text(row.get(NAME_COL))
            if not full_name:
                continue

            status = clean_text(row.get(STATUS_COL))
            student_year = clean_text(row.get(YEAR_COL))

            student_code = make_student_code(next_code_number)
            next_code_number += 1

            student = Student(
                student_code=student_code,
                full_name=full_name,
                status=status,
                student_year=student_year,
                level_name=target_sheet,
            )
            db.session.add(student)
            imported_count += 1

        db.session.commit()
        print(f"{target_sheet}: {imported_count} rows imported")


def main() -> None:
    file_path = Path("data/students.xlsx")
    if not file_path.exists():
        raise FileNotFoundError(f"Excel file not found: {file_path}")

    app = create_app()
    with app.app_context():
        db.create_all()
        import_students(file_path)


if __name__ == "__main__":
    main()
