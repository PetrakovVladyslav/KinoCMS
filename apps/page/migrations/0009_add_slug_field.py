# Generated manually to add slug field safely

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('page', '0008_pagenewssales_logo'),
    ]

    operations = [
        # First add the slug field without unique constraint
        migrations.AddField(
            model_name='pageelse',
            name='slug',
            field=models.SlugField(max_length=120, blank=True, null=True, verbose_name='Слаг (для URL)'),
        ),
        # Update model options
        migrations.AlterModelOptions(
            name='pageelse',
            options={'ordering': ['-status', 'name'], 'verbose_name': 'Дополнительная страница', 'verbose_name_plural': 'Дополнительные страницы'},
        ),
        # Update other fields
        migrations.AlterField(
            model_name='pageelse',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='page/logo', verbose_name='Баннер/Логотип'),
        ),
        migrations.AlterField(
            model_name='pageelse',
            name='status',
            field=models.BooleanField(default=False, verbose_name='Включена'),
        ),
    ]