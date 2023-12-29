from django.contrib import admin
from .emp_model import Employee,EmployeeSalary,UpdateSalary,PaymentDetail,balanceAmount
from .attendance_reg import Attendance
# Register your models here.
admin.site.register(Employee)
admin.site.register(Attendance)
admin.site.register(EmployeeSalary)
admin.site.register(UpdateSalary)
admin.site.register(PaymentDetail)
admin.site.register(balanceAmount)