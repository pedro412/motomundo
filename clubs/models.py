import secrets
import string
from django.db import models
from django.db.models.functions import Lower
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils.module_loading import import_string
from django.conf import settings as django_settings
from django.contrib.gis.db import models as gis_models

from motomundo import settings
from geography.models import Country, State


def get_image_storage():
    """Get the flexible image storage instance"""
    storage_path = getattr(django_settings, 'FLEXIBLE_IMAGE_STORAGE', 'clubs.storage_backends.get_flexible_image_storage')
    storage_class = import_string(storage_path)
    return storage_class()


class Club(models.Model):
    CLUB_TYPE_CHOICES = [
        ('mc', 'Motorcycle Club'),
        ('association', 'Association'),
        ('organization', 'Organization'),
        ('riding_group', 'Riding Group'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    foundation_date = models.DateField(null=True, blank=True)
    logo = models.ImageField(
        upload_to='clubs/logos/', 
        blank=True, 
        null=True,
        storage=get_image_storage,
        help_text="Club logo - automatically optimized and stored in the cloud"
    )
    website = models.URLField(blank=True)
    
    # NEW FIELDS FOR DISCOVERY PLATFORM
    # Club type and categorization
    club_type = models.CharField(
        max_length=50, 
        choices=CLUB_TYPE_CHOICES, 
        default='mc',
        help_text="Type of motorcycle organization"
    )
    
    # Geographic information
    country = models.CharField(max_length=100, default='Mexico')  # Keep original field
    country_new = models.ForeignKey(
        Country, 
        on_delete=models.CASCADE, 
        null=True,
        blank=True,
        help_text="Country where this club is primarily located"
    )
    primary_state = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Primary state where this club is located"
    )  # Keep original field
    primary_state_new = models.ForeignKey(
        State,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Primary state where this club is located"
    )
    founded_year = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Year the club was founded"
    )
    
    # Visibility and public settings
    is_public = models.BooleanField(
        default=True,
        help_text="Whether this club appears in public discovery"
    )
    accepts_new_chapters = models.BooleanField(
        default=True,
        help_text="Whether this club accepts requests for new chapters"
    )
    
    # Contact information for discovery
    contact_email = models.EmailField(
        blank=True,
        help_text="Contact email for inquiries about joining this club"
    )
    
    # Auto-calculated statistics for discovery
    total_members = models.PositiveIntegerField(
        default=0,
        help_text="Total active members across all chapters (auto-updated)"
    )
    total_chapters = models.PositiveIntegerField(
        default=0,
        help_text="Total active chapters (auto-updated)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['country', 'primary_state']),
            models.Index(fields=['club_type']),
            models.Index(fields=['is_public']),
        ]

    def __str__(self):
        return self.name
    
    def update_stats(self):
        """Update total_members and total_chapters counts"""
        # Count active chapters
        self.total_chapters = self.chapters.filter(is_active=True).count()
        
        # Count active members across all active chapters
        from django.db.models import Q
        self.total_members = Member.objects.filter(
            chapter__club=self,
            chapter__is_active=True,
            is_active=True
        ).count()
        
        self.save(update_fields=['total_members', 'total_chapters'])
    
    @property 
    def total_members_legacy(self):
        """Count all active members across all chapters in this club (legacy property)"""
        from django.db.models import Q
        return Member.objects.filter(
            chapter__club=self,
            is_active=True
        ).count()


