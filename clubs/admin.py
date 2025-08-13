from django.contrib import admin
from django.contrib.auth.models import User
from .models import Club, Chapter, Member, ClubAdmin, ChapterManager


class ChapterInline(admin.TabularInline):
	model = Chapter
	extra = 1


@admin.register(Club)
class ClubModelAdmin(admin.ModelAdmin):
	list_display = ("name", "foundation_date", "website", "created_at", "updated_at")
	search_fields = ("name", "website")
	readonly_fields = ("created_at", "updated_at")
	fields = ("name", "description", "foundation_date", "logo", "website", "created_at", "updated_at")
	inlines = [ChapterInline]


@admin.register(Chapter)
class ChapterModelAdmin(admin.ModelAdmin):
	list_display = ("name", "club", "foundation_date", "created_at", "updated_at")
	list_filter = ("club",)
	search_fields = ("name", "club__name")

@admin.register(Member)
class MemberModelAdmin(admin.ModelAdmin):
	list_display = ("first_name", "last_name", "nickname", "role", "chapter", "joined_at", "is_active")
	list_filter = ("chapter", "role", "is_active")
	search_fields = ("first_name", "last_name", "nickname", "chapter__name")


class ClubAdminInline(admin.TabularInline):
	model = ClubAdmin
	extra = 0
	readonly_fields = ('created_at', 'created_by')


class ChapterManagerInline(admin.TabularInline):
	model = ChapterManager
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


@admin.register(ChapterManager)
class ChapterManagerModelAdmin(admin.ModelAdmin):
	list_display = ('user', 'chapter', 'created_at', 'created_by')
	list_filter = ('chapter__club', 'chapter', 'created_at')
	search_fields = ('user__username', 'user__first_name', 'user__last_name', 'chapter__name', 'chapter__club__name')
	readonly_fields = ('created_at', 'created_by')

	def save_model(self, request, obj, form, change):
		if not change:  # Only set created_by for new objects
			obj.created_by = request.user
		obj.save()
