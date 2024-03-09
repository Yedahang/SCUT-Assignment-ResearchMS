from django.contrib import admin
from .models import Contact, Office, RearchRooms, Secretary, Organization, ProjectResearcher

# admin.site.register([Contact, Office, RearchRooms])


admin.site.site_header = '科研管理系统'
admin.site.site_title = '科研管理系统'
admin.site.index_title = '欢迎使用科研管理系统'
# 联系人
class ContactAdmin(admin.ModelAdmin):
    list_display = ('contact_id', 'name', 'office_phone', 'mobile_phone', 'email')
    # list_editable = ('name', 'office_phone', 'mobile_phone', 'email')
    search_fields = ('name',) # 表示以name,id 作为搜索字段
admin.site.register(Contact,ContactAdmin)

class SecretaryAdmin(admin.ModelAdmin):
    list_display = ('secretary_id', 'employee_id', 'name', 'gender', 'age',"hire_date","responsibilities")
    # list_editable = ('name', 'office_phone', 'mobile_phone', 'email')
    search_fields = ('name','employee_id',) #
admin.site.register(Secretary,SecretaryAdmin)


class OrganizationContactInline(admin.StackedInline):
    model = Organization.contacts.through
    verbose_name = '单位相关联系人'  # 设置内联模型的名称
    verbose_name_plural = '单位相关联系人'  # 设置内联模型的复数名称
    min_num = 0
    extra = 0

class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('organization_id', 'organization_name', 'address', 'leader','display_contacts')
    list_display_links = ('organization_id', 'organization_name',)  # 设置字段链接
    search_fields = ('organization_name', 'address', 'leader',)
    # inlines = [OrganizationContactInline]
    filter_horizontal = ('contacts',)
    def display_contacts(self,obj):
        contacts = obj.contacts.all()
        return ", ".join(str(contact) for contact in contacts)  # 以逗号分隔显示联系人姓名
    display_contacts.short_description = '联系人'  # 设置显示名称
    # list_editable = ('name', 'office_phone', 'mobile_phone', 'email')
    # search_fields = ('name','contact_id') # 表示以name,id 作为搜索字段

admin.site.register(Organization,OrganizationAdmin)
# Register your models here.

from .models import RearchRooms,Researcher
class ResearchersInline(admin.TabularInline):
    model = Researcher
    extra = 0
class RearchRoomsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'introduction', 'secretary','director','director_start_date','director_tenure')
    list_display_links = ('name','secretary','director',)
    # inlines = [ResearchersInline]
    # list_editable = ('name', 'office_phone', 'mobile_phone', 'email')
    search_fields = ('name',)
admin.site.register(RearchRooms,RearchRoomsAdmin)

from .models import Office
class OfficeAdmin(admin.ModelAdmin):
    list_display = ('id','research_room','office_area','address')
    list_display_links = ('address',)
    search_fields = ('address',)
admin.site.register(Office,OfficeAdmin)
#
from .models import Researcher
class ResearcherAdmin(admin.ModelAdmin):
    list_display = ('researcher_id', 'employee_id', 'name', 'gender',"title",
                    "age","research_area","research_room",
                    )
    list_display_links =('employee_id', 'name',)
    search_fields = ('address',)
#     list_display = ('researcher_id')
#     # list_editable = ('name', 'office_phone', 'mobile_phone', 'email')
#     search_fields = ('name') # 表示以name,id 作为搜索字段
admin.site.register(Researcher,ResearcherAdmin)

from .models import Project
class collaboratorsInline(admin.StackedInline):
    model = Project.collaborators.through
    verbose_name = '合作单位'  # 设置内联模型的名称
    verbose_name_plural = '合作方信息'  # 设置内联模型的复数名称
    min_num = 0
    extra = 0

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'collaborator':
            # 自定义外键字段的显示和选择选项
            kwargs['queryset'] = Organization.objects.filter(is_active=True)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class ProjectResearcherInline(admin.TabularInline):
    model = ProjectResearcher
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('project_id', 'projectCode', 'project_name',"research_content",
                    "total_funding","start_date","completion_date","client","qualityMonitor","display_collaborators"
                    )
    search_fields = ('projectCode', 'project_name',)  # 设置字段链接
    list_display_links = ('projectCode', )
    filter_horizontal = ('researcher',)
    inlines = [collaboratorsInline,ProjectResearcherInline]
    exclude = ('collaborators',)
    def display_collaborators(self,obj):
        collaborators = obj.collaborators.all()
        return ", ".join(str(collaborator) for collaborator in collaborators)  # 以逗号分隔显示联系人姓名
    display_collaborators.short_description = '合作方'  # 设置显示名称
admin.site.register(Project,ProjectAdmin)

from .models import ProjectResearcher
class ProjectResearcherAdmin(admin.ModelAdmin):
    list_display = ('project', 'researcher', 'subproject',"join_date",
                    "workload","discretionary_funds"
                    )
    # list_display_links = ('project_name',)  # 设置字段链接
admin.site.register(ProjectResearcher,ProjectResearcherAdmin)


from .models import Subproject
class SubprojectAdmin(admin.ModelAdmin):
    list_display = ('subproject_id', 'project', 'leader','completion_time',"discretionary_funds",
                    "tech_specification",
                    )
#     list_display = ('researcher_id')
#     # list_editable = ('name', 'office_phone', 'mobile_phone', 'email')
#     search_fields = ('name') # 表示以name,id 作为搜索字段
admin.site.register(Subproject,SubprojectAdmin)


from .models import Achievement
from .models import Paper,Patents, SoftwareCopyrights
class PaperInline(admin.TabularInline):
    model = Paper
    extra = 0
class PatentsInline(admin.TabularInline):
    model = Patents
    extra = 0
class SoftwareCopyrightsInline(admin.TabularInline):
    model = SoftwareCopyrights
    extra = 0

class AchievementAdmin(admin.ModelAdmin):
    list_display = ('achievement_id', 'achievement_name', 'achievement_date',"ranking",
                    "project",
                    )
    list_display_links = ('achievement_name', 'project',)  # 设置字段链接
    filter_horizontal = ('contributors',)
    inlines = [PaperInline,PatentsInline,SoftwareCopyrightsInline]
    # list_display = ('researcher_id')
#     # list_editable = ('name', 'office_phone', 'mobile_phone', 'email')
#     search_fields = ('name') # 表示以name,id 作为搜索字段
admin.site.register(Achievement,AchievementAdmin)

class PaperAdmin(admin.ModelAdmin):
    list_display = ('id', 'paper_name', 'paper_date',"achievement",
                    )
    list_display_links = ('paper_name', 'achievement',)  # 设置字段链接
    # list_display = ('researcher_id')
#     # list_editable = ('name', 'office_phone', 'mobile_phone', 'email')
#     search_fields = ('name') # 表示以name,id 作为搜索字段
admin.site.register(Paper,PaperAdmin)


# 自定义管理后台显示
class PatentsAdmin(admin.ModelAdmin):
    list_display = ('patent_id', 'patent_name', 'patent_type', 'achievement')
    list_filter = ('patent_type', 'achievement')
    list_display_links = ('patent_name', 'achievement',)
    search_fields = ('patent_name',)
    # 其他自定义配置...
admin.site.register(Patents, PatentsAdmin)

class CopyrightsAdmin(admin.ModelAdmin):
    list_display = ('copyright_id', 'copyright_name', 'achievement')
    list_filter = ('achievement',)
    search_fields = ('copyright_name',)
    list_display_links = ('copyright_name', 'achievement',)
    # 其他自定义配置...
admin.site.register(SoftwareCopyrights, CopyrightsAdmin)
