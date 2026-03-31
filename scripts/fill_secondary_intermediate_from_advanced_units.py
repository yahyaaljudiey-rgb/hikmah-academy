from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import app, build_instructional_slot_sequence
from models import SyllabusPlanEntry, db


TARGET_LEVEL_ID = 7
SOURCE_LEVEL_ID = 8
SOURCE_UNITS = {
    "الوحدة 9: العالم قرية صغيرة",
    "الوحدة 10: النظافة",
    "الوحدة 11: الإسلام",
}


def main() -> None:
    with app.app_context():
        slots = build_instructional_slot_sequence()
        used_slots = {
            row.order_index
            for row in SyllabusPlanEntry.query.filter(
                SyllabusPlanEntry.level_id == TARGET_LEVEL_ID,
                SyllabusPlanEntry.week_number.isnot(None),
            ).all()
            if row.order_index
        }
        remaining_slots = [slot for slot in slots if slot["slot_order"] not in used_slots]
        if not remaining_slots:
            print("NO_REMAINING_SLOTS")
            return

        source_rows = (
            SyllabusPlanEntry.query.filter(
                SyllabusPlanEntry.level_id == SOURCE_LEVEL_ID,
                SyllabusPlanEntry.unit_name.in_(SOURCE_UNITS),
            )
            .order_by(SyllabusPlanEntry.order_index.asc(), SyllabusPlanEntry.id.asc())
            .all()
        )

        created = 0
        for slot, source in zip(remaining_slots, source_rows):
            db.session.add(
                SyllabusPlanEntry(
                    level_id=TARGET_LEVEL_ID,
                    week_number=slot["academic_week_number"],
                    session_number=slot["session_number"],
                    book_name=source.book_name,
                    unit_name=source.unit_name,
                    lesson_title=source.lesson_title,
                    source_reference=source.source_reference,
                    learning_objective=source.learning_objective,
                    planned_homework=source.planned_homework,
                    note_text=source.note_text,
                    status="planned",
                    order_index=slot["slot_order"],
                )
            )
            created += 1

        db.session.commit()
        print(f"CREATED={created}")
        print(f"REMAINING_UNFILLED={max(len(remaining_slots) - created, 0)}")


if __name__ == "__main__":
    main()
