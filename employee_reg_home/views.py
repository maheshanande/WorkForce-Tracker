import os
import re
from telnetlib import LOGOUT
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Subquery, OuterRef, Max
import csv
from datetime import date, datetime, timedelta
from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from .emp_model import Employee,EmployeeSalary,UpdateSalary,PaymentDetail, balanceAmount
from .attendance_reg import Attendance
from django.contrib.auth.decorators import login_required
from reportlab.lib.pagesizes import letter,landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, PageBreak, KeepTogether
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus.flowables import KeepTogether
from django.db.models import F



# Create your views here.
@login_required
def Employee_reg_page(request):
    return render(request, 'home.html')

@login_required
def user_logout(request):
    logout(request)
    return render(request,'home')

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
    message = ''
    if request.method == 'POST':
        emp_id = request.POST.get('emp_id')
        name = request.POST.get('name')
        f_name = request.POST.get('father_name')
        m_name = request.POST.get('mother_name')
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
                doj = doj,
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
            message = 'Employee data Sucessully recorded!!!'
        else:
            message = 'Account Number do not match record failed!!!'
    else:
        message = 'Add employee data to register!!!'
    context = {
        'message':message
    }    
        
    return render(request,'employee_reg.html',context)

def Attendance_marker(request):
    message = ''
    if request.method == 'POST':
        emp_id = request.POST.get('emp_id')
        date = request.POST.get('date')
        status = request.POST.get('status')
        ot = request.POST.get('ot')   
        employee_id = Employee.objects.get(emp_id=emp_id)
        # Convert "P" to True (Present) and "NP" to False (Absent)
        if status == "P" or status == "NP" or status:
            attendance = Attendance(employee=employee_id, date=date, present=status, overtime=ot)
            attendance.save()
            message = "Attendance recorded successfully."
        else:
            message = 'Data not Recorded'


    # Render the HTML template with the success message
    return render(request, 'mark_attendence.html', {'message': message})



def add_salary(request):
    message = ''
    employeetype = ''
    gross_salary_ctc = ''
    monthly_salary = ''
    balance_amount = ''
    charge_per_day = ''
    if request.method == 'POST':
        emp_id = request.POST.get('emp_id')
        emtype = request.POST.get('emp_type')
        basic_salary = request.POST.get('bsal')
        annual_salary = request.POST.get('calculated_salary')
        per_day_amount = request.POST.get('per_day')

        # Retrieve the employee
        employee = Employee.objects.get(emp_id=emp_id)
        employee_salaries = EmployeeSalary.objects.filter(employee=employee)
        if employee_salaries.exists():
            employeetype = employee_salaries.first().employee_type
            gross_salary_ctc = employee_salaries.first().gross_salary_ctc
            monthly_salary = employee_salaries.first().monthly_salary
            balance_amount = employee_salaries.first().balance_amount
            charge_per_day = employee_salaries.first().charge_per_day
            message = 'Salary Data fetched successfully'
        else:
            print('No data')
        if emtype is not None and annual_salary is not None and basic_salary is not None and per_day_amount is not None:
            print(employeetype,gross_salary_ctc,monthly_salary,balance_amount,charge_per_day)
            # Create or update the EmployeeSalary record
            salary_detail, created = EmployeeSalary.objects.get_or_create(
                employee=employee,
                employee_type=emtype,
                defaults={
                    'monthly_salary': basic_salary,
                    'gross_salary_ctc': annual_salary,
                    "balance_amount":basic_salary,
                    'charge_per_day':per_day_amount
                }
            )

            if created:
                message = "New salary record created successfully."
                
            else:
                # Update the existing record
                salary_detail.monthly_salary = basic_salary
                salary_detail.gross_salary_ctc = annual_salary
                salary_detail.balance_amount = basic_salary
                salary_detail.charge_per_day = per_day_amount
                salary_detail.save()
                message = "Salary record updated successfully."
    context = {
        'message': message,
        'type': employeetype,
        'Salary_ctc':gross_salary_ctc,
        'm_salary':monthly_salary,
        'b_amount':balance_amount,
        'charge_per_day':charge_per_day

    }

    return render(request, 'salary_details.html', context)


