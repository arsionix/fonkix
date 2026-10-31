import os

from django import forms

from .models import Sample

MAX_SIZE_MB = 50
ALLOWED_EXTENSIONS = {".wav", ".mp3"}


class SampleUploadForm(forms.ModelForm):
    class Meta:
        model = Sample
        fields = ["title", "genre", "bpm", "musical_key", "audio_file"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Например, Hard Cowbell"}),
            "bpm": forms.NumberInput(attrs={"min": 60, "max": 200}),
            "musical_key": forms.TextInput(attrs={"placeholder": "Am, F#m (необязательно)"}),
        }

    def clean_audio_file(self):
        f = self.cleaned_data["audio_file"]
        ext = os.path.splitext(f.name)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise forms.ValidationError("Только WAV или MP3.")
        if f.size > MAX_SIZE_MB * 1024 * 1024:
            raise forms.ValidationError(f"Файл больше {MAX_SIZE_MB} МБ.")
        return f
