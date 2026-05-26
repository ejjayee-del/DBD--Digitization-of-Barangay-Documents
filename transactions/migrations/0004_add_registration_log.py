# Generated migration for RegistrationLog

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('transactions', '0003_visithistory_certificate_request_and_more'),
    ]

    operations = [
        # Create RegistrationLog model
        migrations.CreateModel(
            name='RegistrationLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('action', models.CharField(
                    choices=[
                        ('registration_submitted', 'Registration Submitted'),
                        ('auto_approved', 'Auto-Approved via Resident List'),
                        ('approved', 'Approved by Staff'),
                        ('rejected', 'Rejected by Staff'),
                        ('resident_added', 'Resident Added'),
                        ('resident_updated', 'Resident Updated'),
                        ('resident_deleted', 'Resident Deleted'),
                    ],
                    max_length=50
                )),
                ('details', models.TextField(blank=True)),
                ('actor', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='registration_logs_created',
                    to=settings.AUTH_USER_MODEL
                )),
                ('subject_user', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='registration_logs',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'verbose_name': 'Registration Log',
                'verbose_name_plural': 'Registration Logs',
                'ordering': ['-timestamp'],
            },
        ),
    ]
