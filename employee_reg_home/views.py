import os
import re
from django.db.models import Subquery, OuterRef, Max
import csv
from datetime import datetime, timedelta
from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login
from .emp_model import Employee,EmployeeSalary,UpdateSalary
from .attendance_reg import Attendance
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def Employee_reg_page(request):
    return render(request, 'home.html')

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('pass')
        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password incorrect!!!')
    return render(request,'login.html')
def admin_register(request):
    if request.method == "POST":
        user_name = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_pass = request.POST.get('confirm_password')
        if password == confirm_pass:

            user_data = User.objects.create_user(user_name,email,password)
            user_data.save()
            # print(user_name,email,password,confirm_pass)
            messages.success(request,'User successfully created!!!')
            return redirect('login')
        else:
            return messages.error(request,"Password doesn't match")
    return render(request,'signup.html')
def employee_reg(request):
    if request.method == 'POST':
        emp_id = request.POST.get('emp_id')
        name = request.POST.get('name')
        f_name = request.POST.get('father_name')
        m_name = request.POST.get('mother_name')
        emp_name = request.POST.get('username')
        dob = request.POST.get('dob')
        doj = request.POST.get('doj')
        present_address = request.POST.get('present_address')
        permanent_address = request.POST.get('permanent_address')
        email = request.POST.get('email')
        contact_no = request.POST.get('contact_number')
        adhar_no = request.POST.get('adhar_no')
        epf_no = request.POST.get('epf_no')
        esi_no = request.POST.get('esi_no')
        pan_no = request.POST.get('pan_no')
        bank_name = request.POST.get('bank_name')
        acc_no = request.POST.get('acc_no')
        conf_acc_no = request.POST.get('confirm_acc_no')
        ifse = request.POST.get('ifse_code')
        branch = request.POST.get('branch')
        bg = request.POST.get('bg')
        weight = request.POST.get('weight')
        height = request.POST.get('height')
        nationality = request.POST.get('nationality')
        religion = request.POST.get('religion')
        category = request.POST.get('category')
        edu = request.POST.get('education')
        last_pay = request.POST.get('lastPay')
        experience = request.POST.get('exp')
        if acc_no == conf_acc_no:
            employee = Employee(
                emp_id=emp_id,
                name=name,
                father_name=f_name,
                mother_name=m_name,
                dob=dob,
                present_address=present_address,
                permanent_address=permanent_address,
                email=email,
                contact_no=contact_no,
                adhar_no=adhar_no,
                epf_no=epf_no,
                esi_no=esi_no,
                pan_no=pan_no,
                bank_name=bank_name,
                acc_no=acc_no,
                ifse=ifse,
                branch=branch,
                bg=bg,
                weight=weight,
                height=height,
                nationality=nationality,
                religion=religion,
                category=category,
                education=edu,
                last_pay=last_pay,
                experience=experience
            )
            employee.save()
            messages.success(request,'Employee data Sucessully recorded!!!')
        else:
            messages.error(request,'No Match Data record failed!!!')
        
    return render(request,'employee_reg.html')

def Attendance_marker(request):
    if request.method == 'POST':
        emp_id = request.POST.get('emp_id')
        date = request.POST.get('date')
        status = request.POST.get('status')
        ot = request.POST.get('ot')   
        employee_id = Employee.objects.get(emp_id=emp_id)
        # Convert "P" to True (Present) and "NP" to False (Absent)
        if status == "P" or status == "NP":
            attendance = Attendance(employee=employee_id, date=date, present=status, overtime=ot)
            attendance.save()
               
                
    return render(request, 'mark_attendence.html')

def submit_salary(request):
    if request.method == 'POST':
        emp_id = request.POST.get('emp_id')
        employee_type = request.POST.get('emp_type')
        basic_salary = request.POST.get('bsal')
        annual_salary = request.POST.get('calculated_salary')

        # Retrieve other form fields
        print(emp_id,basic_salary,annual_salary,employee_type)
        # Create a new record in Employeesalary with the foreign key reference to Employee
        employee = Employee.objects.get(id=emp_id)
        salary_detail = EmployeeSalary.objects.create(employee=employee, monthly_salary=basic_salary, gross_salary_ctc=annual_salary, employee_type=employee_type)
        salary_detail.save()

        # Redirect or return a response as needed

    return render(request,'salary_details.html')  # Redirect to a success page


