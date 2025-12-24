# Generated manually for Atlanta tech board updates

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_company_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='remote_level',
            field=models.CharField(blank=True, choices=[('FULL_REMOTE', 'Fully Remote'), ('HYBRID_OPTIONAL', 'Hybrid Optional'), ('HYBRID_REQUIRED', 'Hybrid Required'), ('ONSITE', 'On-site Required')], db_index=True, help_text='Remote work policy for this position', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='async_level',
            field=models.CharField(blank=True, choices=[('FULL_ASYNC', 'Fully Asynchronous'), ('MOSTLY_ASYNC', 'Mostly Asynchronous'), ('SOME_SYNC', 'Some Synchronous Work'), ('TRADITIONAL', 'Traditional Schedule')], db_index=True, help_text='Asynchronous work level required', max_length=20, null=True),
        ),
        migrations.RenameField(
            model_name='job',
            old_name='tags',
            new_name='tech_tags',
        ),
        migrations.RemoveField(
            model_name='job',
            name='sensory_warnings',
        ),
        migrations.RemoveField(
            model_name='job',
            name='interview_accommodations',
        ),
        migrations.RemoveField(
            model_name='job',
            name='is_autism_friendly',
        ),
        migrations.AddField(
            model_name='job',
            name='benefits',
            field=models.TextField(blank=True, help_text='Company benefits and perks', null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='interview_process',
            field=models.TextField(blank=True, help_text='Description of interview process', null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='is_remote_friendly',
            field=models.BooleanField(default=False, help_text='Company has strong remote work culture'),
        ),
    ]