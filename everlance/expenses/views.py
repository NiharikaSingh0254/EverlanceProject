from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Category, Expense
# Create your views here.
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
import json
from django.http import JsonResponse,HttpResponse
from userpreferences.models import UserPreference
import datetime
from collections import defaultdict
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar
import csv
import xlwt
from django.template.loader import render_to_string
import pdfkit
from django.db.models import Sum


def search_expenses(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        expenses = Expense.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            date__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            description__icontains=search_str, owner=request.user) | Expense.objects.filter(
            category__icontains=search_str, owner=request.user)
        data = expenses.values()
        return JsonResponse(list(data), safe=False)


@login_required(login_url='/authentication/login')
def index(request):
    categories = Category.objects.all()
    expenses = Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 5)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    # currency = UserPreference.objects.get(user=request.user).currency
    try:
        user_preference = UserPreference.objects.get(user=request.user)
        currency = user_preference.currency
    except UserPreference.DoesNotExist:
        currency = None
    
    context = {
        'expenses': expenses,
        'page_obj': page_obj,
        'currency': currency,
        'categories':categories
    }
    return render(request, 'expenses/index.html', context)
# @login_required(login_url='/authentication/login')
# def index(request):
#     categories = Category.objects.all()
#     expenses = Expense.objects.filter(owner=request.user)
#     paginator = Paginator(expenses, 5)
#     page_number = request.GET.get('page')
#     page_obj = Paginator.get_page(paginator, page_number)
    
#     try:
#         user_preference = UserPreference.objects.get(user=request.user)
#         currency = user_preference.currency
#     except UserPreference.DoesNotExist:
#         currency = None
    
#     context = {
#         'expenses': expenses,
#         'page_obj': page_obj,
#         'currency': currency
#     }
#     return render(request, 'expenses/index.html', context)


@login_required(login_url='/authentication/login')
def add_expense(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'expenses/add_expense.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/add_expense.html', context)
        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'expenses/add_expense.html', context)
        
        if not date:
            messages.error(request, 'date is required')
            return render(request, 'expenses/add_expense.html', context)

        Expense.objects.create(owner=request.user, amount=amount, date=date,
                               category=category, description=description)
        messages.success(request, 'Expense saved successfully')

        return redirect('expenses')


@login_required(login_url='/authentication/login')
def expense_edit(request, id):
    expense = Expense.objects.get(pk=id)
    categories = Category.objects.all()
    context = {
        'expense': expense,
        'values': expense,
        'categories': categories
    }
    if request.method == 'GET':
        return render(request, 'expenses/edit-expense.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/edit-expense.html', context)
        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'expenses/edit-expense.html', context)

        expense.owner = request.user
        expense.amount = amount
        expense. date = date
        expense.category = category
        expense.description = description

        expense.save()
        messages.success(request, 'Expense updated  successfully')

        return redirect('expenses')


def delete_expense(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, 'Expense removed')
    return redirect('expenses')

@login_required(login_url='/authentication/login')
def expense_category_summary(request):
    # todays_date = datetime.date.today()
    # six_months_ago = todays_date - datetime.timedelta(days=30 * 6)
    # expenses = Expense.objects.filter(owner=request.user,
    #                                   date__gte=six_months_ago, date__lte=todays_date)
    expenses = Expense.objects.filter(owner=request.user)
    finalrep = {}

    def get_category(expense):
        return expense.category  # Assuming expense has a category field

    # Ensure unique categories (optional)
    category_list = list(set(map(get_category, expenses)))

    def get_expense_category_amount(category):
        amount = 0
        filtered_by_category = expenses.filter(category=category)
        for item in filtered_by_category:
            amount += item.amount
        return amount

    for category in category_list:
        # Update finalrep with 0 if category is empty
        finalrep.setdefault(category, 0)  # defaultdict-like behavior
        finalrep[category] = get_expense_category_amount(category)

    return JsonResponse({'expense_category_data': finalrep}, safe=False)

def expensestats_view(request):
    return render(request, 'expenses/expensestats.html')

