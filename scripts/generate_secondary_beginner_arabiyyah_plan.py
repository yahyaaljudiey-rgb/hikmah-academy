from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import app, build_instructional_slot_sequence
from models import Level, SyllabusPlanEntry, db


BOOK_NAME = "العربية بين يديك - الكتاب الأول - جزآن"

LESSON_BLUEPRINTS = [
    ("الحوار الأول ومفرداته وتدريباته", 2, "تدريس الحوار الأول واكتساب مفرداته الأساسية.", "مراجعة مفردات الحوار الأول والتدرب عليها."),
    ("الحوار الثاني ومفرداته وتدريباته", 2, "تدريس الحوار الثاني وتنمية الفهم الشفهي واللفظي.", "حل تدريبات الحوار الثاني ومراجعته."),
    ("الحوار الثالث ومفرداته وتدريباته", 2, "تدريس الحوار الثالث وربط مفرداته بالوحدة.", "مراجعة الحوار الثالث والتدرب على مفرداته."),
    ("تدريبات المفردات والمفردات الإضافية", 2, "ترسيخ مفردات الوحدة واستخداماتها الإضافية.", "تدريبات المفردات الإضافية في المنزل."),
    ("التراكيب النحوية وتدريباتها", 4, "فهم التراكيب الأساسية في الوحدة وتطبيقها.", "تطبيق التراكيب في جمل وتمارين قصيرة."),
    ("الأصوات وفهم المسموع", 3, "تدريب على الأصوات والتمييز السمعي وفهم المسموع.", "الاستماع والمراجعة الصوتية المنزلية."),
    ("الكلام وتدريباته", 3, "تنمية مهارة الكلام باستخدام مفردات الوحدة.", "تجهيز تعبير شفهي قصير من موضوع الوحدة."),
    ("القراءة وتدريباتها", 3, "تنمية مهارة القراءة والفهم القرائي في الوحدة.", "قراءة النص ومراجعة أسئلته."),
    ("الكتابة وتدريباتها", 4, "تنمية مهارة الكتابة والتعبير الكتابي حول موضوع الوحدة.", "إنجاز كتابة قصيرة أو تلخيص من موضوع الوحدة."),
]

UNITS = [
    {"unit_number": 1, "title": "التحية والتعارف", "start_page": 1},
    {"unit_number": 2, "title": "الأسرة", "start_page": 27, "review_start_page": 53},
    {"unit_number": 3, "title": "السكن", "start_page": 55},
    {"unit_number": 4, "title": "الحياة اليومية", "start_page": 81, "review_start_page": 107},
    {"unit_number": 5, "title": "الطعام والشراب", "start_page": 109},
    {"unit_number": 6, "title": "الصلاة", "start_page": 135, "review_start_page": 161},
    {"unit_number": 7, "title": "الدراسة", "start_page": 163},
    {"unit_number": 8, "title": "العمل", "start_page": 189, "review_start_page": 215},
    {"unit_number": 9, "title": "التسوق", "start_page": 239},
    {"unit_number": 10, "title": "الحج", "start_page": 265, "review_start_page": 291},
    {"unit_number": 11, "title": "الناس والأماكن", "start_page": 294},
    {"unit_number": 12, "title": "الهوايات", "start_page": 319, "review_start_page": 345},
    {"unit_number": 13, "title": "السفر", "start_page": 347},
    {"unit_number": 14, "title": "الحج والعمرة", "start_page": 373, "review_start_page": 399},
    {"unit_number": 15, "title": "الصحة", "start_page": 401},
    {"unit_number": 16, "title": "المظلة", "start_page": 427, "review_start_page": 453},
]

TARGET_LEVEL_IDS = (5, 6)


def build_plan_rows() -> list[dict]:
    rows: list[dict] = []
    order_index = 0

    for unit in UNITS:
        unit_number = unit["unit_number"]
        unit_title = unit["title"]
        unit_name = f"الوحدة {unit_number}: {unit_title}"
        current_page = unit["start_page"]

        for lesson_index, (lesson_title, lesson_pages, objective, homework) in enumerate(LESSON_BLUEPRINTS, start=1):
            page_start = current_page
            page_end = current_page + lesson_pages - 1
            current_page = page_end + 1
            order_index += 1
            rows.append(
                {
                    "order_index": order_index,
                    "book_name": BOOK_NAME,
                    "unit_name": unit_name,
                    "lesson_title": f"{unit_title} - {lesson_title}",
                    "source_reference": f"الوحدة {unit_number} - الدرس {lesson_index} - الصفحات {page_start}-{page_end}",
                    "learning_objective": objective,
                    "planned_homework": homework,
                    "note_text": f"الوحدة {unit_number} - الدرس {lesson_index}",
                }
            )

        review_start_page = unit.get("review_start_page")
        if review_start_page:
            paired_unit = unit_number - 1
            order_index += 1
            rows.append(
                {
                    "order_index": order_index,
                    "book_name": BOOK_NAME,
                    "unit_name": f"مراجعة الوحدتين {paired_unit}-{unit_number}",
                    "lesson_title": f"مراجعة الوحدتين {paired_unit}-{unit_number}",
                    "source_reference": f"مراجعة الوحدتين {paired_unit}-{unit_number} - الصفحات {review_start_page}-{review_start_page + 1}",
                    "learning_objective": f"مراجعة شاملة لمهارات ومفردات وتراكيب الوحدتين {paired_unit} و{unit_number}.",
                    "planned_homework": f"حل تدريبات مراجعة الوحدتين {paired_unit} و{unit_number}.",
                    "note_text": f"مراجعة الوحدتين {paired_unit}-{unit_number}",
                }
            )

    return rows


def fill_level_plan(level: Level, rows: list[dict]) -> int:
    existing_rows = SyllabusPlanEntry.query.filter_by(level_id=level.id).all()
    for row in existing_rows:
        db.session.delete(row)

    slots = build_instructional_slot_sequence()
    created = 0
    for index, row in enumerate(rows, start=1):
        slot = slots[index - 1] if index - 1 < len(slots) else None
        week_number = slot["academic_week_number"] if slot else None
        session_number = slot["session_number"] if slot else None
        db.session.add(
            SyllabusPlanEntry(
                level_id=level.id,
                week_number=week_number,
                session_number=session_number,
                book_name=row["book_name"],
                unit_name=row["unit_name"],
                lesson_title=row["lesson_title"],
                source_reference=row["source_reference"],
                learning_objective=row["learning_objective"],
                planned_homework=row["planned_homework"],
                note_text=row["note_text"],
                status="planned",
                order_index=slot["slot_order"] if slot else index,
            )
        )
        created += 1
    return created


def main() -> None:
    rows = build_plan_rows()
    with app.app_context():
        total_created = 0
        for level_id in TARGET_LEVEL_IDS:
            level = Level.query.get(level_id)
            if not level:
                print(f"SKIPPED level_id={level_id} missing")
                continue
            created = fill_level_plan(level, rows)
            total_created += created
            print(f"CREATED level={level.id} name={level.name} rows={created}")
        db.session.commit()
        print(f"TOTAL_ROWS={total_created}")


if __name__ == "__main__":
    main()
