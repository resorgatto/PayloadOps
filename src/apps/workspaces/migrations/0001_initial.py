from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Workspace",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=100)),
                ("slug", models.SlugField(max_length=120, unique=True)),
                ("description", models.TextField(blank=True, default="")),
                ("settings", models.JSONField(blank=True, default=dict, help_text="Workspace-specific settings (JSONB)")),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name": "Workspace",
                "verbose_name_plural": "Workspaces",
                "db_table": "workspaces_workspace",
                "ordering": ["-created_at"],
            },
        ),
    ]
