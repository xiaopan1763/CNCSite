from django import forms
from .models import Inquiry

class InquiryForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ['company', 'service_type', 'quantity', 'message', 'cad_file']
        widgets = {
            'company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name (Optional)'}),
            'service_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., CNC Machining, 3D Printing', 'required': 'required'}),
            'quantity': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 1-10, 1000+'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Please describe your project requirements, materials, tolerances, etc. *', 'required': 'required'}),
            'cad_file': forms.FileInput(attrs={'class': 'form-control'}),
        }

    # 校验上传文件的大小 (限制 50MB)
    def clean_cad_file(self):
        file = self.cleaned_data.get('cad_file')
        if file and file.size > 50 * 1024 * 1024:
            raise forms.ValidationError("File size must be under 50MB.")
        return file