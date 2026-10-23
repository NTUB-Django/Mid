from django.conf import settings
from django.db import models


COLOR_CHOICES = [
    ("terracotta", "湖水藍"),
    ("blue", "海灣藍"),
    ("green", "森林綠"),
    ("amber", "晴空藍"),
    ("purple", "晨霧藍"),
    ("slate", "石板藍"),
]


class Selection(models.Model):
    class Status(models.TextChoices):
        PRE = "pre", "預選中"
        SELECTED = "selected", "正取"
        REJECTED = "rejected", "未選上"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="使用者", related_name="selections"
    )
    offering = models.ForeignKey(
        "courses.Offering", on_delete=models.CASCADE, verbose_name="開課", related_name="selections"
    )
    status = models.CharField("狀態", max_length=20, choices=Status.choices, default=Status.SELECTED, db_index=True)
    notes = models.CharField("個人備註", max_length=100, blank=True)
    color = models.CharField("標籤顏色", max_length=20, choices=COLOR_CHOICES, default="terracotta")
    created_at = models.DateTimeField("加入時間", auto_now_add=True)

    class Meta:
        verbose_name = "個人課表課程"
        verbose_name_plural = "個人課表課程"
        ordering = ["created_at"]
        constraints = [models.UniqueConstraint(fields=["user", "offering"], name="uniq_selection_user_offering")]

    def __str__(self):
        return f"{self.user} → {self.offering} [{self.get_status_display()}]"


class CustomSchedule(models.Model):
    WEEKDAY_CHOICES = [
        (1, "星期一"),
        (2, "星期二"),
        (3, "星期三"),
        (4, "星期四"),
        (5, "星期五"),
        (6, "星期六"),
        (7, "星期日"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="使用者",
        related_name="custom_schedules",
    )
    title = models.CharField("行程名稱", max_length=100)
    weekday = models.PositiveSmallIntegerField("星期", choices=WEEKDAY_CHOICES, db_index=True)
    period = models.CharField("節次名稱", max_length=30, blank=True)
    start = models.TimeField("開始時間")
    end = models.TimeField("結束時間")
    location = models.CharField("地點/教室", max_length=60, blank=True)
    color = models.CharField("標籤顏色", max_length=20, choices=COLOR_CHOICES, default="blue")
    note = models.TextField("備註說明", blank=True)
    created_at = models.DateTimeField("建立時間", auto_now_add=True)
    updated_at = models.DateTimeField("更新時間", auto_now=True)

    class Meta:
        verbose_name = "個人自訂行程"
        verbose_name_plural = "個人自訂行程"
        ordering = ["weekday", "start"]

    def __str__(self):
        return f"{self.user}：{self.get_weekday_display()} {self.title}（{self.start:%H:%M}-{self.end:%H:%M}）"
