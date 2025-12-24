# Generated manually for Atlanta tech board updates

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_company_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='atlanta_neighborhood',
            field=models.CharField(blank=True, choices=[('MIDTOWN', 'Midtown'), ('TECH_SQUARE', 'Tech Square'), ('PONCE_CITY', 'Ponce City Market'), ('CENTENNIAL_PARK', 'Centennial Park'), ('EAV', 'East Atlanta Village'), ('LITTLE_FIVE', 'Little Five Points'), ('GRANT_PARK', 'Grant Park'), ('WESTSIDE', 'Westside'), ('VIRGINIA_HIGHLAND', 'Virginia Highland'), ('DECATUR', 'Decatur'), ('SANDY_SPRINGS', 'Sandy Springs'), ('ROSWELL', 'Roswell'), ('MARIETTA', 'Marietta'), ('ALPHARETTA', 'Alpharetta'), ('DULUTH', 'Duluth'), ('JOHNSCREEK', 'Johns Creek'), ('SMYRNA', 'Smyrna'), ('KENNESAW', 'Kennesaw'), ('OTHER', 'Other Atlanta Area')], db_index=True, help_text='Specific Atlanta neighborhood or metro area location', max_length=20, null=True),
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