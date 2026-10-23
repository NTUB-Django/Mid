from captcha.fields import CaptchaField
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import User


class CaptchaAuthenticationForm(AuthenticationForm):
    pass
    captcha = CaptchaField(
        label="安全驗證碼",
        error_messages={
            "invalid": "驗證碼輸入錯誤或已失效，請點擊驗證碼圖片刷新後重新輸入",
            "required": "請輸入圖片中的驗證碼",
        },
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "請輸入學號或管理帳號",
            "autofocus": "autofocus",
        })
        self.fields["password"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "請輸入密碼",
        })
        self.fields["captcha"].widget.attrs.update({
            "class": "form-control captcha-input",
            "placeholder": "請輸入右側驗證碼",
            "autocomplete": "off",
        })


class StudentRegisterForm(UserCreationForm):
    display_name = forms.CharField(label="顯示名稱", max_length=60, required=False)

    class Meta:
        model = User
        fields = ["username", "display_name"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.STUDENT
        user.display_name = self.cleaned_data.get("display_name", "")
        if commit:
            user.save()
        return user
