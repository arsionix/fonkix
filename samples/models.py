import uuid
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.validators import (
    FileExtensionValidator,
    MinValueValidator,
    MaxValueValidator,
)
from django.db import models
from django.utils import timezone
from django.conf import settings


class Genre(models.TextChoices):
    DRIFT = "drift", "Drift Phonk"
    BRAZILIAN = "brazilian", "Brazilian Phonk"
    ATMOSPHERIC = "atmospheric", "Atmospheric Phonk"
    WAVE = "wave", "Wave Phonk"
    MEMPHIS = "memphis", "Memphis Phonk"
    CLASSIC = "classic", "Classic Phonk"


class ModerationStatus(models.TextChoices):
    PENDING = "pending", "На модерации"
    APPROVED = "approved", "Одобрено"
    REJECTED = "rejected", "Отклонено"


def sample_upload_path(instance: "Sample", filename: str) -> str:
    ext = Path(filename).suffix.lower()
    return f"samples/{timezone.now():%Y/%m}/{uuid.uuid4().hex}{ext}"


def validate_file_size(file) -> None:
    max_size = 50 * 1024 * 1024
    if file.size > max_size:
        raise ValidationError("Файл слишком большой: максимум 50 МБ.")


class Sample(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField("Название", max_length=200)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="samples",
        verbose_name="Автор",
    )
    genre = models.CharField("Поджанр", max_length=20, choices=Genre.choices)

    bpm = models.PositiveSmallIntegerField(
        "BPM",
        validators=[MinValueValidator(60), MaxValueValidator(200)],
        help_text="Темп от 60 до 200 BPM",
    )
    musical_key = models.CharField(
        "Тональность",
        max_length=5,
        blank=True,
        help_text="Например: Am, F#m, C",
    )

    audio_file = models.FileField(
        "Аудиофайл",
        upload_to=sample_upload_path,
        validators=[
            FileExtensionValidator(allowed_extensions=["mp3", "wav"]),
            validate_file_size,
        ],
    )

    status = models.CharField(
        "Статус модерации",
        max_length=10,
        choices=ModerationStatus.choices,
        default=ModerationStatus.PENDING,
        db_index=True,
    )

    uploaded_at = models.DateTimeField("Загружено", auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]
        indexes = [
            models.Index(fields=["genre", "bpm"], name="idx_sample_genre_bpm"),
            models.Index(fields=["bpm"], name="idx_sample_bpm"),
        ]
        verbose_name = "Сэмпл"
        verbose_name_plural = "Сэмплы"

    def __str__(self) -> str:
        return f"{self.title} ({self.get_genre_display()}, {self.bpm} BPM)"
