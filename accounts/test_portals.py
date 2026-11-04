from django.contrib.auth import authenticate
from django.test import Client, TestCase
from django.urls import reverse
import re

from .models import GroupMembership, SharingGroup, User


class PortalCsrfTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.student = User.objects.create_user(username="csrf_student", email="csrf-student@example.com", password="Portal-test-password-905")
        cls.school = User.objects.create_user(username="csrf_school", email="csrf-school@example.com", password="Portal-test-password-905", role=User.Role.SCHOOL)
        cls.admin = User.objects.create_superuser(username="admin", password="Portal-test-password-905", role=User.Role.ADMIN)

    def setUp(self):
        self.browser = Client(enforce_csrf_checks=True)

    def form_token(self, path):
        response = self.browser.get(path, secure=True)
        self.assertEqual(response.status_code, 200)
        return re.search(r'name="csrfmiddlewaretoken" value="([A-Za-z0-9]+)"', response.content.decode()).group(1)

    def submit_login(self, path, token, identifier):
        from captcha.models import CaptchaStore
        key = CaptchaStore.generate_key()
        answer = CaptchaStore.objects.get(hashkey=key).response
        return self.browser.post(path, {
            "csrfmiddlewaretoken": token, "username": identifier,
            "password": "Portal-test-password-905", "captcha_0": key, "captcha_1": answer,
        }, secure=True, HTTP_ORIGIN="https://testserver")

    def test_student_login_does_not_invalidate_an_open_school_login_form(self):
        school_token = self.form_token("/school/login/")
        student_token = self.form_token("/accounts/login/")
        self.assertEqual(self.submit_login("/accounts/login/", student_token, self.student.email).status_code, 302)
        response = self.submit_login("/school/login/", school_token, self.school.email)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/school/")
        self.assertEqual(self.browser.get("/school/", secure=True).status_code, 200)
        self.assertEqual(self.browser.get("/selection/timetable/", secure=True).status_code, 200)

    def test_school_login_does_not_invalidate_an_open_admin_login_form(self):
        admin_token = self.form_token("/admin/login/")
        school_token = self.form_token("/school/login/")
        self.assertEqual(self.submit_login("/school/login/", school_token, self.school.email).status_code, 302)
        self.assertEqual(self.submit_login("/admin/login/", admin_token, "admin").status_code, 302)
        self.assertEqual(self.browser.get("/admin/", secure=True).status_code, 200)
        self.assertEqual(self.browser.get("/school/", secure=True).status_code, 200)

    def test_csrf_token_from_another_portal_is_rejected(self):
        school_token = self.form_token("/school/login/")
        self.form_token("/accounts/login/")
        response = self.submit_login("/accounts/login/", school_token, self.student.email)
        self.assertEqual(response.status_code, 403)

    def test_missing_token_has_a_safe_uncached_retry_page(self):
        response = self.submit_login("/school/login/", "", self.school.email)
        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "重新開啟學校端登入", status_code=403)
        self.assertNotContains(response, "DEBUG=True", status_code=403)
        self.assertNotContains(response, "Portal-test-password-905", status_code=403)
        self.assertIn("no-store", response["Cache-Control"])

    def test_untrusted_origin_stays_rejected_and_does_not_log_in(self):
        token = self.form_token("/school/login/")
        response = self.browser.post("/school/login/", {"csrfmiddlewaretoken": token}, secure=True, HTTP_ORIGIN="https://untrusted.example")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.browser.get("/school/", secure=True).status_code, 302)

    def test_legacy_shared_cookie_cannot_replace_a_portal_session(self):
        token = self.form_token("/school/login/")
        self.browser.cookies["csrftoken"] = "x" * 32
        self.assertEqual(self.submit_login("/school/login/", token, self.school.email).status_code, 302)

    def test_expired_session_can_recover_through_a_fresh_login_form(self):
        stale = self.form_token("/school/login/")
        self.browser.cookies.pop("mid_school_session")
        rejected = self.submit_login("/school/login/", stale, self.school.email)
        self.assertEqual(rejected.status_code, 403)
        fresh = self.form_token("/school/login/")
        self.assertEqual(self.submit_login("/school/login/", fresh, self.school.email).status_code, 302)

    def test_school_logout_does_not_invalidate_a_student_form(self):
        token = self.form_token("/accounts/login/")
        self.assertEqual(self.submit_login("/accounts/login/", token, self.student.email).status_code, 302)
        school_token = self.form_token("/school/login/")
        self.assertEqual(self.submit_login("/school/login/", school_token, self.school.email).status_code, 302)
        student_form = self.form_token("/accounts/profile/")
        logout_token = self.form_token("/school/")
        self.assertEqual(self.browser.post("/school/logout/", {"csrfmiddlewaretoken": logout_token}, secure=True, HTTP_ORIGIN="https://testserver").status_code, 302)
        response = self.browser.post("/accounts/profile/", {
            "csrfmiddlewaretoken": student_form, "form_kind": "email", "email": self.student.email,
            "current_password": "Portal-test-password-905",
        }, secure=True, HTTP_ORIGIN="https://testserver")
        self.assertEqual(response.status_code, 302)


class PortalSessionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.student = User.objects.create_user(username="s123456", email="student@example.com", password="Safe-student-pass-905")
        cls.teacher = User.objects.create_user(username="teacher1", email="teacher@example.com", password="Safe-teacher-pass-905", role=User.Role.SCHOOL)
        cls.admin = User.objects.create_superuser(username="admin", password="Safe-admin-pass-905", role=User.Role.ADMIN)

    def scoped_login(self, user, name):
        separate = Client()
        separate.force_login(user)
        self.client.cookies[name] = separate.cookies["mid_student_session"].value

    def test_email_only_with_admin_exception(self):
        self.assertIsNone(authenticate(username="s123456", password="Safe-student-pass-905"))
        self.assertEqual(authenticate(username="STUDENT@EXAMPLE.COM", password="Safe-student-pass-905"), self.student)
        self.assertIsNone(authenticate(username="teacher1", password="Safe-teacher-pass-905"))
        self.assertEqual(authenticate(username="teacher@example.com", password="Safe-teacher-pass-905"), self.teacher)
        self.assertEqual(authenticate(username="admin", password="Safe-admin-pass-905"), self.admin)

    def test_three_sessions_coexist_and_school_logout_is_scoped(self):
        self.scoped_login(self.student, "mid_student_session")
        self.scoped_login(self.teacher, "mid_school_session")
        self.scoped_login(self.admin, "mid_admin_session")
        self.assertEqual(self.client.get(reverse("selection:timetable")).status_code, 200)
        self.assertEqual(self.client.get(reverse("school:dashboard")).status_code, 200)
        self.assertEqual(self.client.get(reverse("admin:index")).status_code, 200)
        self.assertEqual(self.client.get(reverse("admin:accounts_user_add")).status_code, 200)
        self.assertEqual(self.client.get(reverse("admin:accounts_user_change", args=[self.student.pk])).status_code, 200)
        self.assertEqual(self.client.get(reverse("admin:index")).status_code, 200)
        school_page = self.client.get(reverse("school:dashboard"))
        self.assertIn("no-store", school_page["Cache-Control"])
        self.client.post(reverse("school:logout"))
        self.assertEqual(self.client.get(reverse("school:dashboard")).status_code, 302)
        self.assertEqual(self.client.get(reverse("selection:timetable")).status_code, 200)
        self.assertEqual(self.client.get(reverse("admin:index")).status_code, 200)

    def test_old_console_leads_to_admin_and_student_cannot_enter_school(self):
        self.scoped_login(self.student, "mid_student_session")
        self.assertEqual(self.client.get(reverse("selection:console_dashboard")).url, reverse("admin:index"))
        self.assertEqual(self.client.get(reverse("school:dashboard")).url, reverse("school:login"))


class GroupWorkspaceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(username="owner1", email="owner@example.com")
        cls.member = User.objects.create_user(username="member1", email="member@example.com")
        cls.pending = User.objects.create_user(username="pending1", email="pending@example.com")
        cls.group = SharingGroup.objects.create(owner=cls.owner, name="共同討論")
        GroupMembership.objects.create(group=cls.group, user=cls.member, accepted=True)
        GroupMembership.objects.create(group=cls.group, user=cls.pending, accepted=False)

    def test_accepted_member_can_work_and_pending_member_cannot(self):
        self.client.force_login(self.member)
        page = self.client.get(reverse("accounts:group_workspace", args=[self.group.pk]))
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "共同待辦")
        task_url = reverse("accounts:group_task_create", args=[self.group.pk])
        response = self.client.post(task_url, {"title": "交報告"})
        self.assertEqual(response.status_code, 302)
        task = self.group.tasks.get()
        event_url = reverse("accounts:group_event_create", args=[self.group.pk])
        self.client.post(event_url, {
            "title": "小組討論", "starts_at": "2026-10-30T09:00", "ends_at": "2026-10-30T10:00",
            "location": "圖書館", "color": "red",
        })
        self.assertEqual(self.group.events.get().color, "red")
        self.client.post(reverse("accounts:group_task_toggle", args=[self.group.pk, task.pk]))
        task.refresh_from_db()
        self.assertTrue(task.completed)
        self.client.force_login(self.pending)
        self.assertEqual(self.client.get(reverse("accounts:group_workspace", args=[self.group.pk])).status_code, 404)
        self.assertEqual(self.client.post(task_url, {"title": "不該加入"}).status_code, 404)
        self.assertEqual(self.client.post(event_url, {"title": "不該加入"}).status_code, 404)

    def test_group_memo_editable_by_member_and_revoked_on_leave(self):
        self.client.force_login(self.owner)
        self.client.post(reverse("accounts:group_memo_create", args=[self.group.pk]), {"title": "分工", "body": "第一版"})
        memo = self.group.memos.get()
        self.client.force_login(self.member)
        self.client.post(reverse("accounts:group_memo_edit", args=[self.group.pk, memo.pk]), {"title": "分工", "body": "第二版"})
        memo.refresh_from_db()
        self.assertEqual(memo.body, "第二版")
        self.assertEqual(self.client.post(reverse("accounts:group_memo_delete", args=[self.group.pk, memo.pk])).status_code, 403)
        GroupMembership.objects.filter(group=self.group, user=self.member).delete()
        self.assertEqual(self.client.get(reverse("accounts:group_memo_edit", args=[self.group.pk, memo.pk])).status_code, 404)


class RegistrationIdempotencyTests(TestCase):
    def test_register_logs_in_once_and_rejects_replayed_form(self):
        response = self.client.get(reverse("accounts:register"))
        token = response.context["register_token"]
        old_cookie = self.client.cookies["mid_student_session"].value
        data = {
            "register_token": token, "username": "s789012", "email": "new@example.com",
            "password1": "Safe-registered-pass-905", "password2": "Safe-registered-pass-905",
        }
        self.assertEqual(self.client.post(reverse("accounts:register"), data).status_code, 302)
        home = self.client.get(reverse("courses:home"))
        self.assertEqual(home.status_code, 200)
        self.assertContains(home, 'data-operation-success')
        self.assertContains(home, 'id="operation-dialog"')
        replay = Client()
        replay.cookies["mid_student_session"] = old_cookie
        self.assertNotEqual(replay.post(reverse("accounts:register"), data).status_code, 302)
        self.assertEqual(User.objects.filter(username="s789012").count(), 1)
