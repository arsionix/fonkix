from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import SampleUploadForm
from .models import Sample, ModerationStatus


def home(request):
    samples = Sample.objects.filter(status=ModerationStatus.APPROVED).order_by("-uploaded_at")[:8]
    return render(request, "samples/home.html", {"samples": samples})


def catalog(request):
    qs = Sample.objects.filter(status=ModerationStatus.APPROVED)

    q = request.GET.get("q")
    if q:
        qs = qs.filter(title__icontains=q)

    genre = request.GET.get("genre")
    if genre:
        qs = qs.filter(genre=genre)

    qs = qs.order_by("-uploaded_at")

    paginator = Paginator(qs, 24)
    page_number = request.GET.get("page", 1)
    page = paginator.get_page(page_number)

    return render(request, "samples/catalog.html", {"samples": page})


def sample_detail(request, pk):
    sample = get_object_or_404(Sample, pk=pk, status=ModerationStatus.APPROVED)
    related = (
        Sample.objects.filter(
            status=ModerationStatus.APPROVED,
            genre=sample.genre,
        )
        .exclude(pk=pk)
        .order_by("-uploaded_at")[:4]
    )
    return render(
        request,
        "samples/sample_detail.html",
        {
            "sample": sample,
            "related_samples": related,
        },
    )


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    samples = Sample.objects.filter(
        author=profile_user,
        status=ModerationStatus.APPROVED,
    ).order_by("-uploaded_at")
    return render(
        request,
        "samples/profile.html",
        {
            "profile_user": profile_user,
            "samples": samples,
        },
    )


@login_required
def upload(request):
    if request.method == "POST":
        form = SampleUploadForm(request.POST, request.FILES)
        if form.is_valid():
            sample = form.save(commit=False)
            sample.author = request.user
            sample.status = ModerationStatus.PENDING
            sample.save()
            messages.success(request, "Сэмпл отправлен на модерацию.")
            return redirect("home")
    else:
        form = SampleUploadForm()

    return render(request, "samples/upload.html", {"form": form})
