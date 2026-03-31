from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import app, build_instructional_slot_sequence
from models import Level, SyllabusPlanEntry, db


BOOK_NAME = "العربية بين يديك - الكتاب الثاني - الجزء الأول"
TARGET_LEVEL_ID = 7

LESSON_BLUEPRINTS = [
    ("الحوار الأول وتدريباته", "تدريس الحوار الأول واستخراج المفردات الأساسية.", "مراجعة الحوار الأول والتدرب على مفرداته."),
    ("الأصوات", "تدريب الطالب على أصوات الوحدة والتمييز السمعي.", "مراجعة النطق والتدرب على الكلمات الجديدة."),
    ("الملاحظة النحوية الأولى", "فهم القاعدة النحوية الأولى في الوحدة وتطبيقها.", "حل أمثلة قصيرة على القاعدة الأولى."),
    ("فهم المسموع والكلام 1", "تنمية الاستماع والكلام في سياق موضوع الوحدة.", "تدرب شفهي قصير من موضوع الدرس."),
    ("النص القرائي الأول", "تنمية القراءة والفهم للنص الأول.", "قراءة النص الأول والإجابة عن أسئلته."),
    ("الملاحظة النحوية الثانية", "فهم القاعدة الثانية وتطبيقها في أمثلة متنوعة.", "حل تدريبات القاعدة الثانية."),
    ("الكلام 2", "توسيع التدريب الشفهي باستخدام مفردات وتراكيب الوحدة.", "إعداد عرض شفهي قصير."),
    ("النص القرائي الثاني", "تنمية الفهم القرائي للنص الثاني.", "قراءة النص الثاني ومراجعته."),
    ("الملاحظة الصرفية", "فهم الملاحظة الصرفية وربطها بأمثلة الوحدة.", "تطبيق الملاحظة الصرفية في أمثلة."),
    ("فهم المسموع والكلام 2", "تعزيز مهارات الاستماع والكلام في سياقات أوسع.", "استماع منزلي وتلخيص شفهي."),
    ("الكتابة", "تنمية الكتابة الموجهة حول موضوع الوحدة.", "إنجاز كتابة قصيرة حول موضوع الدرس."),
    ("الإملاء", "تقوية مهارة الإملاء والتمييز الكتابي.", "تدريبات إملائية منزلية."),
    ("التدريبات العامة", "مراجعة شاملة لمهارات ومفردات الوحدة.", "حل التدريبات العامة واستكمال النواقص."),
]

UNITS = [
    {"unit_number": 1, "title": "العناية بالصحة", "start_page": 1},
    {"unit_number": 2, "title": "الترويح عن النفس", "start_page": 23, "review_start_page": None},
    {"unit_number": 3, "title": "الحياة الزوجية", "start_page": 49},
    {"unit_number": 4, "title": "الحياة في المدينة", "start_page": 71, "review_start_page": None},
    {"unit_number": 5, "title": "العلم والتعلّم", "start_page": 97},
    {"unit_number": 6, "title": "المهن", "start_page": 119, "review_start_page": None},
    {"unit_number": 7, "title": "اللغة العربية", "start_page": 145},
    {"unit_number": 8, "title": "الجوائز", "start_page": 167, "review_start_page": None},
]

# صفحات الدروس الدقيقة غير متوفرة بعد للكتاب الثاني، لذا نعتمد مرجع بداية الوحدة
# حتى تزودنا لاحقاً ببدايات المراجعات أو توزيع صفحات الدروس.


def build_plan_rows() -> list[dict]:
    rows: list[dict] = []
    order_index = 0

    for unit in UNITS:
        unit_number = unit["unit_number"]
        unit_title = unit["title"]
        unit_name = f"الوحدة {unit_number}: {unit_title}"

        for lesson_index, (lesson_title, objective, homework) in enumerate(LESSON_BLUEPRINTS, start=1):
            order_index += 1
            rows.append(
                {
                    "order_index": order_index,
                    "book_name": BOOK_NAME,
                    "unit_name": unit_name,
                    "lesson_title": f"{unit_title} - {lesson_title}",
                    "source_reference": f"الوحدة {unit_number} - الدرس {lesson_index} - تبدأ من صفحة {unit['start_page']}",
                    "learning_objective": objective,
                    "planned_homework": homework,
                    "note_text": f"الوحدة {unit_number} - الدرس {lesson_index}",
                }
            )

        if unit_number % 2 == 0:
            paired_unit = unit_number - 1
            order_index += 1
            rows.append(
                {
                    "order_index": order_index,
                    "book_name": BOOK_NAME,
                    "unit_name": f"مراجعة الوحدتين {paired_unit}-{unit_number}",
                    "lesson_title": f"مراجعة الوحدتين {paired_unit}-{unit_number}",
                    "source_reference": f"مراجعة الوحدتين {paired_unit}-{unit_number}",
                    "learning_objective": f"مراجعة شاملة لمهارات ومفردات وتراكيب الوحدتين {paired_unit} و{unit_number}.",
                    "planned_homework": f"حل تدريبات مراجعة الوحدتين {paired_unit} و{unit_number}.",
                    "note_text": f"مراجعة الوحدتين {paired_unit}-{unit_number}",
                }
            )

    return rows


def fill_level_plan(level: Level, rows: list[dict]) -> tuple[int, int]:
    existing_rows = SyllabusPlanEntry.query.filter_by(level_id=level.id).all()
    for row in existing_rows:
        db.session.delete(row)

    slots = build_instructional_slot_sequence()
    created = 0
    unscheduled = 0
    for index, row in enumerate(rows, start=1):
        slot = slots[index - 1] if index - 1 < len(slots) else None
        week_number = slot["academic_week_number"] if slot else None
        session_number = slot["session_number"] if slot else None
        if slot is None:
            unscheduled += 1
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
    return created, unscheduled


def main() -> None:
    rows = build_plan_rows()
    with app.app_context():
        level = Level.query.get(TARGET_LEVEL_ID)
        if not level:
            print(f"SKIPPED level_id={TARGET_LEVEL_ID} missing")
            return
        created, unscheduled = fill_level_plan(level, rows)
        db.session.commit()
        print(f"CREATED level={level.id} name={level.name} rows={created} unscheduled={unscheduled}")


if __name__ == "__main__":
    main()
