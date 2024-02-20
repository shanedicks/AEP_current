from django.contrib import admin

from import_export import resources, fields, widgets
from import_export.admin import ImportExportActionModelAdmin

from people.models import Student, Staff
from .models import Category, Item, Ticket



class CategoryResource(resources.ModelResource):
	class Meta:
		model = Category
		fields = (
			'name',
			'description',
		)


class ItemResource(resources.ModelResource):
	
	category = fields.Field(
		column_name = 'category',
		attribute = 'category',
		widget = widgets.ForeignKeyWidget(Category, 'name')
	)

	class Meta:
		model = Item
		fields = (
			"name",
			"state_tag",
			'item_id',
		)


class TicketResource(resources.ModelResource):

	student = fields.Field(
		column_name = 'student',
		attribute = 'student',
		widget = widgets.ForeignKeyWidget(Student, 'WRU_ID')
	)

	class Meta:
		model = Ticket
		fields = (
			'item',
			'staff',
			'issued_date',
			'returned_date'
		)

class CategoryAdmin(ImportExportActionModelAdmin):

	resource_class = CategoryResource

	list_display = (
		'id',
		'name'
	)

	search_fields = (
		'name',
		'description'
	)

	fields = (
		'name',
		'description'
	)

admin.site.register(Category, CategoryAdmin)


class ItemAdmin(ImportExportActionModelAdmin):

	resource_class = ItemResource

	list_display = (
		'id',
		'item_id',
		'category',
		'name',
		'state_tag'
	)

	search_fields = (
		'item_id',
		'name',
		'state_tag'
	)

	fields = (
		'item_id',
		'category',
		'name',
		'state_tag'
	)

	list_filter = ['category']

admin.site.register(Item, ItemAdmin)


class TicketAdmin(ImportExportActionModelAdmin):

	resource_class = TicketResource

	list_display = (
		'item',
		'get_category',
		'student',
		'staff',
		'issued_date',
		'returned_date',
		'return_req_date'
	)

	search_fields = (
		'student__last_name',
		'student__first_name',
		'student__WRU_ID',
		'staff__last_name',
		'staff__first_name',
		'item__name',
		'item__item_id'
	)

	fields = (
		'item',
		'student',
		'staff',
		'issued_date',
		'returned_date',
		'return_req_date'
	)

	autocomplete_fields = [
		'item',
		'student',
		'staff'
	]

	list_filter = ['item__category']

	list_select_related = ['item']

	@admin.display(description='Item Category', ordering='item__category')
	def get_category(self, obj):
		return obj.item.category

admin.site.register(Ticket, TicketAdmin)
