from django.urls import path, re_path, include
from . import views 

app_name = 'inventory'

items_patterns = [
	path('',
		views.ItemListView.as_view(),
		name="items list"),
	path('available/',
		views.ItemListView.as_view(),
		{'available': True},
		name="available items list"),
]

single_category_patterns = [
	path('items/',
		include(items_patterns)),
	path('assign/',
		views.CreateTicketView.as_view(),
		name="create ticket")
]

person_patterns = [
	path('',
		views.SelectCategoryView.as_view(),
		name='select category'),
	path('<category>/',
		views.SelectTicketItemView.as_view(),
		name='select item')
]

urlpatterns = [
	path('',
		views.CategoryListView.as_view(),
		name="category list"),
	path('<category>/',
		include(single_category_patterns)),
	path('student/<student_slug>/',
		include(person_patterns)),
	path('staff/<staff_slug>/',
		include(person_patterns)),
	path('items/',
		include(items_patterns)),
]