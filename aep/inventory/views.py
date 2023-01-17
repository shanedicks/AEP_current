from django.apps import apps
from django.db.models import Exists, OuterRef
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils import timezone
from django.views.generic import (
    DetailView, ListView, UpdateView,
    CreateView)
from .models import Category, Item, Ticket
from .forms import TicketForm, SelectTicketItemForm, TicketUpdateForm



class CategoryListView(LoginRequiredMixin, ListView):

    model = Category
    template_name = 'inventory/category_list.html'

class SelectCategoryView(LoginRequiredMixin, ListView):

    model=Category
    template_name = "inventory/select_category.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'student_slug' in self.kwargs:
            context['student'] = apps.get_model(
                'people', 'Student'
            ).objects.get(slug=self.kwargs['student_slug'])
        if 'staff_slug' in self.kwargs:
            context['staff'] = apps.get_model(
                'people', 'Staff'
            ).objects.get(slug=self.kwargs['staff_slug'])
        return context

class ItemListView(LoginRequiredMixin, ListView):

    model = Item
    template_name = "inventory/item_list.html"

    def get_queryset(self):
        open_ticket = Ticket.objects.filter(
            item=OuterRef('pk'),
            returned_date__isnull=True
        )
        queryset = Item.objects.all()
        if 'category' in self.kwargs:
            category = self.kwargs['category']
            queryset = queryset.filter(category=category)
        if 'available' in self.kwargs:
            queryset = queryset.exclude(Exists(open_ticket))
        return queryset


class CreateTicketView(LoginRequiredMixin, CreateView):

    model = Ticket
    form_class = TicketForm
    template_name = "inventory/create_ticket.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if 'category' in self.kwargs:
            kwargs['category'] = self.kwargs['category']
        if self.request.GET:
            kwargs.update(self.request.GET)
        return kwargs

    def get_success_url(self):
        return reverse("inventory:category list")


class UpdateTicketView(LoginRequiredMixin, UpdateView):

    model = Ticket
    form_class = TicketUpdateForm
    template_name = "inventory/update_ticket.html"

    def get_success_url(self):
        try:
            url = self.object.student.get_absolute_url()
        except AttributeError:
            url = self.object.staff.get_absolute_url()
        return url

class SelectTicketItemView(LoginRequiredMixin, CreateView):

    model = Ticket
    form_class = SelectTicketItemForm
    template_name = "inventory/select_item.html"

    def form_valid(self, form):
        ticket = form.save(commit=False)
        person_dict = self.get_person_dict()
        try:
            ticket.staff = person_dict['staff']
        except KeyError:
            try:
                ticket.student = person_dict['student']
            except KeyError:
                form.add_error(
                    'student',
                    "This form can't be submitted"
                )
                return self.form_invalid(form)
        ticket.save()
        return super().form_valid(form)

    def get_person_dict(self):
        person_dict = {}
        if 'student_slug' in self.kwargs:
            person = apps.get_model(
                'people', 'Student'
            ).objects.get(slug=self.kwargs['student_slug'])
            person_dict['student'] = person
        if 'staff_slug' in self.kwargs:
            person = apps.get_model(
                'people', 'Staff'
            ).objects.get(slug=self.kwargs['staff_slug'])
            person_dict['staff'] = person
        return person_dict

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'category' in self.kwargs:
            context['category'] = Category.objects.get(pk=self.kwargs['category'])
        person_dict = self.get_person_dict()
        context.update(**person_dict)
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if 'category' in self.kwargs:
            kwargs['category'] = self.kwargs['category']
        return kwargs

    def get_success_url(self):
        person = self.get_person_dict().popitem()[1] 
        return person.get_absolute_url()
