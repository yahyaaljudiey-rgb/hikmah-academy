from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import app, build_instructional_slot_sequence
from models import SyllabusPlanEntry, db


TARGET_LEVEL_ID = 8
BOOK_NAME = "العربية بين يديك - الكتاب الثالث - الجزء الأول"

LESSON_BLUEPRINTS = [
    ("النص القرائي", "قراءة النص الرئيس وفهم فكرته العامة والتفصيلية.", "إعادة قراءة النص وتلخيص فكرته."),
    ("المفردات والتعبيرات", "اكتساب مفردات الوحدة والتعبيرات الواردة فيها.", "مراجعة المفردات واستعمالها في جمل."),
    ("القواعد اللغوية 1", "فهم القاعدة الأولى في الوحدة وتطبيقها.", "حل تدريبات القاعدة الأولى."),
    ("فهم المسموع", "تنمية مهارة الاستماع والفهم السمعي.", "الاستماع المنزلي ومراجعة الفكرة الرئيسة."),
    ("التعبير الشفهي والكتابي", "تنمية مهارات التعبير حول موضوع الوحدة.", "إعداد فقرة أو عرض قصير."),
    ("الإملاء", "تقوية مهارة الإملاء والكتابة الصحيحة.", "تدريبات إملائية منزلية."),
    ("التدريبات العامة", "مراجعة شاملة لمهارات الوحدة ومفرداتها.", "استكمال التدريبات العامة ومراجعتها."),
]

UNITS = [
    {"unit_number": 1, "title": "الهجرة الخالدة", "start_page": 1},
    {"unit_number": 2, "title": "يوم في حياة ناشئ", "start_page": 20},
    {"unit_number": 3, "title": "أقليّاتنا في العالم", "start_page": 40},
    {"unit_number": 4, "title": "السنة النبوية", "start_page": 60},
    {"unit_number": 5, "title": "الأطفال والقراءة", "start_page": 86},
]


def build_rows() -> list[dict]:
    rows: list[dict] = []
    for unit in UNITS:
        unit_number = unit["unit_number"]
        unit_title = unit["title"]
        unit_name = f"الوحدة {unit_number}: {unit_title}"

        for lesson_index, (lesson_title, objective, homework) in enumerate(LESSON_BLUEPRINTS, start=1):
            rows.append(
                {
                    "book_name": BOOK_NAME,
                    "unit_name": unit_name,
                    "lesson_title": f"{unit_title} - {lesson_title}",
                    "source_reference": f"الوحدة {unit_number} - الدرس {lesson_index} - تبدأ من صفحة {unit['start_page']}",
                    "learning_objective": objective,
                    "planned_homework": homework,
                    "note_text": f"الوحدة {unit_number} - الدرس {lesson_index}",
                }
            )

        if unit_number in (2, 4):
            paired_unit = unit_number - 1
            rows.append(
                {
                    "book_name": BOOK_NAME,
                    "unit_name": f"مراجعة الوحدتين {paired_unit}-{unit_number}",
                    "lesson_title": f"مراجعة الوحدتين {paired_unit}-{unit_number}",
                    "source_reference": f"مراجعة الوحدتين {paired_unit}-{unit_number}",
                    "learning_objective": f"مراجعة شاملة للوحدتين {paired_unit} و{unit_number}.",
                    "planned_homework": f"حل مراجعة الوحدتين {paired_unit} و{unit_number}.",
                    "note_text": f"مراجعة الوحدتين {paired_unit}-{unit_number}",
                }
            )
    return rows


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
        rows = build_rows()

        created = 0
        for slot, row in zip(remaining_slots, rows):
            db.session.add(
                SyllabusPlanEntry(
                    level_id=TARGET_LEVEL_ID,
                    week_number=slot["academic_week_number"],
                    session_number=slot["session_number"],
                    book_name=row["book_name"],
                    unit_name=row["unit_name"],
                    lesson_title=row["lesson_title"],
                    source_reference=row["source_reference"],
                    learning_objective=row["learning_objective"],
                    planned_homework=row["planned_homework"],
                    note_text=row["note_text"],
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
