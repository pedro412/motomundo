from django.db import models
from django.db.models.functions import Lower
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from motomundo import settings


class Club(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    foundation_date = models.DateField(null=True, blank=True)
    logo = models.ImageField(upload_to="clubs/logos/", null=True, blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Chapter(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="chapters")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    foundation_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["club", "name"], name="unique_chapter_name_per_club"),
        ]
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.club.name})"

class Member(models.Model):
    ROLE_CHOICES = [
        ('president', 'President'),
        ('vice_president', 'Vice President'),
        ('secretary', 'Secretary'),
        ('treasurer', 'Treasurer'),
        ('rider', 'Rider'),
        # Add more roles as needed
    ]
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name="members")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    nickname = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    joined_at = models.DateField(null=True, blank=True)
    user = models.ForeignKey(
        to='auth.User', null=True, blank=True, on_delete=models.SET_NULL,
        help_text="Link to a registered user, if applicable.",
        related_name='memberships'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['first_name', 'last_name']
        constraints = [
            models.UniqueConstraint(
                Lower('first_name'), Lower('last_name'), 'chapter',
                name='uq_member_chapter_fullname_ci'
            ),
            models.UniqueConstraint(
                fields=['user', 'chapter'],
                name='uq_user_chapter_membership',
                condition=models.Q(user__isnull=False)
            )
        ]

    def __str__(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return f"{full_name} ({self.role}) - {self.chapter.name}"

    def clean(self):
        # Normalize names and enforce case-insensitive uniqueness within a chapter
        self.first_name = (self.first_name or '').strip()
        self.last_name = (self.last_name or '').strip()

        if self.chapter_id is None or not self.first_name:
            return

        qs = Member.objects.filter(
            chapter_id=self.chapter_id,
            first_name__iexact=self.first_name,
            last_name__iexact=self.last_name,
        )
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError({
                'first_name': 'A member with the same name already exists in this chapter.',
                'last_name': 'A member with the same name already exists in this chapter.',
            })

    def save(self, *args, **kwargs):
        # Ensure validation runs on programmatic saves as well
        self.full_clean()
        return super().save(*args, **kwargs)


class ClubAdmin(models.Model):
    """
    Represents a user who can manage a specific club and all its chapters
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='club_admin_roles')
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='admins')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, 
        related_name='created_club_admins'
    )

    class Meta:
        unique_together = ['user', 'club']
        ordering = ['club__name', 'user__username']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - Admin of {self.club.name}"


class ChapterAdmin(models.Model):
    """
    Represents a user who can manage members of a specific chapter
    Users can have multiple ChapterAdmin roles across different clubs
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chapter_admin_roles')
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='admins')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='created_chapter_admins'
    )

    class Meta:
        unique_together = ['user', 'chapter']
        ordering = ['chapter__club__name', 'chapter__name', 'user__username']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - Admin of {self.chapter.name}"


class UserClubContext(models.Model):
    """
    Tracks the user's currently active club context for performing actions
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='active_club_context')
    active_club = models.ForeignKey(Club, on_delete=models.CASCADE, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Club Context"
        verbose_name_plural = "User Club Contexts"

    def __str__(self):
        if self.active_club:
            return f"{self.user.username} - Active: {self.active_club.name}"
        return f"{self.user.username} - No active club"