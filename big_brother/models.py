from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.contrib.auth.hashers import make_password, check_password


class Participant(models.Model):
    USER_STATUS = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('moderator', 'Moderator'),
        ('viewer', 'Viewer'),
        ('simple', 'Simple'),
    )

    # Basic information
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)  # Store hashed passwords
    nickname = models.CharField(max_length=50)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=150, blank=True)

    # Status and role
    status = models.CharField(max_length=10, choices=USER_STATUS, default='active')
    date_inactive = models.DateField(blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='simple')

    # Relationships
    assigned_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                    limit_choices_to={'role__in': ['admin', 'moderator']})

    # Media
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} - {self.nickname}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def save(self, *args, **kwargs):
        # If password is not hashed yet, hash it
        if not self.password.startswith('pbkdf2_sha256$'):
            self.set_password(self.password)
        super().save(*args, **kwargs)


class Phone(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='phones')
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    number = models.CharField(validators=[phone_regex], max_length=17)

    def __str__(self):
        return self.number


class Email(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='emails')
    email = models.EmailField()

    def __str__(self):
        return self.email


class HistoricalRecord(models.Model):
    RECORD_TYPES = (
        ('activity', 'Activity'),
        ('activity_address', 'Activity Address'),
        ('job', 'Job'),
        ('job_address', 'Job Address'),
        ('address', 'Address'),
    )

    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='history')
    record_type = models.CharField(max_length=20, choices=RECORD_TYPES)
    value = models.TextField()
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.participant.username} - {self.record_type} - {self.changed_at}"
