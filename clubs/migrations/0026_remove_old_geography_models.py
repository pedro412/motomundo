# Generated manually to safely remove old Country/State models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0025_add_member_metadata'),
        ('geography', '0003_alter_state_unique_together_country_boundary_and_more'),
    ]

    operations = [
        # First, update the foreign key fields to point to geography models
        migrations.AlterField(
            model_name='club',
            name='country_new',
            field=models.ForeignKey(
                blank=True, 
                help_text='Country where this club is primarily located', 
                null=True, 
                on_delete=django.db.models.deletion.CASCADE, 
                to='geography.country'
            ),
        ),
        migrations.AlterField(
            model_name='club',
            name='primary_state_new',
            field=models.ForeignKey(
                blank=True, 
                help_text='Primary state where this club is located', 
                null=True, 
                on_delete=django.db.models.deletion.SET_NULL, 
                to='geography.state'
            ),
        ),
        migrations.AlterField(
            model_name='chapter',
            name='state_new',
            field=models.ForeignKey(
                blank=True, 
                help_text='State where this chapter is located', 
                null=True, 
                on_delete=django.db.models.deletion.SET_NULL, 
                to='geography.state'
            ),
        ),
        migrations.AlterField(
            model_name='chapterjoinrequest',
            name='state_new',
            field=models.ForeignKey(
                blank=True, 
                help_text='State where the chapter will be located', 
                null=True, 
                on_delete=django.db.models.deletion.SET_NULL, 
                to='geography.state'
            ),
        ),
        
        # Now safely remove the old models
        # Django will automatically drop the tables since no model references them
        migrations.RunSQL(
            "DROP TABLE IF EXISTS clubs_state CASCADE;",
            reverse_sql="-- Cannot reverse table drop"
        ),
        migrations.RunSQL(
            "DROP TABLE IF EXISTS clubs_country CASCADE;",
            reverse_sql="-- Cannot reverse table drop"
        ),
    ]
