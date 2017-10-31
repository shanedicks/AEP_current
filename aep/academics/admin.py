from django.contrib import admin

from import_export import resources
from import_export.admin import ImportExportActionModelAdmin

from .models import Course, Resource, Skill
# Register your models here.


class ResourceResource(resources.ModelResource):

    class Meta:
        model = Resource
        fields = (
            'id',
            'title',
            'description'
        )


class SkillResource(resources.ModelResource):

    class Meta:
        model = Skill
        fields = (
            'id',
            'title',
            'ccrs',
            'description',
            'resources'
        )


class CourseResource(resources.ModelResource):

    class Meta:
        model = Course
        fields = (
            'id',
            'title',
            'code',
            'description',
            'g_suite_id',
            'skills',
            'resources'
        )


class ResourceAdmin(ImportExportActionModelAdmin):

    resource_class = ResourceResource

    list_display = ('title',)

    search_fields = [
        'title',
        'description'
    ]


admin.site.register(Resource, ResourceAdmin)


class SkillAdmin(ImportExportActionModelAdmin):

    resource_class = SkillResource

    list_display = ('title',)

    search_fields = [
        'title',
        'ccrs',
        'description'
    ]


admin.site.register(Skill, SkillAdmin)


class CourseAdmin(ImportExportActionModelAdmin):

    resource_class = CourseResource

    list_display = (
        'title',
        'code'
    )

    search_fields = [
        'title',
        'code',
        'description'
    ]


admin.site.register(Course, CourseAdmin)
