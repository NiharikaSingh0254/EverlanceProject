from django.urls import path
from . import views

from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', views.index, name="income"),
    path('add-income', views.add_income, name="add-income"),
    path('edit-income/<int:id>', views.income_edit, name="income-edit"),
    path('income-delete/<int:id>', views.delete_income, name="income-delete"),
    path('search-income', csrf_exempt(views.search_income),
         name="search_income"),
    path('income_sources_data',views.income_sources_data,name="income_sources_data"),
    path('income_summary_rest',views.income_summary_rest,name='income_summary_rest'),
    path('incomestats',views.incomestats_view,name="incomestats"),
    path('metric_card_view_income',views.metric_card_view_income,name="metric_card_view_income"),
    path('metric_card_view2_income',views.metric_card_view2_income,name="metric_card_view2_income"),
    path('income_yearwise_summary', views.income_yearwise_summary,
         name="income_yearwise_summary"),
    path('income_weekwise_summary', views.income_weekwise_summary,
         name="income_weekwise_summary"),
    path('incomeexport_csv',views.incomeexport_csv,name='incomeexport-csv'),
    path('incomeexport_excel',views.incomeexport_excel,name='incomeexport-excel'),
    path('incomeexport_pdf',views.incomeexport_pdf,name='incomeexport-pdf')
]
