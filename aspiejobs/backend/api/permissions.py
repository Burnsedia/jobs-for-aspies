from rest_framework.exceptions import PermissionDenied

def ensure_user_can_post_job(user):
    """
    Central guard for whether a user is allowed to post a job.
    Reuse this anywhere you create Job objects.
    """
    if not user.is_authenticated:
        raise PermissionDenied("You must be logged in to post jobs.")

    if user.role != "COMPANY":
        raise PermissionDenied("Only company accounts may post jobs.")

    if not hasattr(user, "company_account") or user.company_account is None:
        raise PermissionDenied("Create your company profile first.")

    # Unlimited if they have an active subscription (via dj-stripe)
    if user.has_active_subscription:
        return

    # Otherwise, require a one-time job posting credit
    if not user.has_active_job_posting_plan:
        raise PermissionDenied(
            "You must buy a job posting credit or subscribe for unlimited posting."
        )
