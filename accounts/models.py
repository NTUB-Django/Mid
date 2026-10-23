from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "student", "學生端"
        SCHOOL = "school", "學校端(教務/行政)"
        ADMIN = "admin", "最高管理員(Admin)"

    role = models.CharField("角色", max_length=20, choices=Role.choices, default=Role.STUDENT)
    display_name = models.CharField("顯示名稱", max_length=60, blank=True)
    student_class = models.ForeignKey(
        "courses.StudentClass",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="所屬班級",
        related_name="students",
    )

    class Meta:
        verbose_name = "帳號"
        verbose_name_plural = "帳號"

    def __str__(self):
        return f"{self.username}（{self.get_role_display()}）"

    def save(self, *args, **kwargs):
        pass





        if self.role == self.Role.ADMIN:
            self.is_staff = True
            self.is_superuser = True
        elif self.role == self.Role.SCHOOL:
            self.is_staff = True
            self.is_superuser = False
        elif self.role == self.Role.STUDENT and not self.is_superuser:
            self.is_staff = False
            self.is_superuser = False
        super().save(*args, **kwargs)

    @property
    def is_admin_role(self) -> bool:
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_school_role(self) -> bool:
        return self.role == self.Role.SCHOOL

    @property
    def is_student_role(self) -> bool:
        return self.role == self.Role.STUDENT

    @property
    def can_manage_school(self) -> bool:
        return self.is_school_role or self.is_admin_role
