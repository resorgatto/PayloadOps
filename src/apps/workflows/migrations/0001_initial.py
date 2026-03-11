from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("workspaces", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Workflow",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True, default="")),
                ("status", models.CharField(choices=[("draft", "Draft"), ("active", "Active"), ("paused", "Paused")], db_index=True, default="draft", max_length=20)),
                ("workspace", models.ForeignKey(db_index=True, on_delete=django.db.models.deletion.CASCADE, related_name="workflows", to="workspaces.workspace")),
            ],
            options={
                "verbose_name": "Workflow",
                "verbose_name_plural": "Workflows",
                "db_table": "workflows_workflow",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Trigger",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("trigger_type", models.CharField(choices=[("webhook", "Webhook")], default="webhook", max_length=20)),
                ("webhook_path", models.UUIDField(db_index=True, default=uuid.uuid4, unique=True)),
                ("is_active", models.BooleanField(default=True)),
                ("workspace", models.ForeignKey(db_index=True, on_delete=django.db.models.deletion.CASCADE, related_name="triggers", to="workspaces.workspace")),
                ("workflow", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="trigger", to="workflows.workflow")),
            ],
            options={
                "verbose_name": "Trigger",
                "verbose_name_plural": "Triggers",
                "db_table": "workflows_trigger",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Action",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=200)),
                ("order", models.PositiveIntegerField(default=0)),
                ("http_method", models.CharField(choices=[("GET", "GET"), ("POST", "POST"), ("PUT", "PUT"), ("PATCH", "PATCH"), ("DELETE", "DELETE")], default="POST", max_length=10)),
                ("url", models.URLField(max_length=2000)),
                ("headers", models.JSONField(blank=True, default=dict)),
                ("body_template", models.JSONField(blank=True, default=dict)),
                ("is_active", models.BooleanField(default=True)),
                ("workspace", models.ForeignKey(db_index=True, on_delete=django.db.models.deletion.CASCADE, related_name="actions", to="workspaces.workspace")),
                ("workflow", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="actions", to="workflows.workflow")),
            ],
            options={
                "verbose_name": "Action",
                "verbose_name_plural": "Actions",
                "db_table": "workflows_action",
                "ordering": ["order", "created_at"],
            },
        ),
        migrations.CreateModel(
            name="Credential",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True, default="")),
                ("encrypted_value", models.TextField()),
                ("workspace", models.ForeignKey(db_index=True, on_delete=django.db.models.deletion.CASCADE, related_name="credentials", to="workspaces.workspace")),
            ],
            options={
                "verbose_name": "Credential",
                "verbose_name_plural": "Credentials",
                "db_table": "workflows_credential",
                "ordering": ["-created_at"],
            },
        ),
    ]
