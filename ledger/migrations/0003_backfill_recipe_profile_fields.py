from django.utils import timezone
from django.db import migrations


def backfill_recipe_profile_fields(apps, schema_editor):
    User = apps.get_model("auth", "User")
    Profile = apps.get_model("ledger", "Profile")
    Recipe = apps.get_model("ledger", "Recipe")

    user, _ = User.objects.get_or_create(
        username="legacy_author",
        defaults={
            "email": "legacy_author@example.com",
            "password": "!",
            "is_active": True,
            "is_staff": False,
            "is_superuser": False,
        },
    )
    profile, _ = Profile.objects.get_or_create(
        user=user,
        defaults={
            "name": "Legacy Author",
            "short_bio": (
                "Legacy author profile created for migration compatibility. "
                "This account owns pre-existing recipes so that historical data "
                "remains valid after enforcing required author relationships in "
                "the recipe model and preserving created and updated timestamps "
                "for all rows already stored in the database before this update."
            ),
        },
    )

    current_time = timezone.now()
    Recipe.objects.filter(author__isnull=True).update(author=profile)
    Recipe.objects.filter(created_on__isnull=True).update(created_on=current_time)
    Recipe.objects.filter(updated_on__isnull=True).update(updated_on=current_time)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('ledger', '0002_recipe_created_on_recipe_updated_on_profile_and_more'),
    ]

    operations = [
        migrations.RunPython(backfill_recipe_profile_fields, noop_reverse),
    ]
