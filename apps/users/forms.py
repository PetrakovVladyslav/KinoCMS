from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.validators import RegexValidator
from django.utils.html import strip_tags

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        max_length=100,
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"}),
    )
    first_name = forms.CharField(
        required=True,
        max_length=50,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Имя"}),
    )
    last_name = forms.CharField(
        required=True,
        max_length=50,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Фамилия"}),
    )
    password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Пароль"}),
    )
    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Подтвердите пароль"}),
    )

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Этот email уже зарегистрирован")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email
        if commit:
            user.save()
        return user


class CustomUserLoginForm(AuthenticationForm):
    username = forms.CharField(
        required=True,
        max_length=100,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Email"}),
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Пароль"}),
    )

    def clean(self):
        email = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if email and password:
            self.user_cache = authenticate(self.request, email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError("Неправильный email или пароль")
        return self.cleaned_data


class CustomUserUpdateForm(forms.ModelForm):
    password1 = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        label="Пароль",
    )
    password2 = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        label="Повторить пароль",
    )

    nickname = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Псевдоним",
    )

    gender = forms.ChoiceField(
        choices=[("male", "Мужской"), ("female", "Женский")],
        required=False,
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        label="Пол",
    )

    language = forms.ChoiceField(
        choices=[("ru", "Русский"), ("uk", "Українська")],
        required=False,
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        label="Язык",
    )

    phone_number = forms.CharField(
        required=False,
        max_length=10,
        validators=[
            RegexValidator(
                r"^0\d{9}$",
                "Введите номер в формате: 0990000000 (10 цифр, начиная с 0)",
            )
        ],
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "0990000000",
                "maxlength": "10",
                "pattern": "0[0-9]{9}",
            }
        ),
        label="Телефон",
    )

    card_number = forms.CharField(
        required=False,
        validators=[RegexValidator(r"^\d{16}$", "Введите 16 цифр номера карты")],
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "maxlength": "16",
                "placeholder": "1234567812345678",
                "pattern": "[0-9]{16}",
            }
        ),
        label="Номер карты",
    )

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "nickname",
            "email",
            "address",
            "card_number",
            "phone_number",
            "date_of_birth",
            "city",
        )
        labels = {
            "first_name": "Имя",
            "last_name": "Фамилия",
            "nickname": "Псевдоним",
            "email": "E-mail",
            "address": "Адрес",
            "card_number": "Номер карты",
            "date_of_birth": "Дата рождения",
            "city": "Город",
        }
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "nickname": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "address": forms.TextInput(attrs={"class": "form-control"}),
            "date_of_birth": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "city": forms.Select(attrs={"class": "form-select"}),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise forms.ValidationError("Email уже зарегистрирован")
        return email

    def clean_nickname(self):
        nickname = self.cleaned_data.get("nickname")
        if nickname and User.objects.filter(nickname=nickname).exclude(id=self.instance.id).exists():
            raise forms.ValidationError("Псевдоним уже используется")
        return nickname

    def clean(self):
        cleaned_data = super().clean()
        text_fields = [
            "first_name",
            "last_name",
            "email",
            "address",
            "phone_number",
            "card_number",
            "nickname",
        ]
        for field in text_fields:
            if cleaned_data.get(field):
                cleaned_data[field] = strip_tags(cleaned_data[field])

        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("Пароли не совпадают")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password1 = self.cleaned_data.get("password1")
        gender = self.cleaned_data.get("gender")
        language = self.cleaned_data.get("language")

        if gender:
            user.gender = gender
        if language:
            user.language = language

        if password1:
            user.set_password(password1)

        if commit:
            user.save()

        return user