def expense_summary_rest(request):
    try:
        expenses = Expense.objects.filter(owner=request.user)

        print("Number of expenses:", len(expenses))  # Debug statement

        summary = defaultdict(lambda: {'total_amount': 0, 'details': []})
        monthwise_summary = defaultdict(list)

        for expense in expenses:
            month_year = expense.date.strftime('%Y-%m')
            monthwise_summary[month_year].append({
                'id': expense.id,
                'amount': expense.amount,
                'description': expense.description,
                'date': expense.date.strftime('%Y-%m-%d')
            })

            summary[expense.category]['total_amount'] += expense.amount
            summary[expense.category]['details'].append({
                'id': expense.id,
                'amount': expense.amount,
                'description': expense.description,
                'date': expense.date.strftime('%Y-%m-%d')
            })

        # Extract unique months from expenses
        months = sorted(set([expense.date.strftime('%Y-%m') for expense in expenses]))
        print("Unique months:", months)  # Debug statement

        summary_data = {
            'months': months,
            'monthwise_expense_data': dict(monthwise_summary),  # Include the month-wise summary data
            'expense_category_data': dict(summary),  # Include the category-wise summary data
        }

        return JsonResponse(summary_data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
def expense_yearwise_summary(request):
    try:
        today = datetime.today().date()
        start_of_year = datetime(today.year, 1, 1).date()

        # Filter expenses for the current year
        expenses = Expense.objects.filter(owner=request.user, date__gte=start_of_year, date__lte=today)

        # Dictionary to store monthly totals
        monthly_totals = {}

        # Loop through each month of the current year
        for month in range(1, 13):
            start_of_month = datetime(today.year, month, 1).date()
            end_of_month = start_of_month + relativedelta(months=1) - timedelta(days=1)

            # Filter expenses for the current month
            monthly_expenses = expenses.filter(date__gte=start_of_month, date__lte=end_of_month)

            # Calculate total expenses for the month
            total_monthly_expenses = sum(expense.amount for expense in monthly_expenses)

            # Get month name
            month_name = start_of_month.strftime('%B')

            # Store the total expenses in the dictionary
            monthly_totals[month_name] = total_monthly_expenses

        return JsonResponse(monthly_totals, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
def expense_weekwise_summary(request):
    try:
        today = datetime.today().date()
        start_of_week = today - timedelta(days=today.weekday())  # Start of the week (Monday)
        end_of_week = start_of_week + timedelta(days=6)  # End of the week (Sunday)

        # Filter expenses by date for the current week
        expenses = Expense.objects.filter(owner=request.user, date__gte=start_of_week, date__lte=end_of_week)

        week_expenses = {day: 0 for day in calendar.day_name}  # Initialize dictionary with days of the week

        for expense in expenses:
            day_name = calendar.day_name[expense.date.weekday()]
            week_expenses[day_name] += expense.amount

        return JsonResponse(week_expenses, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
def get_monday_of_current_week(date):
    # Find the Monday of the current week
    monday = date - timedelta(days=date.weekday())
    return monday

def get_sunday_of_current_week(date):
    # Find the Sunday of the current week
    sunday = date + timedelta(days=(6 - date.weekday()))
    return sunday

def metric_card_view1(request):
    try:
        today = datetime.today().date()
        start_of_year = datetime(today.year, 1, 1).date()

        monday_of_current_week = get_monday_of_current_week(today)
        sunday_of_current_week = get_sunday_of_current_week(today)


        # Filter expenses by date
        expenses = Expense.objects.filter(owner=request.user)

        daily_expenses = expenses.filter(date=today).count()
        weekly_expenses = expenses.filter(date__gte=monday_of_current_week, date__lte=sunday_of_current_week).count()
        yearly_expenses = expenses.filter(date__gte=start_of_year, date__lte=today).count()

        monthly_expenses = {}
        current_month = today.month
        current_year = today.year
        while current_year > start_of_year.year or (current_year == start_of_year.year and current_month >= start_of_year.month):
            start_of_month = datetime(current_year, current_month, 1).date()
            end_of_month = start_of_month + relativedelta(months=1) - timedelta(days=1)
            monthly_expenses_count = expenses.filter(date__gte=start_of_month, date__lte=end_of_month).count()
            monthly_expenses[start_of_month.strftime('%Y-%m')] = monthly_expenses_count
            current_month -= 1
            if current_month == 0:
                current_month = 12
                current_year -= 1

        # Get the total expenses for the current month
        current_month_key = datetime(today.year, today.month, 1).strftime('%Y-%m')
        monthly_expenses = monthly_expenses.get(current_month_key, 0)

        data = {
            'daily_expenses': daily_expenses,
            'weekly_expenses': weekly_expenses,
            'monthly_expenses': monthly_expenses,
            'yearly_expenses': yearly_expenses
        }

        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def metric_card_view2(request):
    try:
        today = datetime.today().date()
        start_of_year = datetime(today.year, 1, 1).date()

        monday_of_current_week = get_monday_of_current_week(today)
        sunday_of_current_week = get_sunday_of_current_week(today)


        # Filter expenses by date
        expenses = Expense.objects.filter(owner=request.user)

        daily_expenses = expenses.filter(date=today)
        weekly_expenses = expenses.filter(date__gte=monday_of_current_week, date__lte=sunday_of_current_week)
        yearly_expenses = expenses.filter(date__gte=start_of_year, date__lte=today)

        total_daily_expenses = sum(expense.amount for expense in daily_expenses)
        total_weekly_expenses = sum(expense.amount for expense in weekly_expenses)
        total_yearly_expenses = sum(expense.amount for expense in yearly_expenses)

        monthly_totals = {}
        current_month = today.month
        current_year = today.year

        while current_year > start_of_year.year or (current_year == start_of_year.year and current_month >= start_of_year.month):
            start_of_month = datetime(current_year, current_month, 1).date()
            end_of_month = start_of_month + relativedelta(months=1) - timedelta(days=1)
            monthly_expenses = expenses.filter(date__gte=start_of_month, date__lte=end_of_month)
            total_monthly_expenses = sum(expense.amount for expense in monthly_expenses)
            monthly_totals[start_of_month.strftime('%Y-%m')] = total_monthly_expenses

            current_month -= 1
            if current_month == 0:
                current_month = 12
                current_year -= 1

        current_month_key = datetime(today.year, today.month, 1).strftime('%Y-%m')
        total_monthly_expenses = monthly_totals.get(current_month_key, 0)

        data = {
            'total_daily_expenses': total_daily_expenses,
            'total_weekly_expenses': total_weekly_expenses,
            'monthly_totals': total_monthly_expenses,
            'total_yearly_expenses': total_yearly_expenses
        }

        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

def get_filtered_expenses(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    category = request.GET.get('category')

    expenses = Expense.objects.filter(owner=request.user)
    
    if start_date:
        expenses =expenses.filter(date__gte=start_date)
    if end_date:
        expenses =expenses.filter(date__lte=end_date)
    if category:
        expenses =expenses.filter(category=category)

    total = expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    context = {
        'expenses': expenses,
        'start_date': start_date,
        'end_date': end_date,
        'category':category,
        'total':total
    }
    

    return context

def export_csv(request):
    expenses = get_filtered_expenses(request)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Expenses' + \
        str(datetime.now()) + '.csv'

    writer = csv.writer(response)
    writer.writerow(['Amount', 'Description', 'Category', 'Date'])

    for expense in expenses:
        writer.writerow([expense.amount, expense.description, expense.category, expense.date])

    return response

def export_excel(request):
    expenses = get_filtered_expenses(request)

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Expenses' + \
        str(datetime.now()) + '.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Expenses')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Amount', 'Description', 'Category', 'Date']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()

    for expense in expenses:
        row_num += 1
        ws.write(row_num, 0, str(expense.amount), font_style)
        ws.write(row_num, 1, expense.description, font_style)
        ws.write(row_num, 2, expense.category, font_style)
        ws.write(row_num, 3, str(expense.date), font_style)

    wb.save(response)
    return response

def export_pdf(request):
    context = get_filtered_expenses(request)
    html_string = render_to_string('expenses/pdf-output.html', context)

    pdf = pdfkit.from_string(html_string, False)

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename=Expenses_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.pdf'
    response['Content-Transfer-Encoding'] = 'binary'

    return response
