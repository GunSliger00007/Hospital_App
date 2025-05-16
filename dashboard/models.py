from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Address(models.Model):
    line1 = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.line1}, {self.city}, {self.state}, {self.pincode}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/', default='default.png',null=False)
    line1 = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

    class Meta:
        abstract = True

class Patient(Profile):
    medical_history = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} (Patient)"

class Doctor(Profile):
    specialty = models.CharField(max_length=100)
    license_number = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.user.username} (Doctor)"
    
CATEGORY_CHOICES = [
    ('mental_health', 'Mental Health'),
    ('heart_disease', 'Heart Disease'),
    ('covid_19', 'COVID-19'),
    ('immunization', 'Immunization'),
]

class Blog_Post(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='blog/images/', null=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    summary = models.TextField()
    content = models.TextField()
    author = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    draft = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
    ]

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    time = models.TimeField()
    end_time = models.TimeField(blank=True,null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    required_speciality = models.TextField(default="Full Body")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    google_event_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Appointment with {self.doctor.user.username} on {self.date} at {self.time}"