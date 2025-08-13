"""
Django Admin configuration for Achievement System
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Achievement, UserAchievement, AchievementProgress


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    """
    Admin interface for Achievement model
    """
    list_display = [
        'icon_display', 'name', 'code', 'category', 'difficulty', 
        'points', 'is_repeatable', 'is_active', 'earned_count'
    ]
    list_filter = ['category', 'difficulty', 'is_active', 'is_repeatable', 'requires_verification']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['created_at', 'earned_count']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name', 'description', 'icon')
        }),
        ('Classification', {
            'fields': ('category', 'difficulty', 'points')
        }),
        ('Settings', {
            'fields': ('is_repeatable', 'requires_verification', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_at', 'earned_count'),
            'classes': ('collapse',)
        })
    )
    
    def icon_display(self, obj):
        """Display icon in list view"""
        return obj.icon or '🏆'
    icon_display.short_description = 'Icon'
    
    def earned_count(self, obj):
        """Show how many users earned this achievement"""
        count = obj.user_achievements.count()
        if count > 0:
            url = reverse('admin:achievements_userachievement_changelist')
            return format_html(
                '<a href="{}?achievement__id__exact={}">{} users</a>',
                url, obj.id, count
            )
        return '0 users'
    earned_count.short_description = 'Users Earned'


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    """
    Admin interface for UserAchievement model
    """
    list_display = [
        'user_display', 'achievement_display', 'earned_at', 
        'source_club', 'verification_status', 'points_display'
    ]
    list_filter = [
        'earned_at', 'achievement__category', 'achievement__difficulty',
        'source_club', 'verified_at'
    ]
    search_fields = [
        'user__username', 'user__first_name', 'user__last_name',
        'achievement__name', 'achievement__code'
    ]
    readonly_fields = ['earned_at', 'is_verified_display']
    
    fieldsets = (
        ('Achievement Details', {
            'fields': ('user', 'achievement', 'earned_at')
        }),
        ('Context', {
            'fields': ('source_member', 'source_club', 'progress_data')
        }),
        ('Verification', {
            'fields': ('verified_by', 'verified_at', 'is_verified_display')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        })
    )
    
    def user_display(self, obj):
        """Display user name with link"""
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:auth_user_change', args=[obj.user.id]),
            obj.user.get_full_name() or obj.user.username
        )
    user_display.short_description = 'User'
    user_display.admin_order_field = 'user__username'
    
    def achievement_display(self, obj):
        """Display achievement with icon"""
        return format_html(
            '{} {}',
            obj.achievement.icon or '🏆',
            obj.achievement.name
        )
    achievement_display.short_description = 'Achievement'
    achievement_display.admin_order_field = 'achievement__name'
    
    def verification_status(self, obj):
        """Show verification status"""
        if obj.achievement.requires_verification:
            if obj.verified_at:
                return format_html(
                    '<span style="color: green;">✓ Verified</span>'
                )
            else:
                return format_html(
                    '<span style="color: orange;">⏳ Pending</span>'
                )
        else:
            return format_html(
                '<span style="color: blue;">ℹ️ Auto</span>'
            )
    verification_status.short_description = 'Status'
    
    def points_display(self, obj):
        """Display points earned"""
        return f"+{obj.achievement.points}"
    points_display.short_description = 'Points'
    points_display.admin_order_field = 'achievement__points'
    
    def is_verified_display(self, obj):
        """Display verification status in detail view"""
        return obj.is_verified
    is_verified_display.short_description = 'Is Verified'
    is_verified_display.boolean = True


@admin.register(AchievementProgress)
class AchievementProgressAdmin(admin.ModelAdmin):
    """
    Admin interface for AchievementProgress model
    """
    list_display = [
        'user_display', 'achievement_display', 'progress_display', 
        'updated_at'
    ]
    list_filter = ['updated_at', 'achievement__category']
    search_fields = [
        'user__username', 'user__first_name', 'user__last_name',
        'achievement__name'
    ]
    readonly_fields = ['updated_at', 'progress_percentage_display']
    
    def user_display(self, obj):
        """Display user name with link"""
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:auth_user_change', args=[obj.user.id]),
            obj.user.get_full_name() or obj.user.username
        )
    user_display.short_description = 'User'
    user_display.admin_order_field = 'user__username'
    
    def achievement_display(self, obj):
        """Display achievement with icon"""
        return format_html(
            '{} {}',
            obj.achievement.icon or '🏆',
            obj.achievement.name
        )
    achievement_display.short_description = 'Achievement'
    achievement_display.admin_order_field = 'achievement__name'
    
    def progress_display(self, obj):
        """Display progress bar"""
        try:
            percentage = obj.progress_percentage
            # Ensure percentage is a valid number
            if percentage is None:
                percentage = 0
            percentage = max(0, min(100, float(percentage)))
        except (TypeError, ValueError, AttributeError):
            percentage = 0
        
        # Format percentage for display
        percentage_str = f"{percentage:.1f}"
            
        return format_html(
            '<div style="background: #f0f0f0; border-radius: 3px; overflow: hidden; width: 100px; height: 20px;">'
            '<div style="background: #007cba; height: 100%; width: {}%; transition: width 0.3s;"></div>'
            '</div> {}%',
            percentage, percentage_str
        )
    progress_display.short_description = 'Progress'
    
    def progress_percentage_display(self, obj):
        """Display progress percentage in detail view"""
        try:
            percentage = obj.progress_percentage
            if percentage is None:
                percentage = 0
            return f"{percentage:.1f}%"
        except (TypeError, ValueError, AttributeError):
            return "0.0%"
    progress_percentage_display.short_description = 'Progress Percentage'


# Customize admin site header
admin.site.site_header = "Motomundo Achievement System"
admin.site.site_title = "Motomundo Admin"
admin.site.index_title = "Achievement Management"
