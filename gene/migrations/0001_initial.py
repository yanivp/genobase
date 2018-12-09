# Generated by Django 2.1.2 on 2018-12-09 22:22

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('gene_parser', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Gene',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(db_index=True, max_length=255)),
                ('sequence', models.TextField()),
                ('gene_parser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gene_parsers', to='gene_parser.GeneParser')),
            ],
        ),
        migrations.AlterIndexTogether(
            name='gene',
            index_together={('gene_parser', 'name')},
        ),
    ]