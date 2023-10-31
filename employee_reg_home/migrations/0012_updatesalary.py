# Generated by Django 4.2.6 on 2023-10-25 09:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('employee_reg_home', '0011_remove_employeesalary_adv_paid_date_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='UpdateSalary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('advance_amount', models.IntegerField(blank=True, null=True)),
                ('balance_amount', models.IntegerField(blank=True, null=True)),
                ('adv_paid_date', models.DateField(null=True, unique=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employee_reg_home.employee')),
            ],
        ),
    ]