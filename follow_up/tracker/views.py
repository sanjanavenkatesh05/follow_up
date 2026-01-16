from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import Http404, HttpResponseForbidden
from .models import FollowUp, PublicViewLog
from .forms import FollowUpForm
from django.db.models import Count, Q
from django.utils import timezone
import datetime

@login_required
def dashboard(request):
    user_profile = getattr(request.user, 'userprofile', None)
    if not user_profile:
        # Handle case where user has no profile/clinic
        return render(request, "tracker/dashboard.html", {"error": "No clinic assigned to this user."})
    
    clinic = user_profile.clinic
    followups = FollowUp.objects.filter(clinic=clinic).annotate(view_count=Count('view_logs')).order_by("due_date")

    # Filtering
    status_filter = request.GET.get("status")
    if status_filter:
        followups = followups.filter(status=status_filter)

    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")
    if date_from:
        followups = followups.filter(due_date__gte=date_from)
    if date_to:
        followups = followups.filter(due_date__lte=date_to)

    # Summary Counts
    total_count = followups.count()
    pending_count = followups.filter(status="pending").count()
    done_count = followups.filter(status="done").count()

    context = {
        "followups": followups,
        "total_count": total_count,
        "pending_count": pending_count,
        "done_count": done_count,
    }
    return render(request, "tracker/dashboard.html", context)


@login_required
def create_followup(request):
    if request.method == "POST":
        form = FollowUpForm(request.POST)
        if form.is_valid():
            followup = form.save(commit=False)
            followup.clinic = request.user.userprofile.clinic
            followup.created_by = request.user
            followup.save()
            messages.success(request, f"Follow-up for {followup.patient_name} created successfully!")
            return redirect("dashboard")
    else:
        form = FollowUpForm()
    return render(request, "tracker/followup_form.html", {"form": form, "title": "Create Follow-up"})


@login_required
def edit_followup(request, pk):
    followup = get_object_or_404(FollowUp, pk=pk)
    
    # Access Control
    if followup.clinic != request.user.userprofile.clinic:
        return HttpResponseForbidden("You cannot edit follow-ups from another clinic.")

    if request.method == "POST":
        form = FollowUpForm(request.POST, instance=followup)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    else:
        form = FollowUpForm(instance=followup)
    return render(request, "tracker/followup_form.html", {"form": form, "title": "Edit Follow-up"})


@login_required
@require_POST
def mark_done(request, pk):
    followup = get_object_or_404(FollowUp, pk=pk)
    
    # Access Control
    if followup.clinic != request.user.userprofile.clinic:
        return HttpResponseForbidden("You cannot modify follow-ups from another clinic.")

    followup.status = "done"
    followup.save()
    return redirect("dashboard")


def public_followup(request, token):
    followup = get_object_or_404(FollowUp, public_token=token)
    
    # Log the view
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
        
    PublicViewLog.objects.create(
        followup=followup,
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        ip_address=ip
    )


    message = "Please visit our clinic for your follow-up."
    if followup.language == 'hi':
        message = "कृपया अपने फॉलो-अप के लिए हमारे क्लिनिक आएं।"

    return render(request, "tracker/public_page.html", {"followup": followup, "message": message})
