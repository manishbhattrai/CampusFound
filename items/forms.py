from .models import Category,Item,Claim
from django import forms



class ReportItemForm(forms.ModelForm):

    class Meta:
        model = Item
        fields = ['item_name','description','image','location','status','category',
                  'verification_question','date_happened']

        widgets = {
            'date_happened': forms.DateInput(attrs={'type':'date'})
        }

    def clean_image(self):

        image = self.cleaned_data.get("image")

        MAX_SIZE = 10*1024*1024

        if image:
            if image.size > MAX_SIZE:
                raise forms.ValidationError("Image should be less than 10MB.")

        return image

    def clean(self):
        cleaned_data = super().clean()

        status = cleaned_data.get("status")
        question = cleaned_data.get("verification_question")

        if status in ['lost','recovered'] and question:
            self.add_error('verification_question',
                           'This field is only for found reports.')

        if status == 'found' and not question:
            self.add_error('verification_question',
                           'This field is required when item is found.')

        return cleaned_data

class ClaimForm(forms.ModelForm):

    class Meta:
        model = Claim
        fields = ['verification_answer','proof_image']


    def clean_image(self):

        image = self.cleaned_data.get("proof_image")

        MAX_SIZE = 5*1024*1024
        if image:
            if image.size > MAX_SIZE:
                raise forms.ValidationError("Image should be less than 5MB.")

        return image

class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = ['name','description']