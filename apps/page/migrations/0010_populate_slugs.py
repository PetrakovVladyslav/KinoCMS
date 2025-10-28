# Data migration to populate slug fields

from django.db import migrations
from django.utils.text import slugify


def populate_slugs(apps, schema_editor):
    """Populate slug field for existing PageElse records"""
    PageElse = apps.get_model('page', 'PageElse')
    
    for page in PageElse.objects.all():
        if not page.slug:  # Only update empty slugs
            base_slug = slugify(page.name)
            if not base_slug:
                base_slug = f'page-{page.pk}'
            
            # Ensure uniqueness
            unique_slug = base_slug
            counter = 1
            while PageElse.objects.filter(slug=unique_slug).exclude(pk=page.pk).exists():
                unique_slug = f'{base_slug}-{counter}'
                counter += 1
            
            page.slug = unique_slug
            page.save()


def reverse_populate_slugs(apps, schema_editor):
    """Reverse migration - clear slugs"""
    PageElse = apps.get_model('page', 'PageElse')
    PageElse.objects.all().update(slug='')


class Migration(migrations.Migration):

    dependencies = [
        ('page', '0009_add_slug_field'),
    ]

    operations = [
        migrations.RunPython(
            populate_slugs,
            reverse_populate_slugs
        ),
    ]