from django import forms
from .models import Product


class ProductAdminForm(forms.ModelForm):
    sizes = forms.MultipleChoiceField(
        choices=Product.SIZE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Product
        fields = '__all__'

    def clean_sizes(self):
        return self.cleaned_data['sizes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and isinstance(self.instance.sizes, list):
            self.initial['sizes'] = self.instance.sizes
