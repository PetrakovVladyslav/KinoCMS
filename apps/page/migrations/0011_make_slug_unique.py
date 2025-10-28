# Final migration to make slug field unique and not null

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('page', '0010_populate_slugs'),
    ]

    operations = [
        # Now make slug unique and not null since all records have slugs
        migrations.AlterField(
            model_name='pageelse',
            name='slug',
            field=models.SlugField(max_length=120, unique=True, blank=True, verbose_name='Слаг (для URL)'),
        ),
    ]