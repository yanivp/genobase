# Generated by Django 2.1.2 on 2018-12-09 18:56

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('async_job', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeneParser',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('source_put_url', models.CharField(blank=True, default=None, max_length=500, null=True)),
                ('is_file_uploaded', models.BooleanField(default=False)),
                ('is_file_processed', models.BooleanField(default=False)),
                ('file_name', models.CharField(max_length=50)),
                ('async_job', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='gene_parsers', to='async_job.AsyncJob')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
