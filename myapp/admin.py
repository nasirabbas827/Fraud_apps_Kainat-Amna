from django.contrib import admin
from django.db.models import Avg
from .models import user_register, Application, Review, SystemFeedback

# ===============================
# User Admin
# ===============================
@admin.register(user_register)
class UserRegisterAdmin(admin.ModelAdmin):
    list_display = ('username', 'full_name', 'email', 'gender', 'age')
    search_fields = ('username', 'full_name', 'email')
    list_filter = ('gender',)


# ===============================
# Application Admin
# ===============================
@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('app_name', 'category', 'fraud_status', 'created_at', 'average_rating', 'average_sentiment')
    search_fields = ('app_name', 'category')
    list_filter = ('category', 'fraud_status')

    # Custom methods to calculate averages
    def average_rating(self, obj):
        avg = obj.reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
        return round(avg, 2) if avg else 0
    average_rating.short_description = 'Avg Rating'

    def average_sentiment(self, obj):
        avg = obj.reviews.aggregate(avg_sentiment=Avg('sentiment_score'))['avg_sentiment']
        return round(avg, 3) if avg else 0
    average_sentiment.short_description = 'Avg Sentiment Score'


# ===============================
# Review Admin
# ===============================
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'app', 'rating', 'sentiment_label', 'sentiment_score', 'created_at')
    search_fields = ('user__username', 'app__app_name', 'comment')
    list_filter = ('sentiment_label', 'rating')


# ===============================
# System Feedback Admin
# ===============================
@admin.register(SystemFeedback)
class SystemFeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'submitted_at', 'short_message')
    search_fields = ('user__username', 'message')
    list_filter = ('status',)

    # Show first 50 chars of message in list display
    def short_message(self, obj):
        return (obj.message[:50] + '...') if len(obj.message) > 50 else obj.message
    short_message.short_description = 'Message Preview'