def update_salary_data(request):
    message = ''
    if request.method == 'POST':
        employee_id = request.POST.get('emp_id')
        advance_amount = request.POST.get('adv_amt')
        paid_date = request.POST.get('advDate')


        # Retrieve the employee
        employee = Employee.objects.get(emp_id=employee_id)
        existing_balance_amount = EmployeeSalary.objects.get(employee=employee).balance_amount
        new_balance = existing_balance_amount-int(advance_amount)
        if new_balance == 0:
            # Add the new_balance to the employer's balance amount
            # employer_salary = EmployeeSalary.objects.get(employee=employee)
            # employer_salary.balance_amount += employer_salary.monthly_salary
            # employer_salary.save()
            message = 'New Balance is 0 '
            employer_salary = EmployeeSalary.objects.get(employee=employee)
            employer_salary.balance_amount = new_balance
            employer_salary.save()
                
        else:
            employer_salary = EmployeeSalary.objects.get(employee=employee)
            employer_salary.balance_amount = new_balance
            employer_salary.save()
            message = 'Data recorded successfully!!!'
        # Create a new instance of UpdateSalary for each update
        update_salary = UpdateSalary.objects.create(
            employee=employee,
            advance_amount=advance_amount,
            adv_paid_date=paid_date
            )
        
        # Save the new instance to the database
        update_salary.save()
              
              
        
        

    return render(request,'update_employee.html',{'message': message})
        

