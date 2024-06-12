from django.shortcuts import render, redirect
from .models import Source, UserIncome
from django.core.paginator import Paginator
from userpreferences.models import UserPreference
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import json
from django.http import JsonResponse,HttpResponse
from collections import defaultdict
import datetime
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar
import csv
import xlwt
from django.template.loader import render_to_string
import pdfkit
from django.db.models import Sum

# Create your views here.


def search_income(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        income = UserIncome.objects.filter(
            amount__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            date__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            description__icontains=search_str, owner=request.user) | UserIncome.objects.filter(
            source__icontains=search_str, owner=request.user)
        data = income.values()
        return JsonResponse(list(data), safe=False)


# @login_required(login_url='/authentication/login')
# def index(request):
#     categories = Source.objects.all()
#     income = UserIncome.objects.filter(owner=request.user)
#     paginator = Paginator(income, 5)
#     page_number = request.GET.get('page')
#     page_obj = Paginator.get_page(paginator, page_number)
#     currency = UserPreference.objects.get(user=request.user).currency
#     context = {
#         'income': income,
#         'page_obj': page_obj,
#         'currency': currency
#     }
#     return render(request, 'income/index.html', context)
@login_required(login_url='/authentication/login')
def index(request):
    categories = Source.objects.all()
    income = UserIncome.objects.filter(owner=request.user)
    paginator = Paginator(income, 5)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    
    try:
        user_preference = UserPreference.objects.get(user=request.user)
        currency = user_preference.currency
    except UserPreference.DoesNotExist:
        currency = None
    
    context = {
        'income': income,
        'page_obj': page_obj,
        'currency': currency,
        'sources':categories
    }
    return render(request, 'income/index.html', context)



@login_required(login_url='/authentication/login')
def add_income(request):
    sources = Source.objects.all()
    context = {
        'sources': sources,
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'income/add_income.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'income/add_income.html', context)
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'income/add_income.html', context)
        
        if not date:
            messages.error(request, 'date is required')
            return render(request, 'income/add_income.html', context)

        UserIncome.objects.create(owner=request.user, amount=amount, date=date,
                                  source=source, description=description)
        messages.success(request, 'Record saved successfully')

        return redirect('income')


@login_required(login_url='/authentication/login')
def income_edit(request, id):
    income = UserIncome.objects.get(pk=id)
    sources = Source.objects.all()
    context = {
        'income': income,
        'values': income,
        'sources': sources
    }
    if request.method == 'GET':
        return render(request, 'income/edit_income.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'income/edit_income.html', context)
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'income/edit_income.html', context)
        income.amount = amount
        income. date = date
        income.source = source
        income.description = description

        income.save()
        messages.success(request, 'Record updated successfully')

        return redirect('income')


def delete_income(request, id):
    income = UserIncome.objects.get(pk=id)
    income.delete()
    messages.success(request, 'record removed')
    return redirect('income')


def income_sources_data(request):
    incomes = UserIncome.objects.filter(owner=request.user)
    finalrep = {}

    def get_source(income):
        return income.source  # Assuming income has a source field

    # Ensure unique categories (optional)
    source_list = list(set(map(get_source, incomes)))

    def get_source_income_amount(source):
        amount = 0
        filtered_by_source = incomes.filter(source=source)
        for item in filtered_by_source:
            amount += item.amount
        return amount

    for source in source_list:
        # Update finalrep with 0 if source is empty
        finalrep.setdefault(source, 0)  # defaultdict-like behavior
        finalrep[source] = get_source_income_amount(source)

    return JsonResponse({'income_source_data': finalrep}, safe=False)
    

def income_summary_rest(request):
    try:
        incomes = UserIncome.objects.filter(owner=request.user)

        summary = defaultdict(lambda: {'total_amount': 0, 'details': []})
        monthly_data = defaultdict(float)
        monthwise_income_data = defaultdict(list)

        for income in incomes:
            month_key = income.date.strftime('%Y-%m')
            monthly_data[month_key] += income.amount
            summary[income.source]['total_amount'] += income.amount
            summary[income.source]['details'].append({
                'id': income.id,
                'amount': income.amount,
                'description': income.description,
                'date': income.date.strftime('%Y-%m-%d')
            })
            monthwise_income_data[month_key].append({
                'id': income.id,
                'amount': income.amount,
                'description': income.description,
                'date': income.date.strftime('%Y-%m-%d')
            })

        summary_data = {
            'months': list(monthly_data.keys()),
            'sources': list(summary.keys()),
            'data': list(summary.values()),
            'monthwise_income_data': dict(monthwise_income_data)
        }

        return JsonResponse(summary_data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def incomestats_view(request):
    return render(request, 'income/incomestats.html')

def get_monday_of_current_week(date):
    # Find the Monday of the current week
    monday = date - timedelta(days=date.weekday())
    return monday

def get_sunday_of_current_week(date):
    # Find the Sunday of the current week
    sunday = date + timedelta(days=(6 - date.weekday()))
    return sunday

def metric_card_view_income(request):
    try:
        today = datetime.today().date()
        start_of_year = datetime(today.year, 1, 1).date()

        monday_of_current_week = get_monday_of_current_week(today)
        sunday_of_current_week = get_sunday_of_current_week(today)

        # Filter incomes by date
        incomes = UserIncome.objects.filter(owner=request.user)

        daily_incomes = incomes.filter(date=today).count()
        weekly_incomes = incomes.filter(date__gte=monday_of_current_week, date__lte=sunday_of_current_week).count()
        yearly_incomes = incomes.filter(date__gte=start_of_year, date__lte=today).count()

        monthly_incomes = {}
        current_month = today.month
        current_year = today.year
        while current_year > start_of_year.year or (current_year == start_of_year.year and current_month >= start_of_year.month):
            start_of_month = datetime(current_year, current_month, 1).date()
            end_of_month = start_of_month + relativedelta(months=1) - timedelta(days=1)
            monthly_incomes_count = incomes.filter(date__gte=start_of_month, date__lte=end_of_month).count()
            monthly_incomes[start_of_month.strftime('%Y-%m')] = monthly_incomes_count
            current_month -= 1
            if current_month == 0:
                current_month = 12
                current_year -= 1

        # Get the total incomes for the current month
        current_month_key = datetime(today.year, today.month, 1).strftime('%Y-%m')
        monthly_incomes = monthly_incomes.get(current_month_key, 0)

        data = {
            'daily_incomes': daily_incomes,
            'weekly_incomes': weekly_incomes,
            'monthly_incomes': monthly_incomes,
            'yearly_incomes': yearly_incomes

        }

        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def metric_card_view2_income(request):
    try:
        today = datetime.today().date()
        start_of_year = datetime(today.year, 1, 1).date()

        monday_of_current_week = get_monday_of_current_week(today)
        sunday_of_current_week = get_sunday_of_current_week(today)
        # Filter incomes by date
        incomes = UserIncome.objects.filter(owner=request.user)

        daily_incomes = incomes.filter(date=today)
        weekly_incomes = incomes.filter(date__gte=monday_of_current_week, date__lte=sunday_of_current_week)
        yearly_incomes = incomes.filter(date__gte=start_of_year, date__lte=today)

        total_daily_incomes = sum(income.amount for income in daily_incomes)
        total_weekly_incomes = sum(income.amount for income in weekly_incomes)
        total_yearly_incomes = sum(income.amount for income in yearly_incomes)

        monthly_totals = {}
        current_month = today.month
        current_year = today.year

        while current_year > start_of_year.year or (current_year == start_of_year.year and current_month >= start_of_year.month):
            start_of_month = datetime(current_year, current_month, 1).date()
            end_of_month = start_of_month + relativedelta(months=1) - timedelta(days=1)
            monthly_incomes = incomes.filter(date__gte=start_of_month, date__lte=end_of_month)
            total_monthly_incomes = sum(income.amount for income in monthly_incomes)
            monthly_totals[start_of_month.strftime('%Y-%m')] = total_monthly_incomes

            current_month -= 1
            if current_month == 0:
                current_month = 12
                current_year -= 1

        current_month_key = datetime(today.year, today.month, 1).strftime('%Y-%m')
        total_monthly_incomes = monthly_totals.get(current_month_key, 0)

        data = {
            'total_daily_incomes': total_daily_incomes,
            'total_weekly_incomes': total_weekly_incomes,
            'monthly_totals': total_monthly_incomes,
            'total_yearly_incomes': total_yearly_incomes
        }

        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

def income_yearwise_summary(request):
    try:
        today = datetime.today().date()
        start_of_year = datetime(today.year, 1, 1).date()

        # Filter incomes for the current year
        incomes = UserIncome.objects.filter(owner=request.user, date__gte=start_of_year, date__lte=today)

        # Dictionary to store monthly totals
        monthly_totals = {}

        # Loop through each month of the current year
        for month in range(1, 13):
            start_of_month = datetime(today.year, month, 1).date()
            end_of_month = start_of_month + relativedelta(months=1) - timedelta(days=1)

            # Filter incomes for the current month
            monthly_incomes = incomes.filter(date__gte=start_of_month, date__lte=end_of_month)

            # Calculate total incomes for the month
            total_monthly_incomes = sum(income.amount for income in monthly_incomes)

            # Get month name
            month_name = start_of_month.strftime('%B')

            # Store the total incomes in the dictionary
            monthly_totals[month_name] = total_monthly_incomes

        return JsonResponse(monthly_totals, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
def income_weekwise_summary(request):
    try:
        today = datetime.today().date()
        start_of_week = today - timedelta(days=today.weekday())  # Start of the week (Monday)
        end_of_week = start_of_week + timedelta(days=6)  # End of the week (Sunday)

        # Filter incomes by date for the current week
        incomes = UserIncome.objects.filter(owner=request.user, date__gte=start_of_week, date__lte=end_of_week)

        week_incomes = {day: 0 for day in calendar.day_name}  # Initialize dictionary with days of the week

        for income in incomes:
            day_name = calendar.day_name[income.date.weekday()]
            week_incomes[day_name] += income.amount

        return JsonResponse(week_incomes, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
def get_filtered_incomes(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    source = request.GET.get('source')

    incomes = UserIncome.objects.filter(owner=request.user)
    
    if start_date:
        incomes =incomes.filter(date__gte=start_date)
    if end_date:
        incomes =incomes.filter(date__lte=end_date)
    if source:
        incomes =incomes.filter(source=source)

    total = incomes.aggregate(Sum('amount'))['amount__sum'] or 0

    context = {
        'incomes': incomes,
        'start_date': start_date,
        'end_date': end_date,
        'source':source,
        'total':total
    }
    

    return context

def incomeexport_csv(request):
    incomes = get_filtered_incomes(request)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Incomes' + \
        str(datetime.now()) + '.csv'

    writer = csv.writer(response)
    writer.writerow(['Amount', 'Description', 'Source', 'Date'])

    for income in incomes:
        writer.writerow([income.amount, income.description, income.source, income.date])

    return response

def incomeexport_excel(request):
    incomes = get_filtered_incomes(request)

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Incomes' + \
        str(datetime.now()) + '.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Incomes')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Amount', 'Description', 'Source', 'Date']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()

    for income in incomes:
        row_num += 1
        ws.write(row_num, 0, str(income.amount), font_style)
        ws.write(row_num, 1, income.description, font_style)
        ws.write(row_num, 2, income.source, font_style)
        ws.write(row_num, 3, str(income.date), font_style)

    wb.save(response)
    return response

def incomeexport_pdf(request):
    context = get_filtered_incomes(request)
    html_string = render_to_string('income/incomepdf-output.html', context)

    pdf = pdfkit.from_string(html_string, False)

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename=Incomes_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.pdf'
    response['Content-Transfer-Encoding'] = 'binary'

    return response
