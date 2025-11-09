from django import forms
from django.forms import inlineformset_factory
from .models import (
    BannerItem,
    BannerSlider,
    BannerBackground,
    BottomBannerSlider,
    BottomBannerItem,
)


class BannerSliderForm(forms.ModelForm):
    class Meta:
        model = BannerSlider
        fields = ["title", "is_active", "rotation_time"]


class BannerItemForm(forms.ModelForm):
    class Meta:
        model = BannerItem
        fields = ["image", "url", "text"]


BannerItemFormset = inlineformset_factory(
    BannerSlider,
    BannerItem,
    form=BannerItemForm,
    extra=1,
    can_delete=True,
)


class BannerBackgroundForm(forms.ModelForm):
    class Meta:
        model = BannerBackground
        fields = ["image", "use_image"]


class BottomBannerSliderForm(forms.ModelForm):
    class Meta:
        model = BottomBannerSlider
        fields = ["title", "is_active", "rotation_time"]


class BottomBannerItemForm(forms.ModelForm):
    class Meta:
        model = BottomBannerItem
        fields = ["image", "url"]


BottomBannerItemFormset = inlineformset_factory(
    BottomBannerSlider,
    BottomBannerItem,
    form=BottomBannerItemForm,
    extra=1,
    can_delete=True,
)