def get_employee_data(request):
    # Subquery to find the latest `adv_paid_date` for each employee from UpdateSalary
    # Get the current date
    current_date = datetime.now()

    # Extract the current month and year
    month_selected = current_date.month
    year_selected = current_date.year

    if request.method == 'POST':
        month_selected = request.POST.get('month')
        year_selected = request.POST.get('year')
    if month_selected == '':
        month_selected = current_date.month
    print(month_selected,year_selected)
    employee_data = Employee.objects.prefetch_related('employeesalary').values('emp_id','name','employeesalary__balance_amount')
    # Fetch all data for each employee from the Attendance model
    attendance_data = Employee.objects.prefetch_related('attendance').filter(
    attendance__date__month=month_selected,
    attendance__date__year=year_selected
    ).values('emp_id', 'attendance__date', 'attendance__present', 'attendance__overtime').order_by('attendance__date')


    emp_data_dict = {}
    for data in employee_data:
        emp_id = data['emp_id']
        name = data['name']
        balance = data['employeesalary__balance_amount']
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
    # loop to count present and overtime duty and also calculate amount to be paid
    for emp_id, emp_data in emp_data_dict.items():
        total_present = 0
        total_overtime = 0
        employee = Employee.objects.get(emp_id=emp_id)
        
        # With this block
        employee_salary_queryset = EmployeeSalary.objects.filter(employee=employee)

        if employee_salary_queryset.exists():
            # If there is exactly one matching EmployeeSalary
            empsal = employee_salary_queryset.first()
            # Rest of your code...

        elif employee_salary_queryset.count() > 1:
            # Handle the case where there are multiple matching EmployeeSalary records
            print("Multiple EmployeeSalary records found for the same employee.")
            # You may want to log this information or handle it appropriately.

        else:
            # Handle the case where no matching EmployeeSalary is found
            print("No matching EmployeeSalary found for the employee.")
            # You may want to log this information or handle it appropriately.

        # print('Hii',empsal)
        for date_data in emp_data['attendance_data'].values():
            if date_data['present'] is not None and date_data['overtime'] is not None:
                # Use a regular expression to extract numeric values followed by 'P' or 'p'
                present_values = re.findall(r'(\d+(?:\.\d+)?)P', date_data['present'])
                print(present_values)
                present_counts = [float(value) for value in present_values]
                total_present += sum(present_counts)
                overtime_values = re.findall(r'(\d+(?:\.\d+)?)P', date_data['overtime'])
                overtime_counts = [float(value) for value in overtime_values]
                total_overtime += sum(overtime_counts)
        
        balance_amt = empsal.balance_amount
        charge_per_day = empsal.charge_per_day
        monthly_sal = empsal.monthly_salary

        total_balance = ((total_present*charge_per_day) + (total_overtime*charge_per_day))-(monthly_sal-balance_amt)

        print('total_balance',total_balance)
        emp_data['total_present'] = total_present
        emp_data['total_overtime'] = total_overtime
        emp_data['balance'] = total_balance

    # Initialize an empty set to store all dates
    all_dates = set()

    # Iterate through all employees and update the set with dates
    for emp_data in emp_data_dict.values():
        all_dates.update(emp_data['attendance_data'].keys())

    # Find the employee with the most dates
    employee_with_most_dates = max(emp_data_dict.values(), key=lambda x: len(x['attendance_data']))

    # Set all_dates to the dates of the employee with the most dates
    all_dates = set(employee_with_most_dates['attendance_data'].keys())

    # Fill missing dates for all employees
    for emp_data in emp_data_dict.values():
        for date in all_dates:
            if date not in emp_data['attendance_data']:
                emp_data['attendance_data'][date] = {
                    'present': None,
                    'overtime': None
                }

    # Sort attendance data by date for all employees
    for emp_data in emp_data_dict.values():
        sorted_attendance_data = sorted(emp_data['attendance_data'].items(), key=lambda x: x[0])
        emp_data['attendance_data'] = dict(sorted_attendance_data)
        print(emp_data_dict)

   # Create a CSV file
    desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")

    file_path = os.path.join(desktop_dir, "employee_attendance_report.pdf")

    # Create a PDF document
    doc = SimpleDocTemplate(file_path, pagesize=landscape(letter))

    # Define the data for the PDF
    data = []

    # Create the header row
    header_row = ["ID", "Name"]
    unique_dates = all_dates

    for date in unique_dates:
        day_number = date.split('-')[2]
        header_row.extend([f"{day_number}", ""])

    header_row.extend(["T(P)", "T(OT)", "Balance","Sign"])
    data.append(header_row)
    subheading_row = ["", ""]

    for date in unique_dates:
        subheading_row.extend(["P", "OT"])

    data.insert(1, subheading_row)  # Insert the subheading row at position 1

    # Create data rows
    for emp_id, emp_data in emp_data_dict.items():
        data_row = [emp_id, emp_data['name']]  # ID and Name

        for date in unique_dates:
            att_data = emp_data['attendance_data'][date]
            data_row.extend([att_data['present'] or '', att_data['overtime'] or ''])

        data_row.extend([emp_data['total_present'], emp_data['total_overtime'], emp_data['balance']])
        data.append(data_row)

    table = Table(data)
    # Apply styles to the table
    style = TableStyle([
        ('BACKGROUND', (0, 1), (-1, 1), colors.grey),  # Background color for the subheading row
        ('TEXTCOLOR', (0, 1), (-1, 1), colors.whitesmoke),  # Text color for the subheading row
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),  # Font for the subheading row
        ('BOTTOMPADDING', (0, 1), (-1, 1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Add a grid to the entire table
        ('LINEABOVE', (0, 0), (-1, 1), 1, colors.black),  # Add line above the header
    ])
    table.setStyle(style)
    KeepTogether(table)  # Ensure the table stays together when breaking across pages
    # Build the PDF document and save it
    doc.build([Paragraph("Employee Attendance Report", getSampleStyleSheet()['Title']), table])

    print(f"PDF file '{file_path}' has been created.")
    context = {
        'emp_data_dict': emp_data_dict,
    }
    return render(request, 'show_employee_data.html',context)

def advance_payment_data(request):
    Adv_data_dict = {}
    if request.method == 'POST':
        emp_id = request.POST.get('emp_id')
        employee = Employee.objects.get(emp_id=emp_id)
        name = employee.name
        id = employee.emp_id
        get_details = UpdateSalary.objects.filter(employee=employee).values('advance_amount','adv_paid_date')
        print(get_details)
        for data in get_details:
            adv_amt = data['advance_amount']
            date = f"{data['adv_paid_date']}"
            if date not in Adv_data_dict:
                # If the 'id' is already in the dictionary, append the data to the list
                Adv_data_dict[date] = {
                'ID':id,
                'Name':name,
                'Advance_amount': adv_amt            
                }
        print(Adv_data_dict)
    context = {
        'Adv_data_dict': Adv_data_dict,
    }
        
    return render(request,'advance_payment_data.html',context)

def payment_data(request):
    balance_amount = None  # Initialize balance_amount
    message = ''
    if request.method == 'POST':
        emp_id = request.POST.get('emp_id')
        paid_date = request.POST.get('pay_date')
        if paid_date:
            date_object = datetime.strptime(paid_date, "%Y-%m-%d")
            # Extract month and year
            month = date_object.month
            year = date_object.year
        amount_paid = request.POST.get('sal_amount')
        month_selected = request.POST.get('month')
        year_selected = request.POST.get('year')

        employee = Employee.objects.get(emp_id=emp_id)
        # Filter balanceAmount objects for the given employee and month
        
        if amount_paid is None:
            balance_records = balanceAmount.objects.filter(
            employee=employee,
            balance_reg_date__month=month_selected,
            balance_reg_date__year=year_selected,
            ).order_by('-balance_reg_date')  # Order by balance_reg_date in descending order

            # Get the latest balance_to_pay amount if any records exist
            latest_balance_record = balance_records.first()
            if latest_balance_record:
                latest_balance_to_pay = latest_balance_record.balance_to_pay
                balance_amount = latest_balance_to_pay
                latest_balance_reg_date = latest_balance_record.balance_reg_date
                print(f"Latest Balance to Pay: {latest_balance_to_pay} on {latest_balance_reg_date}")
            else:
                print("No balance records found for the specified employee and month.")
        else:
            if paid_date is not None :
                balance_records = balanceAmount.objects.filter(
                employee=employee,
                balance_reg_date__month=month,
                balance_reg_date__year=year,
                ).order_by('-balance_reg_date')  # Order by balance_reg_date in descending order

                # Get the latest balance_to_pay amount if any records exist
                latest_balance_record = balance_records.first()
                if latest_balance_record:
                    latest_balance_to_pay = latest_balance_record.balance_to_pay
                    balance_amount = latest_balance_to_pay
                    latest_balance_reg_date = latest_balance_record.balance_reg_date
                    print(f"Latest Balance to Pay: {latest_balance_to_pay} on {latest_balance_reg_date}")
                else:
                    print("No balance records found for the specified employee and month.")
                balance_amount = balance_amount-int(amount_paid)
                if balance_amount == 0 and paid_date is not None:
                    set_balance_amount = EmployeeSalary.objects.get(employee=employee)
                    set_balance_amount.balance_amount = set_balance_amount.monthly_salary
                    set_balance_amount.save()
                    balance_topay = balanceAmount.objects.create(employee=employee,balance_to_pay=balance_amount,balance_reg_date=paid_date)
                    balance_topay.save()
                    message = 'Payment Succesfully Added!!'
                    pay_details = PaymentDetail.objects.create(employee=employee, paid_amount=amount_paid, paid_date=paid_date)
                    pay_details.save()
                else:
                    balance_topay = balanceAmount.objects.create(employee=employee,balance_to_pay=balance_amount,balance_reg_date=paid_date)
                    balance_topay.save()
                    pay_details = PaymentDetail.objects.create(employee=employee, paid_amount=amount_paid, paid_date=paid_date)
                    pay_details.save()
                    message = 'Payment Succesfully Added!!'

                
            

    context = {
        'balance_amount': balance_amount,
        'message':message
    }
    return render(request, 'payment_details.html', context)


def delete_emp(request):
    message = ''
    if request.method == 'POST':
        emp_id = request.POST.get('emp_id')
        Employee.objects.filter(emp_id=emp_id).delete()
        message = 'Employee Data Successfully deleted!!!'

    context = {
        'message':message,
    }
    return render(request,'delete_employee_data.html',context)


def payment_data_view(request):
    data_dict = {}
    if request.method == 'POST':
        emp_id = request.POST.get('emp_id')
        employee = Employee.objects.get(emp_id=emp_id)
        name = employee.name
        id = employee.emp_id
        get_details = PaymentDetail.objects.filter(employee=employee).values('paid_amount','paid_date')
        print(get_details)
        for data in get_details:
            paid_amt = data['paid_amount']
            date = f"{data['paid_date']}"
            if date not in data_dict:
                # If the 'id' is already in the dictionary, append the data to the list
                data_dict[date] = {
                'ID':id,
                'Name':name,
                'Paid_amount': paid_amt            
                }
        print(data_dict)
    context = {
        'data_dict': data_dict,
    }
        
    return render(request,'view_payment_data.html',context)

def calculate_balance_amount(request):
    # Subquery to find the latest `adv_paid_date` for each employee from UpdateSalary
    # Get the current date
    amt_data_dict = {}
    current_date = datetime.now()

    # Extract the current month and year
    month_selected = current_date.month
    year_selected = current_date.year

    if request.method == 'POST':
        month_selected = request.POST.get('month')
        year_selected = request.POST.get('year')
    if month_selected == '':
        month_selected = current_date.month
    print(month_selected,year_selected)
    employee_data = Employee.objects.prefetch_related('employeesalary').values('emp_id','name','employeesalary__balance_amount')
    # Fetch all data for each employee from the Attendance model
    attendance_data = Employee.objects.prefetch_related('attendance').filter(
    attendance__date__month=month_selected,
    attendance__date__year=year_selected
    ).values('emp_id', 'attendance__date', 'attendance__present', 'attendance__overtime').order_by('attendance__date')


    emp_data_dict = {}
    for data in employee_data:
        emp_id = data['emp_id']
        name = data['name']
        balance = data['employeesalary__balance_amount']
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
    # loop to count present and overtime duty and also calculate amount to be paid
    for emp_id, emp_data in emp_data_dict.items():
        total_present = 0
        total_overtime = 0
        employee = Employee.objects.get(emp_id=emp_id)
        
        # With this block
        employee_salary_queryset = EmployeeSalary.objects.filter(employee=employee)

        if employee_salary_queryset.exists():
            # If there is exactly one matching EmployeeSalary
            empsal = employee_salary_queryset.first()
            # Rest of your code...

        elif employee_salary_queryset.count() > 1:
            # Handle the case where there are multiple matching EmployeeSalary records
            print("Multiple EmployeeSalary records found for the same employee.")
            # You may want to log this information or handle it appropriately.

        else:
            # Handle the case where no matching EmployeeSalary is found
            print("No matching EmployeeSalary found for the employee.")

        for date_data in emp_data['attendance_data'].values():
            if date_data['present'] is not None and date_data['overtime'] is not None:
                # Use a regular expression to extract numeric values followed by 'P' or 'p'
                present_values = re.findall(r'(\d+(?:\.\d+)?)P', date_data['present'])
                print(present_values)
                present_counts = [float(value) for value in present_values]
                total_present += sum(present_counts)
                overtime_values = re.findall(r'(\d+(?:\.\d+)?)P', date_data['overtime'])
                overtime_counts = [float(value) for value in overtime_values]
                total_overtime += sum(overtime_counts)

        # Continue with the rest of your code
        balance_amt = empsal.balance_amount
        charge_per_day = empsal.charge_per_day
        monthly_sal = empsal.monthly_salary

        total_balance = ((total_present*charge_per_day) + (total_overtime*charge_per_day))-(monthly_sal-balance_amt)

        # Check if a record for the same employee and date already exists
        existing_record = balanceAmount.objects.filter(
            employee=employee,
            balance_reg_date=timezone.localdate()  # Use the current date and time
        ).first()

        if existing_record:
            # Update the existing record if it already exists
            existing_record.balance_to_pay = total_balance
            existing_record.save()
        else:
            # Create a new record if it doesn't exist
            new_update_salary_record = balanceAmount.objects.create(
                employee=employee,
                balance_to_pay=total_balance,
                balance_reg_date=timezone.localdate()  # Use the current date and time
            )
            new_update_salary_record.save()

            if new_update_salary_record or existing_record:
                print('total_balance', total_balance)
            else:
                print('Record not created')
    
    # Assuming emp_id is a specific employee's ID
    balance_data = Employee.objects.prefetch_related('balanceamount').filter(
        balanceamount__balance_reg_date__month=month_selected,
        balanceamount__balance_reg_date__year=year_selected
    ).values('emp_id','name','balanceamount__balance_reg_date','balanceamount__balance_to_pay').order_by('-balanceamount__balance_reg_date')
    print(balance_data)
    for data in balance_data:
        emp_id = data['emp_id']
        name = data['name']
        date = f"{data['balanceamount__balance_reg_date']}"
        amount = data['balanceamount__balance_to_pay']
        print(emp_id,name,amount)
        if emp_id not in amt_data_dict:
            amt_data_dict[emp_id]={
                    'Name':name,
                    'Net_Balance_Amount': amount
                }
        print(amt_data_dict)
    context = {
        'data_dict': amt_data_dict,
    }  
    return render(request,"calc_balance.html",context)
        


# -------------------------------------------------------------------------------------------------------------------#
# # logic to fetch balance amount to be paid from latest data update
        # latest_balance_value = 0
        # latest_balance_record = balanceAmount.objects.filter(
        # employee=employee,
        # balance_to_pay__isnull=False  # Exclude records with null balance_to_pay
        # ).annotate(
        #     latest_balance_date=Max('balance_reg_date'),
        #     latest_balance=F('balance_to_pay')
        # )

        # if latest_balance_record.exists():
        #     latest_balance_value = latest_balance_record.first().latest_balance
        #     print("Latest Balance to Pay:", latest_balance_value,timezone.now())
        # else:
        #     print("No balance record found for the specified employee.")
        #     latest_balance_value = empsal.monthly_salary