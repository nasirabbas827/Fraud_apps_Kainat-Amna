from django.db import models
from django.utils import timezone

class user_register(models.Model):
    id = models.AutoField(primary_key=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    full_name = models.CharField(max_length=255)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)
    age = models.PositiveIntegerField()

    def __str__(self):
        return self.username


class Application(models.Model):
    app_id = models.AutoField(primary_key=True)
    category = models.CharField(max_length=50)
    app_name = models.CharField(max_length=150)
    app_link = models.URLField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    app_image = models.ImageField(upload_to='app_images/', blank=True, null=True)

    FRAUD_STATUS_CHOICES = [
        ('genuine', 'Genuine'),
        ('fraud', 'Fraud'),
    ]
    fraud_status = models.CharField(
        max_length=10,
        choices=FRAUD_STATUS_CHOICES,
        default='genuine'
    )

    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.app_name


class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(user_register, on_delete=models.CASCADE)
    app = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(default=1)
    comment = models.TextField()

    sentiment_score = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)

    SENTIMENT_CHOICES = [
        ('Positive', 'Positive'),
        ('Negative', 'Negative'),
        ('Neutral', 'Neutral'),
    ]
    sentiment_label = models.CharField(
        max_length=10,
        choices=SENTIMENT_CHOICES,
        default='Neutral'
    )

    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.app.app_name}"


from django.db import models
from django.utils import timezone

class SystemFeedback(models.Model):
    feedback_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('user_register', on_delete=models.CASCADE)
    message = models.TextField()

    STATUS_CHOICES = [
        ('Unread', 'Unread'),
        ('Read', 'Read'),
    ]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='Unread'
    )

    submitted_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.status}"
