from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import app
from models import Level, Subject, SyllabusPlanEntry, db


LESSON_BLOCKS = [
    ("Vocabulary and Warm-up", "Core vocabulary and guided oral practice.", "Workbook vocabulary review."),
    ("Reading and Structures", "Reading practice with sentence patterns from the unit.", "Reading follow-up and sentence writing."),
    ("Listening and Speaking", "Listening focus and structured speaking practice.", "Short speaking preparation and home review."),
    ("Writing and Review", "Guided writing task with lesson review and correction.", "Writing extension and unit revision."),
]


def load_index_lessons(index_file: Path) -> tuple[str, list[dict]]:
    payload = json.loads(index_file.read_text())
    book_title = (payload.get("book_title") or "").strip() or "Indexed Book"
    lessons = []
    for unit in payload.get("units", []):
        unit_number = unit.get("unit_number")
        unit_title = (unit.get("unit_title") or "").strip()
        unit_name = f"الوحدة {unit_number}: {unit_title}"
        for lesson in unit.get("lessons", []):
            printed_pages = lesson.get("printed_pages") or {}
            page_start = printed_pages.get("start")
            page_end = printed_pages.get("end")
            page_label = f"{page_start}" if page_start == page_end else f"{page_start}-{page_end}"
            lessons.append(
                {
                    "book_name": book_title,
                    "unit_name": unit_name,
                    "lesson_title": lesson.get("title") or f"Lesson {lesson.get('textbook_lesson_number')}",
                    "source_reference": f"درس {lesson.get('textbook_lesson_number')} - الصفحات {page_label}",
                    "learning_objective": f"تدريس درس: {lesson.get('title')}",
                    "planned_homework": f"مراجعة درس {lesson.get('title')} والتدرب عليه منزلياً.",
                    "note_text": f"الوحدة {unit_number} - الدرس {lesson.get('unit_lesson_position')}",
                }
            )
        lessons.append(
            {
                "book_name": book_title,
                "unit_name": unit_name,
                "lesson_title": f"مراجعة الوحدة {unit_number}",
                "source_reference": f"مراجعة ختامية للوحدة {unit_number}",
                "learning_objective": f"مراجعة شاملة لمفردات وتراكيب ومهارات الوحدة {unit_number}.",
                "planned_homework": f"حل أسئلة مراجعة الوحدة {unit_number} والاستعداد للتقويم.",
                "note_text": f"الوحدة {unit_number} - حصة مراجعة",
            }
        )
    return book_title, lessons


def pick_target_level(level_id: int | None) -> Level | None:
    if level_id:
        return Level.query.get(level_id)

    return (
        Level.query.filter(Level.teacher_id.isnot(None))
        .order_by(Level.order_index.desc(), Level.id.desc())
        .first()
    )


def pick_book_name(level: Level) -> str:
    subjects = (
        Subject.query.filter_by(level_id=level.id, is_active=True)
        .order_by(Subject.order_index.asc().nullslast(), Subject.id.asc())
        .all()
    )
    for subject in subjects:
        items = sorted(subject.curriculum_items, key=lambda item: ((item.order_index or 0), item.id))
        if items:
            return items[0].title
    return f"{level.name} Main Book"


def create_plan_rows(level: Level, replace: bool = False, index_file: Path | None = None) -> tuple[int, int]:
    existing_rows = SyllabusPlanEntry.query.filter_by(level_id=level.id).all()
    if existing_rows and not replace:
        return 0, len(existing_rows)
    if existing_rows and replace:
        for row in existing_rows:
            db.session.delete(row)

    indexed_lessons: list[dict] = []
    if index_file and index_file.exists():
        _, indexed_lessons = load_index_lessons(index_file)

    book_name = pick_book_name(level)
    created_count = 0
    if indexed_lessons:
        for index, lesson in enumerate(indexed_lessons, start=1):
            week_number = ((index - 1) // 4) + 1
            session_number = ((index - 1) % 4) + 1
            entry = SyllabusPlanEntry(
                level_id=level.id,
                week_number=week_number,
                session_number=session_number,
                book_name=lesson["book_name"] or book_name,
                unit_name=lesson["unit_name"],
                lesson_title=lesson["lesson_title"],
                source_reference=lesson["source_reference"],
                learning_objective=lesson["learning_objective"],
                planned_homework=lesson["planned_homework"],
                note_text=lesson["note_text"],
                status="planned",
                order_index=((week_number - 1) * 4) + session_number,
            )
            db.session.add(entry)
            created_count += 1
        return created_count, 0

    for week_number in range(1, 41):
        unit_number = ((week_number - 1) // 2) + 1
        cycle_week = ((week_number - 1) % 2) + 1
        for session_number in range(1, 5):
            block_title, objective, homework = LESSON_BLOCKS[session_number - 1]
            lesson_index = ((cycle_week - 1) * 4) + session_number
            entry = SyllabusPlanEntry(
                level_id=level.id,
                week_number=week_number,
                session_number=session_number,
                book_name=book_name,
                unit_name=f"Unit {unit_number:02d}",
                lesson_title=f"Lesson {lesson_index:02d} - {block_title}",
                source_reference=f"Unit {unit_number:02d} / Week {week_number:02d} / Session {session_number}",
                learning_objective=objective,
                planned_homework=homework,
                note_text="Sample yearly plan template generated for teacher use.",
                status="planned",
                order_index=((week_number - 1) * 4) + session_number,
            )
            db.session.add(entry)
            created_count += 1

    return created_count, 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a sample 40x4 syllabus plan for a level.")
    parser.add_argument("--level-id", type=int, default=None, help="Optional explicit level id")
    parser.add_argument("--replace", action="store_true", help="Replace existing plan rows if present")
    parser.add_argument("--index-file", type=str, default="", help="Optional book planning index JSON file")
    args = parser.parse_args()

    with app.app_context():
        level = pick_target_level(args.level_id)
        if not level:
            print("NO_LEVEL")
            return
        index_file = Path(args.index_file).resolve() if args.index_file else None
        created_count, existing_count = create_plan_rows(level, replace=args.replace, index_file=index_file)
        if created_count == 0 and existing_count:
            print(f"SKIPPED level={level.id} name={level.name} existing_rows={existing_count}")
            return
        db.session.commit()
        print(f"CREATED level={level.id} name={level.name} rows={created_count}")


if __name__ == "__main__":
    main()
