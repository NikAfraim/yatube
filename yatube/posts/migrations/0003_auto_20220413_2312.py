# Generated by Django 2.2.9 on 2022-04-13 19:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_auto_20220410_1832'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='group',
            options={'verbose_name': 'Сообщество', 'verbose_name_plural': 'Сообщества'},
        ),
        migrations.AlterField(
            model_name='group',
            name='description',
            field=models.TextField(verbose_name='описание'),
        ),
        migrations.AlterField(
            model_name='group',
            name='title',
            field=models.CharField(max_length=200, verbose_name='сообщество'),
        ),
        migrations.AlterField(
            model_name='post',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts', to=settings.AUTH_USER_MODEL, verbose_name='автор'),
        ),
        migrations.AlterField(
            model_name='post',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='posts', to='posts.Group', verbose_name='сообщество'),
        ),
        migrations.AlterField(
            model_name='post',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='дата публикации'),
        ),
        migrations.AlterField(
            model_name='post',
            name='text',
            field=models.TextField(verbose_name='текст'),
        ),
    ]
