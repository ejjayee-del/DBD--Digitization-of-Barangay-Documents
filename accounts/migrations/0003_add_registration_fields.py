# Generated migration for registration system

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_customuser_role'),
    ]

    operations = [
        # Add registration fields to CustomUser
        migrations.AddField(
            model_name='customuser',
            name='status',
            field=models.CharField(
                choices=[('pending', 'Pending Approval'), ('approved', 'Approved'), ('rejected', 'Rejected')],
                default='approved',
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='customuser',
            name='registration_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='rejection_reason',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='address',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='birthday',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='contact_number',
            field=models.CharField(blank=True, max_length=20),
        ),
        # Create BarangayResident model
        migrations.CreateModel(
            name='BarangayResident',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=300)),
                ('address', models.TextField()),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('added_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='residents_added', to='accounts.customuser')),
            ],
            options={
                'verbose_name': 'Barangay Resident',
                'verbose_name_plural': 'Barangay Residents',
                'ordering': ['full_name'],
            },
        ),
    ]
