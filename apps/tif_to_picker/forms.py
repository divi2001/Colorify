# myapp/forms.py

from django import forms

class TiffUploadForm(forms.Form):
    tiff_file = forms.FileField()
