from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.gis.admin import GISModelAdmin
from .models import Club, Chapter, Member, ClubAdmin, ChapterAdmin, UserClubContext, ChapterJoinRequest


class ChapterInline(admin.TabularInline):
	model = Chapter
	extra = 1
	fields = ('name', 'city', 'state_new', 'location', 'owner', 'is_public', 'accepts_new_members', 'is_active')
	readonly_fields = ()


class JoinRequestInline(admin.TabularInline):
	model = ChapterJoinRequest
	extra = 0
	fields = ('proposed_chapter_name', 'requested_by', 'city', 'state_new', 'status', 'created_at')
	readonly_fields = ('created_at',)
	can_delete = False


@admin.register(Club)
class ClubModelAdmin(admin.ModelAdmin):
	list_display = ("name", "club_type", "country_new", "primary_state_new", "is_public", "accepts_new_chapters", "total_members", "total_chapters", "foundation_date")
	list_filter = ("club_type", "country_new", "primary_state_new", "is_public", "accepts_new_chapters", "foundation_date")
	search_fields = ("name", "description", "country_new__name", "primary_state_new__name")
	readonly_fields = ("created_at", "updated_at", "total_members", "total_chapters")
	fields = (
		("name", "club_type"),
		"description", 
		("foundation_date", "logo"), 
		("country_new", "primary_state_new"),
		("is_public", "accepts_new_chapters"),
		("website",),
		("total_members", "total_chapters"),
		("created_at", "updated_at")
	)
	inlines = [ChapterInline, JoinRequestInline]
	
	def save_model(self, request, obj, form, change):
		obj.save()
		# Update stats after saving
		obj.update_stats()


@admin.register(Chapter)
class ChapterModelAdmin(GISModelAdmin):
	list_display = ("name", "club", "city", "state_new", "owner", "is_public", "accepts_new_members", "foundation_date", "is_active")
	list_filter = ("club", "state_new", "is_public", "accepts_new_members", "is_active", "foundation_date")
	search_fields = ("name", "club__name", "city", "state_new__name", "description")
	readonly_fields = ("created_at", "updated_at")
	fields = (
		("name", "club"),
		"description",
		("city", "state_new"),
		"location",  # Map widget will be automatically added
		("owner",),
		("foundation_date",),
		("is_public", "accepts_new_members"),
		("contact_email", "meeting_info"),
		("is_active",),
		("created_at", "updated_at")
	)
	
	# GIS Admin settings for interactive map
	gis_widget_kwargs = {
		'attrs': {
			'default_zoom': 12,
			'display_wkt': False,
			'map_srid': 4326,
		},
	}
	
	def save_model(self, request, obj, form, change):
		obj.save()
		# Update club stats after saving chapter
		if obj.club:
			obj.club.update_stats()

@admin.register(Member)
class MemberModelAdmin(admin.ModelAdmin):
	list_display = ("first_name", "last_name", "nickname", "role", "chapter", "joined_at", "is_active")
	list_filter = ("chapter", "role", "is_active")
	search_fields = ("first_name", "last_name", "nickname", "chapter__name")


class ClubAdminInline(admin.TabularInline):
	model = ClubAdmin
	extra = 0
	readonly_fields = ('created_at', 'created_by')


class ChapterAdminInline(admin.TabularInline):
	model = ChapterAdmin
	extra = 0
	readonly_fields = ('created_at', 'created_by')


@admin.register(ClubAdmin)
class ClubAdminModelAdmin(admin.ModelAdmin):
	list_display = ('user', 'club', 'created_at', 'created_by')
	list_filter = ('club', 'created_at')
	search_fields = ('user__username', 'user__first_name', 'user__last_name', 'club__name')
	readonly_fields = ('created_at', 'created_by')

	def save_model(self, request, obj, form, change):
		if not change:  # Only set created_by for new objects
			obj.created_by = request.user
		obj.save()


@admin.register(ChapterAdmin)
class ChapterAdminModelAdmin(admin.ModelAdmin):
	list_display = ('user', 'chapter', 'created_at', 'created_by')
	list_filter = ('chapter__club', 'chapter', 'created_at')
	search_fields = ('user__username', 'user__first_name', 'user__last_name', 'chapter__name', 'chapter__club__name')
	readonly_fields = ('created_at', 'created_by')

	def save_model(self, request, obj, form, change):
		if not change:  # Only set created_by for new objects
			obj.created_by = request.user
		obj.save()


@admin.register(UserClubContext)
class UserClubContextModelAdmin(admin.ModelAdmin):
	list_display = ('user', 'active_club', 'updated_at')
	list_filter = ('active_club', 'updated_at')
	search_fields = ('user__username', 'user__first_name', 'user__last_name', 'active_club__name')


@admin.register(ChapterJoinRequest)
class ChapterJoinRequestModelAdmin(admin.ModelAdmin):
	list_display = ('proposed_chapter_name', 'club', 'requested_by', 'city', 'state_new', 'status', 'created_at', 'reviewed_at')
	list_filter = ('status', 'club', 'state_new', 'created_at', 'reviewed_at')
	search_fields = ('proposed_chapter_name', 'club__name', 'requested_by__username', 'requested_by__first_name', 'requested_by__last_name', 'city', 'state_new__name')
	readonly_fields = ('created_at', 'reviewed_at')
	fields = (
		('proposed_chapter_name', 'club'),
		('requested_by',),
		('city', 'state_new'),
		'description',
		'reason',
		('estimated_members',),
		('status',),
		'admin_notes',
		('created_at', 'reviewed_at')
	)
	
	actions = ['approve_requests', 'reject_requests']
	
	def approve_requests(self, request, queryset):
		"""Bulk approve selected join requests"""
		approved_count = 0
		for join_request in queryset.filter(status='pending'):
			try:
				join_request.approve(admin_notes=f"Bulk approved by {request.user.username}")
				approved_count += 1
			except Exception as e:
				self.message_user(request, f"Error approving {join_request.proposed_chapter_name}: {str(e)}", level='ERROR')
		
		if approved_count > 0:
			self.message_user(request, f"Successfully approved {approved_count} join requests and created chapters.")
	approve_requests.short_description = "Approve selected join requests"
	
	def reject_requests(self, request, queryset):
		"""Bulk reject selected join requests"""
		rejected_count = 0
		for join_request in queryset.filter(status='pending'):
			try:
				join_request.reject(admin_notes=f"Bulk rejected by {request.user.username}")
				rejected_count += 1
			except Exception as e:
				self.message_user(request, f"Error rejecting {join_request.proposed_chapter_name}: {str(e)}", level='ERROR')
		
		if rejected_count > 0:
			self.message_user(request, f"Successfully rejected {rejected_count} join requests.")
	reject_requests.short_description = "Reject selected join requests"
