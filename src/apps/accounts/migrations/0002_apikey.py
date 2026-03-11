from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
        ("workspaces", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="APIKey",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(help_text="A descriptive name for this API key", max_length=100)),
                ("prefix", models.CharField(db_index=True, help_text="Visible key prefix", max_length=16)),
                ("hashed_key", models.CharField(help_text="SHA-256 hash of the full key", max_length=128, unique=True)),
                ("is_active", models.BooleanField(default=True)),
                ("last_used_at", models.DateTimeField(blank=True, null=True)),
                ("expires_at", models.DateTimeField(blank=True, null=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="api_keys", to=settings.AUTH_USER_MODEL)),
                ("workspace", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="api_keys", to="workspaces.workspace")),
            ],
            options={
                "verbose_name": "API Key",
                "verbose_name_plural": "API Keys",
                "db_table": "accounts_api_key",
                "ordering": ["-created_at"],
            },
        ),
    ]
