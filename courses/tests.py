import io
import json
import tempfile
from pathlib import Path

from django.core.management import call_command
from django.test import TestCase

from .models import Course, Offering, OfferingSlot, StudentClass


class CourseBootstrapTests(TestCase):
    def test_initial_import_is_persistent_and_does_not_overwrite_existing_data(self):
        record = {
            'query_ok': True, 'edu_code': '4', 'edu_name': '四技',
            'dept_code': '401', 'dept_name': '資管', 'class_code': '401A', 'class_name': '一年甲班',
            'sessions': [{'課程代號': 'TEST101', '課程名稱': '資料庫', '序號': '1',
                          '教師': '測試老師', '星期': '一', '節次': '第一節',
                          '開始時間': '08:10', '結束時間': '09:00', '教室': 'A101'}],
        }
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'courses.jsonl'
            source.write_text(json.dumps(record), encoding='utf-8')
            call_command('import_courses', file=str(source), if_empty=True, stdout=io.StringIO())
            self.assertEqual(Course.objects.count(), 1)
            self.assertEqual(OfferingSlot.objects.count(), 1)
            self.assertEqual(StudentClass.objects.count(), 1)
            offering = Offering.objects.get()
            offering.capacity = 75
            offering.save(update_fields=['capacity'])
            source.unlink()
            call_command('import_courses', file=str(source), if_empty=True, stdout=io.StringIO())
            offering.refresh_from_db()
            self.assertEqual(offering.capacity, 75)
            self.assertEqual(Offering.objects.count(), 1)
