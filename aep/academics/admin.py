from django.contrib import admin

from import_export import resources, fields, widgets
from import_export.admin import ImportExportActionModelAdmin
from people.models import Student, Staff
from .models import (Course, Resource, Skill, Milestone, Achievement,
    Credential, CourseCompletion, Certificate, SkillMastery)


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
            'anchor_standard',
            'code',
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
            'resources',
            'nrs_min',
            'nrs_max',
            'nrs_type'
        )


class CredentialResource(resources.ModelResource):

    class Meta:
        model = Credential
        fields = (
            'id',
            'title',
            'description'
        )

class CourseCompletionResource(resources.ModelResource):

    student = fields.Field(
        column_name = 'student',
        attribute = 'student',
        widget = widgets.ForeignKeyWidget(Student, 'WRU_ID')
    )

    course = fields.Field(
        column_name = 'course',
        attribute = 'course',
        widget = widgets.ForeignKeyWidget(Course, 'code')
    )

    class Meta:
        model = CourseCompletion
        fields = (
            'id',
            'student',
            'cert_date',
            'certifier',
            'course'
        )


class CertificateResource(resources.ModelResource):

    student = fields.Field(
        column_name = 'student',
        attribute = 'student',
        widget = widgets.ForeignKeyWidget(Student, 'WRU_ID')
    )

    class Meta:
        model = Certificate
        fields = (
            'id',
            'student',
            'cert_date',
            'certifier',
            'credential'
        )

class SkillMasteryResource(resources.ModelResource):

    student = fields.Field(
        column_name = 'student',
        attribute = 'student',
        widget = widgets.ForeignKeyWidget(Student, 'WRU_ID')
    )

    class Meta:
        model = SkillMastery
        fields = (
            'id',
            'student',
            'cert_date',
            'certifier',
            'skill',
            'mastered'
        )


class MilestoneResource(resources.ModelResource):
    class Meta:
        model = Milestone
        fields = (
            'id',
            'title',
            'description'
        )


class AchievementResource(resources.ModelResource):
    student = fields.Field(
        column_name = 'student',
        attribute = 'student',
        widget = widgets.ForeignKeyWidget(Student, 'WRU_ID')
    )

    class Meta:
        model = Achievement
        fields = (
            'id',
            'student',
            'cert_date',
            'certifier',
            'milestone'
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

    list_display = (
        'id',
        'title',
        'code',
        'anchor_standard'
    )

    search_fields = [
        'title',
        'code',
        'anchor_standard',
        'description'
    ]

admin.site.register(Skill, SkillAdmin)


class CourseAdmin(ImportExportActionModelAdmin):

    resource_class = CourseResource

    list_display = (
        'title',
        'code',
        'nrs_min',
        'nrs_max',
        'nrs_type'
    )

    list_editable = (
        'nrs_min',
        'nrs_max',
        'nrs_type'
    )

    search_fields = [
        'title',
        'code',
        'description'
    ]


admin.site.register(Course, CourseAdmin)


class CredenitalAdmin(ImportExportActionModelAdmin):

    resource_class = CredentialResource

    search_fields = [
        'title'
    ]

    list_display = (
        'id',
        'title',
    )

    fields = (
        'title',
        'description',
    )

admin.site.register(Credential, CredenitalAdmin)


class CourseCompletionAdmin(ImportExportActionModelAdmin):

    resource_class = CourseCompletionResource

    search_fields = [
        'course__title',
        'course__code',
        'student__last_name',
        'student__first_name',
        'student__WRU_ID'
    ]

    list_display = (
        'student',
        'course',
        'cert_date',
        'certifier'
    )

    autocomplete_fields = ['student', 'certifier', 'course']

    fields = (
        'cert_date',
    )

admin.site.register(CourseCompletion, CourseCompletionAdmin)


class CertificateAdmin(ImportExportActionModelAdmin):

    resource_class = CertificateResource

    search_fields = [
        'credential__title',
        'student__last_name',
        'student__first_name',
        'student__WRU_ID'
    ]

    list_display = (
        'student',
        'credential',
        'cert_date',
        'certifier'
    )

    autocomplete_fields = ['student', 'certifier', 'credential']

    fields = (
        'cert_date',
    )

admin.site.register(Certificate, CertificateAdmin)

class SkillMasteryAdmin(ImportExportActionModelAdmin):

    resource_class = SkillMasteryResource

    search_fields = [
        'skill__title',
        'student__last_name',
        'student__first_name',
        'student__WRU_ID'
    ]

    list_filter = [
        'mastered'
    ]

    list_display = (
        'student',
        'skill',
        'cert_date',
        'certifier',
    )

    autocomplete_fields = ['student', 'certifier', 'skill']

    fields = (
        'cert_date',
        'mastered'
    )

admin.site.register(SkillMastery, SkillMasteryAdmin)    


class MilestoneAdmin(ImportExportActionModelAdmin):
    resource_class = MilestoneResource

    search_fields = [
        'title'
    ]

    list_display = (
        'id',
        'title',
    )

    fields = (
        'title',
        'description',
    )

admin.site.register(Milestone, MilestoneAdmin)


class AchievementAdmin(ImportExportActionModelAdmin):
    resource_class = AchievementResource

    search_fields = [
        'milestone__title',
        'student__last_name',
        'student__first_name',
        'student__WRU_ID'
    ]

    list_display = (
        'student',
        'milestone',
        'cert_date',
        'certifier'
    )

    autocomplete_fields = ['student', 'certifier', 'milestone']

    fields = (
        'cert_date',
    )

admin.site.register(Achievement, AchievementAdmin)
