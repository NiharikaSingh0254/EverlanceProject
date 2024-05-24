from django.urls import path
from . import views

from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', views.index, name="expenses"),
    path('add-expense', views.add_expense, name="add-expenses"),
    path('edit-expense/<int:id>', views.expense_edit, name="expense-edit"),
    path('expense-delete/<int:id>', views.delete_expense, name="expense-delete"),
    path('search-expenses', csrf_exempt(views.search_expenses),
         name="search_expenses"),
    path('expense_category_summary', views.expense_category_summary,
         name="expense_category_summary"),
    path('expensestats', views.expensestats_view,
         name="expensestats"),
    path('expense_summary_rest', views.expense_summary_rest,
         name="expense_summary_rest"),
#     path('last_3months_stats',views.last_3months_stats,name='last_3months_stats'),
    path('metric_card_view',views.metric_card_view1,name="metric_card_view"),
    path('metric_card_view2',views.metric_card_view2,name="metric_card_view2"),
    path('expense_yearwise_summary', views.expense_yearwise_summary,
         name="expense_yearwise_summary"),
    path('expense_weekwise_summary', views.expense_weekwise_summary,
         name="expense_weekwise_summary"),
    path('export_csv',views.export_csv,name='export-csv'),
    path('export_excel',views.export_excel,name='export-excel'),
    path('export_pdf',views.export_pdf,name='export-pdf')
]
