from datetime import time
from django.apps import apps
from django.views.generic import DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Semester


class SemesterListView(LoginRequiredMixin, ListView):

    model = Semester
    template_name = 'semesters/semester_list.html'
    paginate_by = 20


class SemesterDetailView(LoginRequiredMixin, DetailView):

    model = Semester
    template_name = 'semesters/semester_detail.html'

    def get_sites_table_data(self, **kwargs):
        sites = apps.get_model('sections', 'Site').objects.filter(
                sections__semester=self.object
            ).distinct()
        sections = self.object.get_sections()
        sites_dict = {}
        for site in sites:
            site_sections = sections.filter(site=site)
            sites_dict[site] = self.object.get_att_rate_list(site_sections)
        days_len = max([len(v) for v in sites_dict.values()])
        return(days_len, sites_dict)

    def get_times_table_data(self, **kwargs):
        sections = self.object.get_sections()
        morning = sections.filter(start_time__lt=time(hour=11, minute=30))
        afternoon = sections.filter(
            start_time__gte=time(hour=11, minute=30),
            start_time__lt=time(hour=5, minute=30)
        )
        evening = sections.filter(start_time__gte=time(hour=5, minute=30))
        times_dict = {
            'Morning': self.object.get_att_rate_list(morning),
            'Afternoon': self.object.get_att_rate_list(afternoon),
            'Evening': self.object.get_att_rate_list(evening)
        }
        days_len = max([len(v) for v in times_dict.values()])
        return (days_len, times_dict)

    def get_context_data(self, **kwargs):
        context = super(SemesterDetailView, self).get_context_data(**kwargs)
        sites_table_data = self.get_sites_table_data()
        context['sites'] = sites_table_data[1]
        context['days'] = [i + 1 for i in range(sites_table_data[0])]
        times_table_data = self.get_times_table_data()
        context['times'] = times_table_data[1]
        return context