class Chapter(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="chapters")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    foundation_date = models.DateField(null=True, blank=True)
    
    # NEW FIELDS FOR DISCOVERY PLATFORM
    # Geographic location for discovery
    city = models.CharField(
        max_length=100,
        blank=True,
        help_text="City where this chapter is located"
    )
    state = models.CharField(
        max_length=100,
        blank=True,
        help_text="State where this chapter is located"
    )  # Keep original field
    state_new = models.ForeignKey(
        State,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="State where this chapter is located"
    )
    # TODO: Add GeoDjango support for location field
    location = gis_models.PointField(
        null=True, 
        blank=True,
        help_text="Geographic coordinates for map display",
        srid=4326  # WGS84 coordinate system
    )
    
    # Chapter ownership for management
    owner = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="owned_chapters",
        null=True,
        blank=True,
        help_text="User who owns and manages this chapter"
    )
    
    # Visibility and activity settings
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this chapter is active and operational"
    )
    is_public = models.BooleanField(
        default=True,
        help_text="Whether this chapter appears in public discovery"
    )
    accepts_new_members = models.BooleanField(
        default=True,
        help_text="Whether this chapter is accepting new members"
    )
    
    # Additional chapter information
    meeting_info = models.TextField(
        blank=True,
        help_text="Information about chapter meetings (time, place, etc.)"
    )
    contact_email = models.EmailField(
        blank=True,
        help_text="Contact email for this chapter"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["club", "name"], name="unique_chapter_name_per_club"),
        ]
        ordering = ["name"]
        indexes = [
            models.Index(fields=['state', 'city']),
            models.Index(fields=['club', 'is_active']),
            models.Index(fields=['is_public', 'is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.club.name})"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Auto-update parent club stats whenever chapter changes
        if self.club_id:
            self.club.update_stats()
    
    def can_manage(self, user):
        """Check if user can manage this chapter"""
        return user == self.owner

class Member(models.Model):
    ROLE_CHOICES = [
        ('president', 'President'),
        ('vice_president', 'Vice President'),
        ('secretary', 'Secretary'),
        ('treasurer', 'Treasurer'),
        ('road_captain', 'Road Captain'),
        ('sergeant_at_arms', 'Sergeant at Arms'),
        ('member', 'Member'),
        # Add more roles as needed
    ]
    
    NATIONAL_ROLE_CHOICES = [
        ('', '-- Sin rol nacional --'),  # Default empty option
        ('national_president', 'National President'),
        ('national_vice_president', 'National Vice President'),
        ('national_secretary', 'National Secretary'),
        ('national_counselor', 'National Counselor'),
        ('zone_vp_south', 'Zone Vice President South'),
        ('zone_vp_center', 'Zone Vice President Center'), 
        ('zone_vp_north', 'Zone Vice President North'),
    ]
    
    MEMBER_TYPE_CHOICES = [
        ('pilot', 'Pilot'),
        ('copilot', 'Copilot'),
        ('prospect', 'Prospect'),
    ]
    
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name="members")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    nickname = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    member_type = models.CharField(max_length=20, choices=MEMBER_TYPE_CHOICES, default='pilot')
    national_role = models.CharField(max_length=50, choices=NATIONAL_ROLE_CHOICES, blank=True, default='')
    profile_picture = models.ImageField(
        upload_to='members/profiles/', 
        blank=False,
        storage=get_image_storage,
        help_text="Member profile picture - automatically optimized and stored in the cloud"
    )
    joined_at = models.DateField(null=True, blank=True)
    
    # User linkage and claim flow
    user = models.ForeignKey(
        to='auth.User', null=True, blank=True, on_delete=models.SET_NULL,
        help_text="Link to a registered user, if applicable.",
        related_name='memberships'
    )
    claim_code = models.CharField(
        max_length=50, unique=True, null=True, blank=True,
        help_text="Unique code that allows a user to claim this member profile"
    )
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True, help_text="Additional member metadata")
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
    
    @property
    def club(self):
        """Get the club this member belongs to through their chapter"""
        return self.chapter.club if self.chapter else None
    
    def generate_claim_code(self):
        """Generate a unique claim code for this member"""
        while True:
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            if not Member.objects.filter(claim_code=code).exists():
                self.claim_code = code
                break
        return self.claim_code

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


class ChapterJoinRequest(models.Model):
    """
    Simplified requests to create chapters under existing clubs
    """
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    club = models.ForeignKey(
        Club, 
        on_delete=models.CASCADE, 
        related_name="join_requests",
        help_text="Club the user wants to create a chapter under"
    )
    requested_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        help_text="User requesting to create the chapter"
    )
    
    # Proposed chapter information
    proposed_chapter_name = models.CharField(
        max_length=200,
        help_text="Name for the proposed chapter"
    )
    city = models.CharField(
        max_length=100,
        help_text="City where the chapter will be located"
    )
    state = models.CharField(
        max_length=100,
        help_text="State where the chapter will be located"
    )  # Keep original field
    state_new = models.ForeignKey(
        State,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="State where the chapter will be located"
    )
    description = models.TextField(
        help_text="Description of the proposed chapter"
    )
    reason = models.TextField(
        help_text="Why the user wants to join this club"
    )
    estimated_members = models.PositiveIntegerField(
        help_text="Estimated number of initial members"
    )
    
    # Request status and management
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    admin_notes = models.TextField(
        blank=True,
        help_text="Notes from admin review"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['club', 'status']),
            models.Index(fields=['requested_by', 'status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.proposed_chapter_name} - {self.club.name} ({self.status})"
    
    def approve(self, admin_notes=""):
        """
        Approve the join request and create the chapter
        """
        from django.utils import timezone
        
        if self.status != 'pending':
            raise ValueError("Can only approve pending requests")
        
        # Create the chapter
        chapter = Chapter.objects.create(
            name=self.proposed_chapter_name,
            club=self.club,
            city=self.city,
            state=self.state,
            state_new=self.state_new,
            description=self.description,
            owner=self.requested_by,
            is_public=True,  # Default to public
            accepts_new_members=True  # Default to accepting members
        )
        
        # Update the request
        self.status = 'approved'
        self.admin_notes = admin_notes
        self.reviewed_at = timezone.now()
        self.save()
        
        # Update club stats
        self.club.update_stats()
        
        return chapter
    
    def reject(self, admin_notes=""):
        """
        Reject the join request
        """
        from django.utils import timezone
        
        if self.status != 'pending':
            raise ValueError("Can only reject pending requests")
        
        self.status = 'rejected'
        self.admin_notes = admin_notes
        self.reviewed_at = timezone.now()
        self.save()
        
        return self


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