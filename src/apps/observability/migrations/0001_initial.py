from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("workspaces", "0001_initial"),
        ("workflows", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ExecutionLog",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("status", models.CharField(choices=[("pending", "Pending"), ("processing", "Processing"), ("success", "Success"), ("failed", "Failed"), ("retrying", "Retrying"), ("dead_letter", "Dead Letter")], db_index=True, default="pending", max_length=20)),
                ("payload_received", models.JSONField(default=dict)),
                ("response_body", models.JSONField(blank=True, default=None, null=True)),
                ("response_status_code", models.IntegerField(blank=True, null=True)),
                ("attempt_number", models.PositiveIntegerField(default=1)),
                ("max_attempts", models.PositiveIntegerField(default=3)),
                ("duration_ms", models.PositiveIntegerField(blank=True, null=True)),
                ("error_message", models.TextField(blank=True, default="")),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("workspace", models.ForeignKey(db_index=True, on_delete=django.db.models.deletion.CASCADE, related_name="executionlogs", to="workspaces.workspace")),
                ("workflow", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="execution_logs", to="workflows.workflow")),
                ("trigger", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="execution_logs", to="workflows.trigger")),
                ("action", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="execution_logs", to="workflows.action")),
            ],
            options={
                "verbose_name": "Execution Log",
                "verbose_name_plural": "Execution Logs",
                "db_table": "observability_execution_log",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="executionlog",
            index=models.Index(fields=["workflow", "status"], name="observabili_workflo_idx"),
        ),
        migrations.AddIndex(
            model_name="executionlog",
            index=models.Index(fields=["created_at"], name="observabili_created_idx"),
        ),
        migrations.AddIndex(
            model_name="executionlog",
            index=models.Index(fields=["status", "created_at"], name="observabili_status__idx"),
        ),
    ]
