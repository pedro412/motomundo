from django.contrib import admin
from .models import Club, Chapter, Member


class ChapterInline(admin.TabularInline):
	model = Chapter
	extra = 1


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
	list_display = ("name", "foundation_date", "website", "created_at", "updated_at")
	search_fields = ("name", "website")
	readonly_fields = ("created_at", "updated_at")
	fields = ("name", "description", "foundation_date", "logo", "website", "created_at", "updated_at")
	inlines = [ChapterInline]


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
	list_display = ("name", "club", "foundation_date", "created_at", "updated_at")
	list_filter = ("club",)
	search_fields = ("name", "club__name")

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
	list_display = ("first_name", "last_name", "nickname", "role", "chapter", "joined_at", "is_active")
	list_filter = ("chapter", "role", "is_active")
	search_fields = ("first_name", "last_name", "nickname", "chapter__name")