def update_employee_details(request):
    if request.method == 'POST':
        employee_id = request.POST.get('emp_id')
        advance_amount = request.POST.get('adv_amt')
        paid_date = request.POST.get('advDate')
        
        # Retrieve the existing balance amount for the employee
        existing_balance_amount = UpdateSalary.objects.filter(employee=employee_id).order_by('-adv_paid_date').first()
        
        # Check if this is the first update and the balance is 0
        if not existing_balance_amount or existing_balance_amount.balance_amount == 0:
            # Fetch the employee's monthly salary from Employeesalary model
            monthly_sal = EmployeeSalary.objects.filter(employee=employee_id).order_by('monthly_salary').first()
            balance_amount = monthly_sal.monthly_salary - int(advance_amount)
        else:
            balance_amount = existing_balance_amount.balance_amount - int(advance_amount)
        
        # Create a new instance of UpdateSalary for each update
        update_salary = UpdateSalary(
            employee_id=employee_id,
            advance_amount=advance_amount,
            balance_amount=balance_amount,
            adv_paid_date=paid_date
        )
        
        # Save the new instance to the database
        update_salary.save()

    return render(request,'update_employee.html')
        

def get_employee_data(request):
    # Subquery to find the latest `adv_paid_date` for each employee from UpdateSalary
    latest_dates_salary = UpdateSalary.objects.filter(
        employee=OuterRef('pk')
    ).values('employee').annotate(
        latest_date_salary=Max('adv_paid_date')
    ).values('latest_date_salary')

    # Fetch the data for emp_id, name, and balance based on the latest `adv_paid_date`
    latest_balance_data = Employee.objects.annotate(
        latest_date_salary=Subquery(latest_dates_salary)
    ).filter(
        updatesalary__adv_paid_date=Subquery(latest_dates_salary)
    ).values('emp_id', 'name', 'updatesalary__balance_amount')

    # Fetch all data for each employee from the Attendance model
    attendance_data = Employee.objects.prefetch_related('Attendance').values('emp_id', 'name', 'attendance__date', 'attendance__present', 'attendance__overtime')

    emp_data_dict = {}
    for data in latest_balance_data:
        emp_id = data['emp_id']
        name = data['name']
        balance = data['updatesalary__balance_amount']

        if emp_id not in emp_data_dict:
            emp_data_dict[emp_id] = {
                'name': name,
                'balance': balance,
                'attendance_data': {}
            }

    for data in attendance_data:
        emp_id = data['emp_id']
        date = f"{data['attendance__date']}"
        present = data['attendance__present']
        overtime = data['attendance__overtime']

        if emp_id in emp_data_dict:
            emp_data_dict[emp_id]['attendance_data'][date] = {
                'present': present,
                'overtime': overtime
            }

    for emp_id, emp_data in emp_data_dict.items():
        total_present = 0
        total_overtime = 0

        for date_data in emp_data['attendance_data'].values():
            if date_data['present'] is not None and date_data['overtime'] is not None:
                # Use a regular expression to extract numeric values followed by 'P' or 'p'
                total_present += date_data['present'].count('P')
                overtime_values = re.findall(r'(\d+)[Pp]', date_data['overtime'])
                overtime_counts = [int(value) for value in overtime_values]
                total_overtime += sum(overtime_counts)

        emp_data['total_present'] = total_present
        emp_data['total_overtime'] = total_overtime

    all_dates = set()
    for emp_data in emp_data_dict.values():
        all_dates.update(emp_data['attendance_data'].keys())

    for emp_id, emp_data in emp_data_dict.items():
        for date in all_dates:
            if date not in emp_data['attendance_data']:
                emp_data['attendance_data'][date] = {
                    'present': None,
                    'overtime': None
                }

   # Create a CSV file
    desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")

    # Full file path including the desktop directory
    file_path = os.path.join(desktop_dir, "employee_attendance_report.csv")
    with open(file_path, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)

        # Create the header row
        header_row = ["ID", "Name"]
        unique_dates = emp_data_dict['1']['attendance_data'].keys()

        for date in unique_dates:
            header_row.extend([f"{date}",""])

        header_row.extend(["Total Present", "Total Overtime", "Balance", "Signature"])
        csvwriter.writerow(header_row)

        # Create subheading row
        subheading_row = ["", ""]

        for date in unique_dates:
            subheading_row.extend(["Present", "Overtime"])

        # subheading_row.extend(["", "", "", ""])
        csvwriter.writerow(subheading_row)

        # Create data rows
        for emp_id, emp_data in emp_data_dict.items():
            data_row = [emp_id, emp_data['name']]  # ID and Name

            for date in unique_dates:
                att_data = emp_data['attendance_data'][date]
                data_row.extend([att_data['present'] or '', att_data['overtime'] or ''])

            data_row.extend([emp_data['total_present'], emp_data['total_overtime'], emp_data['balance'], ''])
            csvwriter.writerow(data_row)

    print("CSV file 'employee_attendance_report.csv' has been created.")
    return render(request, 'show_employee_data.html', {'emp_data_dict': emp_data_dict})

# Include necessary imports for UpdateSalary, Employee, and any other required modules

