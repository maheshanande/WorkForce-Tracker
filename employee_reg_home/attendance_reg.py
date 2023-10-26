from .emp_model import Employee
from django.db import models


class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    present = models.CharField(max_length=3)  
    overtime = models.CharField(max_length=5,blank=True,null=True) 
