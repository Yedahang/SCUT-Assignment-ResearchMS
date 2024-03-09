import json
import time

from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import transaction, IntegrityError, connection
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from decimal import Decimal
from django.core.serializers.json import DjangoJSONEncoder
from app import models
from .tools import query_one_dict, query_all_dict


class DecimalEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)

'''
基础处理类，其他处理继承这个类
'''
class BaseView(View):
    '''
    检查指定的参数是否存在
    存在返回 True
    不存在返回 False
    '''
    def isExit(param):

        if (param == None) or (param == ''):
            return False
        else:
            return True

    def check_exist(item_attr,replace ="-"):
        return replace if item_attr=="" or item_attr==None else item_attr
    '''
    转换分页查询信息
    '''
    def parasePage(pageIndex, pageSize, pageTotal, count, data):

        return {'pageIndex': pageIndex, 'pageSize': pageSize, 'pageTotal': pageTotal, 'count': count, 'data': data}

    '''
    转换分页查询信息
    '''
    def parasePage(pageIndex, pageSize, pageTotal, count, data):
        return {'pageIndex': pageIndex, 'pageSize': pageSize, 'pageTotal': pageTotal, 'count': count, 'data': data}

    '''
    成功响应信息
    '''
    def success(msg='处理成功'):
        resl = {'code': 0, 'msg': msg}
        return HttpResponse(json.dumps(resl), content_type='application/json; charset=utf-8')

    '''
    成功响应信息, 携带数据
    '''
    def successData(data, msg='处理成功'):
        resl = {'code': 0, 'msg': msg, 'data': data}
        return HttpResponse(json.dumps(resl,cls=DecimalEncoder), content_type='application/json; charset=utf-8')

    '''
    系统警告信息
    '''
    def warn(msg='操作异常，请重试'):
        resl = {'code': 1, 'msg': msg}
        return HttpResponse(json.dumps(resl), content_type='application/json; charset=utf-8')

    '''
    系统异常信息
    '''
    def error(msg='系统异常'):
        resl = {'code': 2, 'msg': msg}
        return HttpResponse(json.dumps(resl), content_type='application/json; charset=utf-8')

'''
系统请求处理
'''
class SysView(BaseView):

    def get(self, request, module, *args, **kwargs):

        if module == 'login':
            return render(request, 'login.html')

        elif module == 'exit':

            del request.session["user"]
            del request.session["type"]

            return HttpResponseRedirect('/jobs/login')

        if module == 'info':

            return SysView.getSessionInfo(request)

        elif module == 'show':

            return render(request, 'index.html')

        elif module == 'sysNum':
            return SysView.getSysNums(request)

    def post(self, request, module, *args, **kwargs):

        if module == 'login':

            return SysView.login(request)

        if module == 'info':
            return SysView.updSessionInfo(request)

        if module == 'pwd':
            return SysView.updSessionPwd(request)

    def login(request):

        userName = request.POST.get('userName')
        passWord = request.POST.get('passWord')

        user = models.Users.objects.filter(userName=userName)

        if (user.exists()):

            user = user.first()
            if user.passWord == passWord:
                request.session["user"] = user.id
                request.session["type"] = user.type

                return SysView.success()
            else:
                return SysView.warn('用户密码输入错误')
        else:
            return SysView.warn('用户名输入错误')

    def getSessionInfo(request):

        user = request.session.get('user')

        data = models.Users.objects.filter(id=user)

        resl = {}
        for item in data:
            resl = {
                'id': item.id,
                'userName': item.userName,
                'passWord': item.passWord,
                'gender': item.gender,
                'name': item.name,
                'age': item.age,
                'phone': item.phone,
                'type': item.type,
            }

        return SysView.successData(resl)

    def getSysNums(request):

        resl = {
            'ResearcherTotal' : models.Researcher.objects.all().count(),
            'ProjectTotal' : models.Project.objects.all().count(),
            'AchievementTotal' : models.Achievement.objects.all().count(),
        }

        return BaseView.successData(resl)

    def updSessionInfo(request):

        user = request.session.get('user')

        models.Users.objects.filter(id=user).update(
            userName=request.POST.get('userName'),
            name=request.POST.get('name'),
            age=request.POST.get('age'),
            gender=request.POST.get('gender'),
            phone=request.POST.get('phone'),
        )

        return SysView.success()

    def updSessionPwd(request):

        user = request.session.get('user')

        models.Users.objects.filter(id=user).update(
            passWord=request.POST.get('password'),
        )

        return SysView.success()

'''
研究室信息管理
'''
class ResearchRoomsView(BaseView):

    def get(self, request, module, *args, **kwargs):

        if module == 'show':
            secretaries = models.Secretary.objects.all().values()
            return render(request, 'researchRooms.html',{'secretaries': list(secretaries)})
        elif module == 'info':
            return self.getInfo(request)
        elif module == 'page':
            return self.getPageInfo(request)
        else:
            return self.error()

    def post(self, request, module, *args, **kwargs):

        if module == 'add':
            return self.addInfo(request)
        elif module == 'upd':
            return self.updInfo(request)
        elif module == 'del':
            return self.delInfo(request)
        else:
            return self.error()

    def getInfo(self, request):
        researchRoom_id = request.GET.get('id')
        # 事务管理
        try:
            with transaction.atomic():
                data = models.RearchRooms.objects.filter(id=researchRoom_id).first()
                # 只有属于研究室的人员才能担任主任 故传输符合条件的内容到前端
                directors = models.Researcher.objects.filter(research_room_id=researchRoom_id).all().values()
        except Exception as e:
            # 如果发生错误，回滚事务
            transaction.rollback()

        directors = list(directors)
        resl = {
            'id': data.id,
            'name': data.name,
            'introduction': data.introduction,
            'directors':directors,
            'secretary_Id':data.secretary.secretary_id if data.secretary!=None else "",
            'director_id':data.director.researcher_id if data.director!=None else "",
            'director_start_date': data.director_start_date,
            'director_tenure': data.director_tenure,
        }

        return BaseView.successData(resl)

    def getPageInfo(self, request):

        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        name = request.GET.get('name','').strip()

        qruery = Q()

        if BaseView.isExit(name):
            qruery = qruery & Q(name__contains=name)

        # data = models.Colleges.objects.filter(qruery)
        data = models.RearchRooms.objects.filter(qruery).order_by('id')
        paginator = Paginator(data, pageSize)

        resl = []

        for item in list(paginator.page(pageIndex)):
            secretary_name = item.secretary.name if item.secretary is not None else ""
            director_name = item.director.name if item.director is not None else ""

            temp = {
                'id': item.id,
                'name': item.name,
                'introduction': item.introduction,
                'secretary_name': secretary_name,
                'director_name':director_name,
                'director_start_date':item.director_start_date,
                'director_tenure':item.director_tenure
            }
            resl.append(temp)

        pageData = BaseView.parasePage(pageIndex, pageSize,
                                   paginator.page(pageIndex).paginator.num_pages,
                                   paginator.count, resl)

        return BaseView.successData(pageData)

    def addInfo(self,request):
        researchRoom_name = request.POST.get('researchRoom_name_add')
        introduction = request.POST.get('introduction_add')
        secretary_Id = request.POST.get('secretary_Id_add') #秘书id
        director_id = request.POST.get('director_id_add')
        director_start_date_add = request.POST.get('director_start_date_add')
        director_tenure_add = request.POST.get('director_tenure_add')
        if secretary_Id != "":
            # 有秘书
            secretary =  models.Secretary.objects.get(secretary_id=secretary_Id)
        else:
            #   没有秘书
            secretary = None
        director = models.Researcher.objects.get(researcher_id=director_id) \
                    if director_id !="" else None
        if not BaseView.isExit(researchRoom_name):
            return BaseView.error(msg="研究室名称不能为空")
        try:
            models.RearchRooms.objects.create(name=researchRoom_name,
                                              introduction=introduction,
                                              secretary=secretary,
                                              director = director,
                                              director_start_date = director_start_date_add \
                                                  if BaseView.isExit(director_start_date_add) else None,
                                              director_tenure =  director_tenure_add \
                                                  if BaseView.isExit(director_tenure_add) else None,
                                              )
        except IntegrityError as e:
            error_message = '错误'+e.__str__()
            # 自定义错误提示
            return BaseView.error(msg=error_message)
        except ValidationError as e:
            error_message = '错误'+e.__str__()
            # 自定义错误提示
            return BaseView.error(msg=error_message)
        return BaseView.success()

    def updInfo(self, request):
        secretary_Id= request.POST.get('secretary_Id')
        director_Id= request.POST.get('director_id')
        # 事务管理
        try:
            with transaction.atomic():
                secretary = models.Secretary.objects.get(secretary_id=secretary_Id) if secretary_Id != "" else None
                director = models.Researcher.objects.get(researcher_id=director_Id) if director_Id != "" else None
                models.RearchRooms.objects.filter(id=request.POST.get('id')) \
                    .update(
                    name=request.POST.get('name'),
                    introduction=request.POST.get('introduction'),
                    secretary=secretary,
                    director=director,
                    director_start_date=request.POST.get('director_start_date'),
                    director_tenure=request.POST.get('director_tenure'),
                )
        except Exception as e:
            # 如果发生错误，回滚事务
            transaction.rollback()
        except IntegrityError as e:
            error_message = '错误'+e.__str__()
            # 自定义错误提示
            return BaseView.error(msg=error_message)
        except ValidationError as e:
            error_message = '错误'+e.__str__()
            # 自定义错误提示
            return BaseView.error(msg=error_message)


        return BaseView.success()

    def delInfo(self, request):
        research_room_id = request.POST.get('id')
        if models.Office.objects.filter(research_room_id=research_room_id).exists():

            return BaseView.warn('存在关联内容无法删除')
        else:
            models.RearchRooms.objects.filter(id=research_room_id).delete()
            return BaseView.success()

'''
科研项目管理
'''
class ProjectsView(BaseView):

    def get(self, request, module, *args, **kwargs):

        if module == 'show':
            researchers = models.Researcher.objects.all().values()
            return render(request, 'projects.html',{
                                                'researchers': list(researchers)})
        elif module == 'info':
            return self.getInfo(request)
        elif module == 'page':
            return self.getPageInfo(request)
        else:
            return self.error()

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return self.addInfo(request)
        elif module == 'upd':
            return self.updInfo(request)
        elif module == 'del':
            return self.delInfo(request)
        else:
            return self.error()

    def getInfo(self, request):

        item = models.Project.objects.filter(project_id=request.GET.get('id')).first()
        project_leader_id = "" if not BaseView.isExit(item.project_leader) else item.project_leader.researcher_id,
        resl = {
            'project_id': item.project_id,
            "projectCode" :item.projectCode,
            'projectName': item.project_name,
            'researchContent': item.research_content,
            'project_leader_id': project_leader_id,
            'totalBudget': item.total_funding,
            'startDate': item.start_date,
            'endDate': item.completion_date,
        }

        return BaseView.successData(resl)

    def getPageInfo(self, request):

        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        name = request.GET.get('name',"").strip()

        qruery = Q()

        if BaseView.isExit(name):
            qruery = qruery & Q(project_name__contains=name)

        data = models.Project.objects.filter(qruery)
        paginator = Paginator(data, pageSize)

        resl = []
        for item in list(paginator.page(pageIndex)):
            project_leader_name = "-" if not BaseView.isExit(item.project_leader) else item.project_leader.name
            temp = {
                'project_id': item.project_id,
                'projectCode': item.projectCode,
                'projectName': item.project_name,
                'researchContent': item.research_content,
                'project_leader_name': project_leader_name,
                'totalBudget': item.total_funding,
                'startDate': item.start_date,
                'endDate': item.completion_date,
            }
            resl.append(temp)

        pageData = BaseView.parasePage(pageIndex, pageSize,
                                   paginator.page(pageIndex).paginator.num_pages,
                                   paginator.count, resl)

        return BaseView.successData(pageData)

    def addInfo(self, request):
        # project_leader_id
        project_leader =  models.Researcher.objects.get(researcher_id=request.POST.get('project_leader_id')) \
            if BaseView.isExit(request.POST.get('project_leader_id')) else None
        # project_leader = None if not BaseView.isExit(project_leader)
        try:
            models.Project.objects.create(
                projectCode = request.POST.get('projectCode'),
                project_name =request.POST.get('projectName'),
                research_content = request.POST.get('researchContent'),
                project_leader =project_leader,
                total_funding =request.POST.get('totalBudget'),
                start_date = request.POST.get('startDate'),
                completion_date = request.POST.get('endDate'),
                                          )
        except IntegrityError as e:
            error_message = '错误'+e.__str__()
            # 自定义错误提示
            return BaseView.error(msg=error_message)
        except ValidationError as e:
            error_message = '错误'+e.__str__()
            # 自定义错误提示
            return BaseView.error(msg=error_message)

        return BaseView.success()

    def updInfo(self, request):
        project_leader =  models.Researcher.objects.get(researcher_id=request.POST.get('project_leader_id'))
        try:
            models.Project.objects.filter(project_id=request.POST.get('project_id')) \
                .update(
                projectCode=request.POST.get('projectCode'),
                project_name=request.POST.get('projectName'),
                project_leader=project_leader,
                research_content=request.POST.get('researchContent'),
                total_funding=request.POST.get('totalBudget'),
                start_date=request.POST.get('startDate'),
                completion_date=request.POST.get('endDate')
            )
        except IntegrityError as e:
            error_message = '错误'+e.__str__()
            # 自定义错误提示
            return BaseView.error(msg=error_message)
        except ValidationError as e:
            error_message = '错误'+e.__str__()
            # 自定义错误提示
            return BaseView.error(msg=error_message)
        return BaseView.success()

    def delInfo(self, request):

        # if models.Project.objects.filter(project_id=request.POST.get('id')).exists():
        #
        #     return BaseView.warn('存在关联内容无法删除')
        # else:
        models.Project.objects.filter(project_id=request.POST.get('id')).delete()
        return BaseView.success()


'''
科研项目参与人员管理
'''
class ProjectResearcherView(BaseView):

    def get(self, request, module, *args, **kwargs):

        if module == 'show':
            projects = models.Project.objects.all().values()
            researchers = models.Researcher.objects.all().values()
            return render(request, 'projects_participators.html',{'projects': list(projects),
                                                                  'researchers': list(researchers)})
        elif module == 'info':
            return self.getInfo(request)
        elif module == 'page':
            return self.getPageInfo(request)
        else:
            return self.error()

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return self.addInfo(request)
        elif module == 'upd':
            return self.updInfo(request)
        elif module == 'del':
            return self.delInfo(request)
        else:
            return self.error()

    def getInfo(self, request):

        item = query_one_dict("SELECT * FROM app_projectresearcher WHERE id="+request.GET.get('id'))

        resl = {
            'id':item['id'],
            'project_id': item['project_id'],
            "researcher_id" :item['researcher_id'],
            'subproject_id': item['subproject_id'],
            'join_date': item['join_date'],
            'workload': item['workload'],
            'discretionary_funds': item['discretionary_funds'],
        }

        return BaseView.successData(resl)

    def getPageInfo(self, request):

        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        s_project_id = request.GET.get('project_id','').strip()

        qruery = Q()

        if BaseView.isExit(s_project_id):
            qruery = qruery & Q(project__project_id=s_project_id)

        data = models.ProjectResearcher.objects.filter(qruery)
        paginator = Paginator(data, pageSize)

        resl = []

        for item in list(paginator.page(pageIndex)):
            temp = {
                'id': item.id,
                'project_name': item.project.project_name,
                'researcher_name': item.researcher.name,
                'subproject_id': item.subproject.subproject_id,
                'join_date': BaseView.check_exist(item.join_date),
                'workload': BaseView.check_exist(item.workload),
                'discretionary_funds': BaseView.check_exist(item.discretionary_funds),
            }
            resl.append(temp)

        pageData = BaseView.parasePage(pageIndex, pageSize,
                                   paginator.page(pageIndex).paginator.num_pages,
                                   paginator.count, resl)

        return BaseView.successData(pageData)

    def addInfo(self, request):
        try:
            models.Project.objects.create(
                projectCode = request.POST.get('projectCode'),
                project_name =request.POST.get('projectName'),
                research_content = request.POST.get('researchContent'),
                total_funding =request.POST.get('totalBudget'),
                start_date = request.POST.get('startDate'),
                completion_date = request.POST.get('endDate'),
                                          )
        except IntegrityError as e:
            error_message = '错误'+e.__str__()
            # 自定义错误提示
            return BaseView.error(msg=error_message)
        except ValidationError as e:
            error_message = '错误'+e.__str__()
            # 自定义错误提示
            return BaseView.error(msg=error_message)
        return BaseView.success()

    def updInfo(self, request):
        try:
            models.ProjectResearcher.objects.filter(id=request.POST.get('id')) \
                .update(
                project=models.Project.objects.get(project_id=request.POST.get('project_id')),
                researcher=models.Researcher.objects.get(researcher_id=request.POST.get('researcher_id')),
                subproject=models.Subproject.objects.get(subproject_id=request.POST.get('subproject_id')),
                join_date=request.POST.get('join_date'),
                workload=request.POST.get('workload'),
                discretionary_funds=request.POST.get('discretionary_funds')
            )
        except IntegrityError as e:
            error_message = '错误'+e.__str__()
            # 自定义错误提示
            return BaseView.error(msg=error_message)
        except ValidationError as e:
            error_message = '错误'+e.__str__()
            # 自定义错误提示
            return BaseView.error(msg=error_message)
        return BaseView.success()

    def delInfo(self, request):

        # if models.Project.objects.filter(project_id=request.POST.get('id')).exists():
        #
        #     return BaseView.warn('存在关联内容无法删除')
        # else:
        models.Project.objects.filter(project_id=request.POST.get('id')).delete()
        return BaseView.success()


'''
办公场地信息管理
'''
class OfficesView(BaseView):

    def get(self, request, module, *args, **kwargs):

        if module == 'show':
            researchRooms = models.RearchRooms.objects.all().values()
            return  render(request, 'offices.html',{'researchRooms': list(researchRooms)})
        elif module == 'info':
            return self.getInfo(request)
        elif module == 'page':
            return self.getPageInfo(request)
        else:
            return self.error()

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return self.addInfo(request)
        elif module == 'upd':
            return self.updInfo(request)
        elif module == 'del':
            return self.delInfo(request)
        else:
            return self.error()

    def getInfo(self, request):

        item = models.Office.objects.filter(id=request.GET.get('id')).first()
        research_room_name = "" if item.research_room == None else item.research_room.name
        research_room_id = "" if item.research_room == None else item.research_room.id
        office_area = "" if item.office_area == None else item.office_area
        resl = {
            'id': item.id,
            'office_area': office_area,
            'address': item.address,
            'research_room_name': research_room_name,
            'researchRooms_Id': research_room_id
        }

        return BaseView.successData(resl)

    def getPageInfo(self, request):

        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        s_address = request.GET.get('s_address','').strip()
        s_research_room_id = request.GET.get('s_research_room_id','').strip()
        qruery = Q()

        if BaseView.isExit(s_address):
            qruery = qruery & Q(address__contains=s_address)
        if BaseView.isExit(s_research_room_id):
            qruery = qruery & Q(research_room__id=s_research_room_id)

        data = models.Office.objects.filter(qruery).order_by('id')
        paginator = Paginator(data, pageSize)

        resl = []
        for item in list(paginator.page(pageIndex)):
            research_room_name = "-" if item.research_room ==None else item.research_room.name
            office_area = "-" if item.office_area ==None else item.office_area
            # research_room.id = "" if item.research_room ==None else item.research_room.name
            temp = {
                'id': item.id,
                'office_area':office_area ,
                'address': item.address,
                'research_room_name': research_room_name,
                # 'researchRooms_Id':item.research_room.id
            }
            resl.append(temp)

        pageData = BaseView.parasePage(pageIndex, pageSize,
                                   paginator.page(pageIndex).paginator.num_pages,
                                   paginator.count, resl)

        return BaseView.successData(pageData)

    def addInfo(self, request):
        research_room = models.RearchRooms.objects.get(id=request.POST.get('researchRooms_Id')) \
                        if request.POST.get('researchRooms_Id')!="" else None
        office_area = request.POST.get('office_area')
        office_area = None if office_area == "" else office_area
        try:
            models.Office.objects.create(
                address=request.POST.get('address'),
                office_area = office_area,
                research_room =research_room
                                            )
        except IntegrityError as e:
            error_message = '错误'+e.__str__()
            # 自定义错误提示
            return BaseView.error(msg=error_message)
        except ValidationError as e:
            error_message = '错误'+e.__str__()
            # 自定义错误提示
            return BaseView.error(msg=error_message)
        return BaseView.success()

    def updInfo(self, request):
        try:
            office_area = request.POST.get('office_area')
            office_area = None if office_area =="" else office_area
            research_room = models.RearchRooms.objects.get(id=request.POST.get('researchRooms_Id')) \
                            if request.POST.get('researchRooms_Id')!="" else None
            models.Office.objects.filter(id=request.POST.get('id')) \
                .update(
                address=request.POST.get('address'),
                office_area = office_area,
                research_room = research_room
            )
        except IntegrityError as e:
            error_message = '错误' + e.__str__()
            # 自定义错误提示
            return BaseView.error(msg=error_message)
        except ValidationError as e:
            error_message = '错误' + e.__str__()
            # 自定义错误提示
            return BaseView.error(msg=error_message)
        return BaseView.success()

    def delInfo(self, request):

        # if models.Jobs.objects.filter(company__id=request.POST.get('id')).exists():
        #
        #     return BaseView.warn('存在关联内容无法删除')
        # else:
        models.Office.objects.filter(id=request.POST.get('id')).delete()
        return BaseView.success()



'''
子课题信息管理
'''
class SubprojectsView(BaseView):

    def get(self, request, module, *args, **kwargs):

        if module == 'show':
            projects = models.Project.objects.all().values()
            return  render(request, 'subprojects.html',{'projects': list(projects)})
        elif module == 'info':
            return self.getInfo(request)
        elif module == 'page':
            return self.getPageInfo(request)
        else:
            return self.error()

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return self.addInfo(request)
        elif module == 'upd':
            return self.updInfo(request)
        elif module == 'del':
            return self.delInfo(request)
        else:
            return self.error()

    def getInfo(self, request):

        item = models.Subproject.objects.filter(subproject_id=request.GET.get('id')).first()
        project_name = item.project.project_name if item.project is not None else ""
        project_id = item.project.project_id if item.project is not None else ""
        # 将日期转换为字符串，使用特定的格式
        completion_time_str = item.completion_time.strftime("%Y-%m-%d")
        resl = {
            'id': item.subproject_id,
            'project_name': project_name,
            "project_Id":project_id,
            'completion_time': item.completion_time,
            'discretionary_funds': item.discretionary_funds,
            'tech_specification': item.tech_specification
        }

        return BaseView.successData(resl)

    def getPageInfo(self, request):

        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        name = request.GET.get('name')

        qruery = Q()

        if BaseView.isExit(name):
            qruery = qruery & Q(project__project_id=name)

        data = models.Subproject.objects.filter(qruery)
        paginator = Paginator(data, pageSize)

        resl = []
        for item in list(paginator.page(pageIndex)):
            project_name= item.project.project_name if item.project is not None else ""
            leader_name = item.leader.name if item.leader is not None else ""
            temp = {
                'id': item.subproject_id,
                'project_name': project_name,
                'leader_name': leader_name,
                'completion_time': BaseView.check_exist(item.completion_time),
                'discretionary_funds':BaseView.check_exist(item.discretionary_funds),
                'tech_specification':BaseView.check_exist(item.tech_specification)
            }
            resl.append(temp)

        pageData = BaseView.parasePage(pageIndex, pageSize,
                                   paginator.page(pageIndex).paginator.num_pages,
                                   paginator.count, resl)

        return BaseView.successData(pageData)

    def addInfo(self, request):
        try:
            models.Subproject.objects.create(
                tech_specification=request.POST.get('tech_specification'),
                completion_time=request.POST.get('completion_time'),
                discretionary_funds = request.POST.get('discretionary_funds'),
                project = models.Project.objects.get(project_id=request.POST.get('project_Id'))
                                            )
        except IntegrityError as e:
            error_message = '错误'+e.__str__()
            # 自定义错误提示
            return BaseView.error(msg=error_message)
        except ValidationError as e:
            error_message = '错误'+e.__str__()
            # 自定义错误提示
            return BaseView.error(msg=error_message)
        return BaseView.success()

    def updInfo(self, request):
        try:
            models.Subproject.objects.filter(subproject_id=request.POST.get('id')) \
                .update(
                tech_specification=request.POST.get('tech_specification'),
                completion_time=request.POST.get('completion_time'),
                discretionary_funds = request.POST.get('discretionary_funds'),
                project = models.Project.objects.get(project_id=request.POST.get('project_Id'))
            )
        except IntegrityError as e:
            error_message = '错误'+e.__str__()
            # 自定义错误提示
            return BaseView.error(msg=error_message)
        except ValidationError as e:
            error_message = '错误'+e.__str__()
            # 自定义错误提示
            return BaseView.error(msg=error_message)
        return BaseView.success()

    def delInfo(self, request):

        # if models.Jobs.objects.filter(company__id=request.POST.get('id')).exists():
        #
        #     return BaseView.warn('存在关联内容无法删除')
        # else:
        models.Subproject.objects.filter(subproject_id=request.POST.get('id')).delete()
        return BaseView.success()

'''
单位信息管理
'''
class OrganizationsView(BaseView):

    def get(self, request, module, *args, **kwargs):

        if module == 'show':
            contacts = models.Contact.objects.all().values()
            # organizations = models.Organization.objects.all().values()
            return  render(request, 'organizations.html',{'contacts': list(contacts)})
        elif module == 'info':
            return self.getInfo(request)
        elif module == 'page':
            return self.getPageInfo(request)
        else:
            return self.error()

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return self.addInfo(request)
        elif module == 'upd':
            return self.updInfo(request)
        elif module == 'del':
            return self.delInfo(request)
        else:
            return self.error()

    def getInfo(self, request):

        item = models.Organization.objects.filter(organization_id=request.GET.get('id')).first()
        leader_id = item.leader.contact_id if item.leader is not None else ""
        resl = {
            'id': item.organization_id,
            'organization_name': item.organization_name,
            'address': item.address,
            'leader_Id':leader_id
        }

        return BaseView.successData(resl)

    def getPageInfo(self, request):

        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        name = request.GET.get('name',"").strip()

        qruery = Q()

        if BaseView.isExit(name):
            qruery = qruery & Q(organization_name__contains=name)
        with transaction.atomic():
            try:
                contacts_data = query_all_dict("""
                SELECT organization.organization_id , GROUP_CONCAT(name SEPARATOR ',') AS concatenated_contacts
                FROM organization 
                LEFT JOIN organization_contacts on organization.organization_id = organization_contacts.organization_id
                NATURAL JOIN contact
                GROUP BY organization.organization_id
                """
                        )
                data = models.Organization.objects.filter(qruery)
            except Exception as e:
                # 发生异常时回滚事务
                transaction.rollback()
                raise e
        paginator = Paginator(data, pageSize)
        resl = []
        for item in list(paginator.page(pageIndex)):
            leader_name= item.leader.name if item.leader is not None else ""
            #找到多个合适的联系人
            contacts = [d['concatenated_contacts'] for d in contacts_data if d['organization_id'] == item.organization_id]
            contacts = contacts if len(contacts)!=0 else "-"
            temp = {
                'id': item.organization_id,
                'organization_name': item.organization_name,
                'address': item.address,
                'contacts':contacts[0],
                'leader_name':leader_name
            }
            resl.append(temp)

        pageData = BaseView.parasePage(pageIndex, pageSize,
                                   paginator.page(pageIndex).paginator.num_pages,
                                   paginator.count, resl)

        return BaseView.successData(pageData)

    def addInfo(self, request):
        leader = models.Contact.objects.get(contact_id = request.POST.get('leader_Id'))\
                    if BaseView.isExit(request.POST.get('leader_Id')) else None
        if not BaseView.isExit(request.POST.get('organization_name')):
            return BaseView.error(msg="单位名称不能为空")
        try:
            models.Organization.objects.create(
                organization_name=request.POST.get('organization_name'),
                address=request.POST.get('address'),
                leader = leader
                                            )
        except IntegrityError as e:
            error_message = '错误'+e.__str__()
            # 自定义错误提示
            return BaseView.error(msg=error_message)
        except ValidationError as e:
            error_message = '错误'+e.__str__()
            # 自定义错误提示
            return BaseView.error(msg=error_message)
        return BaseView.success()

    def updInfo(self, request):
        try:
            models.Organization.objects.filter(organization_id=request.POST.get('id')) \
                .update(
                organization_name=request.POST.get('organization_name'),
                address=request.POST.get('address'),
                leader = models.Contact.objects.get(contact_id=request.POST.get('leader_Id'))
            )
        except IntegrityError as e:
            error_message = '错误'+e.__str__()
            # 自定义错误提示
            return BaseView.error(msg=error_message)
        except ValidationError as e:
            error_message = '错误'+e.__str__()
            # 自定义错误提示
            return BaseView.error(msg=error_message)
        return BaseView.success()

    def delInfo(self, request):

        # if models.Jobs.objects.filter(company__id=request.POST.get('id')).exists():
        #
        #     return BaseView.warn('存在关联内容无法删除')
        # else:
        models.Organization.objects.filter(organization_id=request.POST.get('id')).delete()
        return BaseView.success()


'''
单位联系人信息管理
'''
class Organization_contactsView(BaseView):

    def get(self, request, module, *args, **kwargs):

        if module == 'show':
            contacts = models.Contact.objects.all().values()
            organizations = models.Organization.objects.all().values()
            return  render(request, 'organization_contacts.html',{'contacts': list(contacts),'organizations':organizations})
        elif module == 'info':
            return self.getInfo(request)
        elif module == 'page':
            return self.getPageInfo(request)
        else:
            return self.error()

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return self.addInfo(request)
        elif module == 'upd':
            return self.updInfo(request)
        elif module == 'del':
            return self.delInfo(request)
        else:
            return self.error()

    def getInfo(self, request):
        item = query_all_dict("""
        SELECT organization_contacts.id,organization_contacts.organization_id,organization_contacts.contact_id
        FROM organization_contacts
        WHERE organization_contacts.id = 
        """+request.GET.get('id'))
        resl = {
            'id': item[0]['id'],
            'organization_Id': item[0]['organization_id'],
            'contact_Id': item[0]['contact_id']
        }
        return BaseView.successData(resl)

    def getPageInfo(self, request):

        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        name = request.GET.get('name',"")
        sql = """
        SELECT organization_contacts.id,organization.organization_id, organization_name,name
        FROM organization 
        NATURAL JOIN organization_contacts 
        NATURAL JOIN contact
        """
        if BaseView.isExit(name):
            sql+=" WHERE organization.organization_id ="+name
        data = query_all_dict(sql)
        # if BaseView.isExit(name):
        #     qruery = qruery & Q(name__contains=name)
        paginator = Paginator(data, pageSize)
        resl = []
        for item in list(paginator.page(pageIndex)):
            temp = {
                'id': item['id'],
                'organization_name': item['organization_name'],
                'contact_name':item['name']
            }
            resl.append(temp)
        pageData = BaseView.parasePage(pageIndex, pageSize,
                                   paginator.page(pageIndex).paginator.num_pages,
                                   paginator.count, resl)

        return BaseView.successData(pageData)

    def addInfo(self, request):
        try:
            models.Organization.objects.create(
                organization_name=request.POST.get('organization_name'),
                address=request.POST.get('address'),
                leader = models.Contact.objects.get(contact_id = request.POST.get('leader_Id'))
                                            )
        except IntegrityError as e:
            error_message = '错误'+e.__str__()
            # 自定义错误提示
            return BaseView.error(msg=error_message)
        except ValidationError as e:
            error_message = '错误'+e.__str__()
            # 自定义错误提示
            return BaseView.error(msg=error_message)
        return BaseView.success()

    def updInfo(self, request):
        id = request.POST.get('id')
        organization_id = request.POST.get('organization_Id')
        contact_id = request.POST.get('contact_Id')
        with transaction.atomic():
            try:
                # 获取数据库游标
                with connection.cursor() as cursor:
                    cursor.execute("SELECT id FROM organization_contacts WHERE organization_id = %s AND contact_id = %s",
                                   [organization_id, contact_id])
                    existing_id = cursor.fetchone()

                    # 执行更新操作
                    if existing_id and existing_id[0] != id:
                    # 存在重复记录，执行相应的处理
                    # ...
                        return BaseView.error("存在重复")
                    else:
                    # 不存在重复记录，执行更新操作
                    # 执行原生的 MySQL 更新语句
                        cursor.execute("UPDATE organization_contacts SET organization_id = %s, contact_id = %s WHERE id = %s",
                                   [organization_id, contact_id, id])
            except Exception as e:
                # 发生异常时回滚事务
                transaction.rollback()
            except IntegrityError as e:
                error_message = '错误' + e.__str__()
                # 自定义错误提示
                return BaseView.error(msg=error_message)
            except ValidationError as e:
                error_message = '错误' + e.__str__()
                # 自定义错误提示
                return BaseView.error(msg=error_message)
        return BaseView.success()

    def delInfo(self, request):

        # if models.Jobs.objects.filter(company__id=request.POST.get('id')).exists():
        #
        #     return BaseView.warn('存在关联内容无法删除')
        # else:
        # 获取数据库游标
        with connection.cursor() as cursor:
            # 执行原生的 MySQL 删除语句
            cursor.execute("DELETE FROM organization_contacts WHERE id = %s", [request.POST.get('id')])
        return BaseView.success()

'''
联系人信息管理
'''
class ContactsView(BaseView):

    def get(self, request, module, *args, **kwargs):

        if module == 'show':
            projects = models.Project.objects.all().values()
            return  render(request, 'contacts.html',{'projects': list(projects)})
        elif module == 'info':
            return self.getInfo(request)
        elif module == 'page':
            return self.getPageInfo(request)
        else:
            return self.error()

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return self.addInfo(request)
        elif module == 'upd':
            return self.updInfo(request)
        elif module == 'del':
            return self.delInfo(request)
        else:
            return self.error()

    def getInfo(self, request):

        item = models.Contact.objects.filter(contact_id=request.GET.get('id')).first()

        resl = {
            'id': item.contact_id,
            'name': item.name,
            'office_phone': item.office_phone,
            'mobile_phone': item.mobile_phone,
            'email': item.email
        }

        return BaseView.successData(resl)

    def getPageInfo(self, request):

        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        # name = request.GET.get('name')

        qruery = Q()

        # if BaseView.isExit(name):
        #     qruery = qruery & Q(name__contains=name)

        data = models.Contact.objects.filter(qruery)
        paginator = Paginator(data, pageSize)

        resl = []
        for item in list(paginator.page(pageIndex)):
            # project_name= item.project.project_name if item.project is not None else ""
            temp = {
                'id': item.contact_id,
                'name': item.name,
                'office_phone': item.office_phone,
                'mobile_phone': item.mobile_phone,
                'email': item.email
            }
            resl.append(temp)

        pageData = BaseView.parasePage(pageIndex, pageSize,
                                   paginator.page(pageIndex).paginator.num_pages,
                                   paginator.count, resl)

        return BaseView.successData(pageData)

    def addInfo(self, request):
        try:
            models.Contact.objects.create(
                name=request.POST.get('name'),
                office_phone=request.POST.get('office_phone'),
                mobile_phone=request.POST.get('mobile_phone'),
                email=request.POST.get('email')
                                            )
        except IntegrityError as e:
            error_message = '错误'+e.__str__()
            # 自定义错误提示
            return BaseView.error(msg=error_message)
        except ValidationError as e:
            error_message = '错误'+e.__str__()
            # 自定义错误提示
            return BaseView.error(msg=error_message)
        return BaseView.success()

    def updInfo(self, request):
        try:
            models.Contact.objects.filter(contact_id=request.POST.get('id')) \
                .update(
                name=request.POST.get('name'),
                office_phone=request.POST.get('office_phone'),
                mobile_phone=request.POST.get('mobile_phone'),
                email=request.POST.get('email')
            )
        except IntegrityError as e:
            error_message = '错误'+e.__str__()
            # 自定义错误提示
            return BaseView.error(msg=error_message)
        except ValidationError as e:
            error_message = '错误'+e.__str__()
            # 自定义错误提示
            return BaseView.error(msg=error_message)
        return BaseView.success()

    def delInfo(self, request):

        # if models.Jobs.objects.filter(company__id=request.POST.get('id')).exists():
        #
        #     return BaseView.warn('存在关联内容无法删除')
        # else:
        models.Contact.objects.filter(contact_id=request.POST.get('id')).delete()
        return BaseView.success()


'''
联系人信息管理
'''
class ContactsView(BaseView):

    def get(self, request, module, *args, **kwargs):

        if module == 'show':
            projects = models.Project.objects.all().values()
            return  render(request, 'contacts.html',{'projects': list(projects)})
        elif module == 'info':
            return self.getInfo(request)
        elif module == 'page':
            return self.getPageInfo(request)
        else:
            return self.error()

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return self.addInfo(request)
        elif module == 'upd':
            return self.updInfo(request)
        elif module == 'del':
            return self.delInfo(request)
        else:
            return self.error()

    def getInfo(self, request):

        item = models.Contact.objects.filter(contact_id=request.GET.get('id')).first()

        resl = {
            'id': item.contact_id,
            'name': item.name,
            'office_phone': item.office_phone,
            'mobile_phone': item.mobile_phone,
            'email': item.email
        }

        return BaseView.successData(resl)

    def getPageInfo(self, request):

        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        name = request.GET.get('name',"").strip()

        qruery = Q()

        if BaseView.isExit(name):
            qruery = qruery & Q(name__contains=name)

        data = models.Contact.objects.filter(qruery)
        paginator = Paginator(data, pageSize)

        resl = []
        for item in list(paginator.page(pageIndex)):
            # project_name= item.project.project_name if item.project is not None else ""
            temp = {
                'id': item.contact_id,
                'name': item.name,
                'office_phone': item.office_phone,
                'mobile_phone': item.mobile_phone,
                'email': item.email
            }
            resl.append(temp)

        pageData = BaseView.parasePage(pageIndex, pageSize,
                                   paginator.page(pageIndex).paginator.num_pages,
                                   paginator.count, resl)

        return BaseView.successData(pageData)

    def addInfo(self, request):

        models.Contact.objects.create(
            name=request.POST.get('name'),
            office_phone=request.POST.get('office_phone'),
            mobile_phone=request.POST.get('mobile_phone'),
            email=request.POST.get('email')
                                        )
        return BaseView.success()

    def updInfo(self, request):
        models.Contact.objects.filter(contact_id=request.POST.get('id')) \
            .update(
            name=request.POST.get('name'),
            office_phone=request.POST.get('office_phone'),
            mobile_phone=request.POST.get('mobile_phone'),
            email=request.POST.get('email')
        )
        return BaseView.success()

    def delInfo(self, request):

        # if models.Jobs.objects.filter(company__id=request.POST.get('id')).exists():
        #
        #     return BaseView.warn('存在关联内容无法删除')
        # else:
        models.Contact.objects.filter(contact_id=request.POST.get('id')).delete()
        return BaseView.success()

'''
秘书信息管理
'''
class SecretariesView(BaseView):

    def get(self, request, module, *args, **kwargs):

        if module == 'show':
            return render(request, 'secretaries.html')
        elif module == 'info':
            return self.getInfo(request)
        elif module == 'page':
            return self.getPageInfo(request)
        else:
            return self.error()

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return self.addInfo(request)
        elif module == 'upd':
            return self.updInfo(request)
        elif module == 'del':
            return self.delInfo(request)
        else:
            return self.error()

    def getInfo(self, request):

        data = models.Secretary.objects.filter(secretary_id=request.GET.get('id')).first()

        resl = {
            'secretary_id': data.secretary_id,
            'employee_id': data.employee_id,
            'name': data.name,
            'gender': data.gender,
            'age': data.age,
            'hire_date': data.hire_date,
            'responsibilities': data.responsibilities,
        }

        return BaseView.successData(resl)

    def getPageInfo(self, request):

        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        name = request.GET.get('name','').strip()

        qruery = Q()

        if BaseView.isExit(name):
            qruery = qruery & Q(name__contains=name)

        data = models.Secretary.objects.filter(qruery)
        paginator = Paginator(data, pageSize)

        resl = []

        for item in list(paginator.page(pageIndex)):
            age = "-" if item.age==None else item.age
            gender = "-" if item.gender =="" else item.gender
            hire_date = "-" if item.hire_date == None else item.hire_date
            responsibilities = "-" if item.responsibilities == "" else item.responsibilities
            temp = {
                'secretary_id': item.secretary_id,
                'employee_id': item.employee_id,
                'name': item.name,
                'gender': gender,
                'age': age,
                'hire_date': hire_date,
                'responsibilities': responsibilities,
            }
            resl.append(temp)

        pageData = BaseView.parasePage(pageIndex, pageSize,
                                       paginator.page(pageIndex).paginator.num_pages,
                                       paginator.count, resl)

        return BaseView.successData(pageData)

    def addInfo(self, request):
        age = request.POST.get('age') if request.POST.get('age')!="" else None
        hire_date = request.POST.get('hire_date') if request.POST.get('age') != "" else None
        models.Secretary.objects.create(
            employee_id=request.POST.get('employee_id'),
            name=request.POST.get('name'),
            gender=request.POST.get('gender'),
            age=age,
            hire_date=hire_date,
            responsibilities=request.POST.get('responsibilities')
                                    )
        return BaseView.success()

    def updInfo(self, request):
        models.Secretary.objects.filter(secretary_id=request.POST.get('secretary_id')) \
            .update(
            employee_id=request.POST.get('employee_id'),
            name=request.POST.get('name'),
            gender=request.POST.get('gender'),
            age=request.POST.get('age'),
            hire_date=request.POST.get('hire_date'),
            responsibilities=request.POST.get('responsibilities')
        )
        return BaseView.success()

    def delInfo(self, request):

        # if models.SendLogs.objects.filter(job__id=request.POST.get('id')).exists():
        #
        #     return BaseView.warn('存在关联内容无法删除')
        # else:
        models.Secretary.objects.filter(secretary_id=request.POST.get('id')).delete()
        return BaseView.success()

'''
用户信息管理
'''
class UsersView(BaseView):

    def get(self, request, module, *args, **kwargs):

        if module == 'show':
            return render(request, 'users.html')
        elif module == 'info':
            return self.getInfo(request)
        elif module == 'page':
            return self.getPageInfo(request)
        else:
            return self.error()

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return self.addInfo(request)
        elif module == 'upd':
            return self.updInfo(request)
        elif module == 'del':
            return self.delInfo(request)
        else:
            return self.error()

    def getInfo(self, request):

        data = models.Users.objects.filter(id=request.GET.get('id')).first()

        resl = {
            'id': data.id,
            'userName': data.userName,
            'passWord': data.passWord,
            'name': data.name,
            'gender': data.gender,
            'age': data.age,
            'phone': data.phone,
            'type': data.type
        }

        return BaseView.successData(resl)

    def getPageInfo(self, request):

        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        userName = request.GET.get('userName')
        name = request.GET.get('name')
        phone = request.GET.get('phone')

        qruery = Q(type = 1);

        if BaseView.isExit(userName):
            qruery = qruery & Q(userName__contains=userName)

        if BaseView.isExit(name):
            qruery = qruery & Q(name__contains=name)

        if BaseView.isExit(phone):
            qruery = qruery & Q(phone__contains=phone)

        data = models.Users.objects.filter(qruery)
        paginator = Paginator(data, pageSize)

        resl = []

        for item in list(paginator.page(pageIndex)):
            temp = {
                'id': item.id,
                'userName': item.userName,
                'passWord': item.passWord,
                'name': item.name,
                'gender': item.gender,
                'age': item.age,
                'phone': item.phone,
                'type': item.type
            }
            resl.append(temp)

        pageData = BaseView.parasePage(pageIndex, pageSize,
                                   paginator.page(pageIndex).paginator.num_pages,
                                   paginator.count, resl)

        return BaseView.successData(pageData)

    def addInfo(self, request):

        models.Users.objects.create(
                                    userName=request.POST.get('userName'),
                                    passWord=request.POST.get('passWord'),
                                    name=request.POST.get('name'),
                                    gender=request.POST.get('gender'),
                                    age=request.POST.get('age'),
                                    phone=request.POST.get('phone'),
                                    type=request.POST.get('type'),
                                    )
        return BaseView.success()

    def updInfo(self, request):

        models.Users.objects.filter(id=request.POST.get('id')) \
            .update(
            userName=request.POST.get('userName'),
            passWord=request.POST.get('passWord'),
            name=request.POST.get('name'),
            gender=request.POST.get('gender'),
            age=request.POST.get('age'),
            phone=request.POST.get('phone'),
        )
        return BaseView.success()

    def delInfo(self, request):

        models.Users.objects.filter(id=request.POST.get('id')).delete()
        return BaseView.success()

'''
科研人员信息管理
'''
class ResearchersView(BaseView):

    def get(self, request, module, *args, **kwargs):

        if module == 'show':
            RearchRooms = models.RearchRooms.objects.all().values()
            return render(request, 'researchers.html', {"RearchRooms":RearchRooms})
        elif module == 'info':
            return self.getInfo(request)
        elif module == 'page':
            return self.getPageInfo(request)
        else:
            return self.error()

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return self.addInfo(request)
        elif module == 'upd':
            return self.updInfo(request)
        elif module == 'del':
            return self.delInfo(request)
        else:
            return self.error()

    def getInfo(self, request):

        item = models.Researcher.objects.filter(researcher_id=request.GET.get('id')).first()
        research_roomName = item.research_room.name if item.research_room is not None else ""
        research_roomId = item.research_room.id if item.research_room is not None else -1
        resl = {
            'researcher_id': item.researcher_id,
            "employee_id": item.employee_id,
            'name': item.name,
            'gender': item.gender,
            'title': item.title,
            'age': item.age,
            'research_area': item.research_area,
            'research_roomName': research_roomName,
            "researchRoomId":research_roomId
        }

        return BaseView.successData(resl)

    def getPageInfo(self, request):

        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        employee_id = request.GET.get('employee_id','').strip()
        name = request.GET.get('name','').strip()
        research_room_id = request.GET.get('research_room_id','').strip()

        qruery = Q()

        if BaseView.isExit(employee_id):
            qruery = qruery & Q(employee_id=employee_id)

        if BaseView.isExit(name):
            qruery = qruery & Q(name__contains=name)

        if BaseView.isExit(research_room_id):
            qruery = qruery & Q(research_room_id=research_room_id)


        data = models.Researcher.objects.filter(qruery)
        paginator = Paginator(data, pageSize)
        resl = []

        for item in list(paginator.page(pageIndex)):
            research_roomName = item.research_room.name if item.research_room is not None else ""
            temp = {
                'researcher_id': item.researcher_id,
                "employee_id":item.employee_id,
                'name': item.name,
                'gender': item.gender,
                'title': item.title,
                'age': item.age,
                'research_area': item.research_area,
                'research_roomName': research_roomName
            }
            resl.append(temp)

        pageData = BaseView.parasePage(pageIndex, pageSize,
                                   paginator.page(pageIndex).paginator.num_pages,
                                   paginator.count, resl)

        return BaseView.successData(pageData)

    def addInfo(self, request):

        researchRoomId = request.POST.get('researchRoomId')  # 秘书id
        if researchRoomId != "-1":
            # 有所属研究室
            researchRoom = models.RearchRooms.objects.get(id=researchRoomId)
        else:
            # 没有所属研究室
            researchRoom = None

        try:
            models.Researcher.objects.create(
                employee_id=request.POST.get('employee_id'),
                name=request.POST.get('name'),
                gender=request.POST.get('gender'),
                title=request.POST.get('title'),
                age=request.POST.get('age'),
                research_area=request.POST.get('research_area'),
                research_room = researchRoom
            )

        except IntegrityError:
            error_message = '该研究人员已存在'  # 自定义错误提示
            return BaseView.error(msg=error_message)

        return BaseView.success()

    def updInfo(self, request):
        researchRoomId = request.POST.get('researchRoomId')  # 秘书id
        if researchRoomId != "-1":
            # 有所属研究室
            researchRoom = models.RearchRooms.objects.get(id=researchRoomId)
        else:
            # 没有所属研究室
            researchRoom = None

        models.Researcher.objects.filter(researcher_id=request.POST.get('researcher_id')) \
            .update(
            employee_id=request.POST.get('employee_id'),
            name=request.POST.get('name'),
            gender=request.POST.get('gender'),
            title=request.POST.get('title'),
            age=request.POST.get('age'),
            research_area=request.POST.get('research_area'),
            research_room=researchRoom
        )


        return BaseView.success()

    def delInfo(self, request):

        models.Researcher.objects.filter(researcher_id=request.POST.get('id')).delete()
        # print(request.GET.get('id'), student);

        # models.Users.objects.filter(id=student.user.id).delete()
        # models.EducationLogs.objects.filter(student__id=student.id).delete()
        # models.ProjectLogs.objects.filter(student__id=student.id).delete()
        # models.SendLogs.objects.filter(student__id=student.id).delete()

        # student.delete()

        return BaseView.success()

'''
主任信息管理
'''
class DirectorsView(BaseView):

    def get(self, request, module, *args, **kwargs):

        if module == 'show':
            return render(request, 'directors.html')
        elif module == 'info':
            return self.getInfo(request)
        elif module == 'page':
            return self.getPageInfo(request)
        else:
            return self.error()

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return self.addInfo(request)
        elif module == 'upd':
            return self.updInfo(request)
        elif module == 'del':
            return self.delInfo( request)
        else:
            return self.error()

    def getInfo(self, request):

        data = models.EducationLogs.objects.filter(id=request.GET.get('id')).first()

        resl = {
            'id': data.id,
            'name': data.name,
            'startTime': data.startTime,
            'endTime': data.endTime,
            'studentId': data.student.id,
        }
        return BaseView.successData(resl)

    def getPageInfo(self, request):

        # type = request.session.get('type')
        # user = request.session.get('user')

        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        # name = request.GET.get('name')
        # studentName = request.GET.get('studentName')

        qruery = Q()

        # if type == 2:
        #     student = models.Students.objects.filter(user__id=user).first()
        #     qruery = qruery & Q(student__id=student.id)

        # if BaseView.isExit(name):
        #     qruery = qruery & Q(name__contains=name)
        #
        # if BaseView.isExit(studentName):
        #     qruery = qruery & Q(student__user__name__contains=studentName)

        # if type == 2:
        #     data = models.EducationLogs.objects.filter(qruery).order_by("-startTime")
        #     paginator = Paginator(data, pageSize)
        # else:
        #     data = models.EducationLogs.objects.filter(qruery).order_by("student_id")
        #     paginator = Paginator(data, pageSize)

        data = models.Director.objects.filter(qruery)
        paginator = Paginator(data, pageSize)
        resl = []

        for item in list(paginator.page(pageIndex)):
            temp = {
                'director_id': item.director_id,
                'researcher_id': item.researcher_id,
                'lab_id': item.lab_id,
                'start_date': item.start_date,
                'tenure': item.tenure,
            }
            resl.append(temp)

        pageData = BaseView.parasePage(pageIndex, pageSize,
                                   paginator.page(pageIndex).paginator.num_pages,
                                   paginator.count, resl)

        return BaseView.successData(pageData)

    def addInfo(self, request):

        user = request.session.get('user')

        models.EducationLogs.objects.create(name=request.POST.get('name'),
                                    startTime=request.POST.get('startTime'),
                                    endTime=request.POST.get('endTime'),
                                    student=models.Students.objects.filter(user__id=user).first()
                                    )
        return BaseView.success()

    def     updInfo(self, request):

        models.EducationLogs.objects.filter(id=request.POST.get('id')) \
            .update(
            name=request.POST.get('name'),
            startTime=request.POST.get('startTime'),
            endTime=request.POST.get('endTime'),
        )
        return BaseView.success()

    def delInfo(self, request):

        models.EducationLogs.objects.filter(id=request.POST.get('id')).delete()
        return BaseView.success()

'''
项目经历管理
'''
class ProjectLogsView(BaseView):

    def get(self, request, module, *args, **kwargs):

        if module == 'show':
            return render(request, 'projectLogs.html')
        elif module == 'info':
            return self.getInfo(request)
        elif module == 'page':
            return self.getPageInfo(request)
        else:
            return self.error()

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return self.addInfo( request)
        elif module == 'upd':
            return self.updInfo(request)
        elif module == 'del':
            return self.delInfo(request)
        else:
            return self.error()

    def getInfo(self, request):

        data = models.ProjectLogs.objects.filter(id=request.GET.get('id')).first()

        resl = {
            'id': data.id,
            'name': data.name,
            'duty': data.duty,
            'detail': data.detail,
            'studentId': data.student.id,
        }

        return BaseView.successData(resl)

    def getPageInfo(self, request):

        type = request.session.get('type')
        user = request.session.get('user')

        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        name = request.GET.get('name')
        studentName = request.GET.get('studentName')

        qruery = Q();

        if type == 2:
            student = models.Students.objects.filter(user__id=user).first()
            qruery = qruery & Q(student__id=student.id)

        if BaseView.isExit(name):
            qruery = qruery & Q(name__contains=name)

        if BaseView.isExit(studentName):
            qruery = qruery & Q(student__user__name__contains=studentName)

        data = models.ProjectLogs.objects.filter(qruery)

        paginator = Paginator(data, pageSize)

        resl = []

        for item in list(paginator.page(pageIndex)):
            temp = {
                'id': item.id,
                'name': item.name,
                'duty': item.duty,
                'detail': item.detail,
                'studentId': item.student.id,
                'studentName': item.student.user.name,
            }
            resl.append(temp)

        pageData = BaseView.parasePage(pageIndex, pageSize,
                                   paginator.page(pageIndex).paginator.num_pages,
                                   paginator.count, resl)

        return BaseView.successData(pageData)

    def addInfo(self, request):

        user = request.session.get('user')

        models.ProjectLogs.objects.create(name=request.POST.get('name'),
                                        duty=request.POST.get('duty'),
                                        detail=request.POST.get('detail'),
                                        student=models.Students.objects.filter(user__id=user).first()
                                        )
        return BaseView.success()

    def updInfo(self, request):

        models.ProjectLogs.objects.filter(id=request.POST.get('id')) \
            .update(
            name=request.POST.get('name'),
            duty=request.POST.get('duty'),
            detail=request.POST.get('detail'),
        )
        return BaseView.success()

    def delInfo(self, request):

        models.ProjectLogs.objects.filter(id=request.POST.get('id')).delete()
        return BaseView.success()

'''
项目成果管理
'''
class AchievementsView(BaseView):

    def get(self, request, module, *args, **kwargs):

        if module == 'show':
            return render(request, 'achievements.html')
        elif module == 'info':
            return self.getInfo(request)
        elif module == 'page':
            return self.getPageInfo(request)
        else:
            return self.error()

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return self.addInfo(request)
        elif module == 'upd':
            return self.updInfo(request)
        elif module == 'del':
            return self.delInfo(request)
        else:
            return self.error()

    def getInfo(self, request):
        sql_query = "SELECT * FROM achievement WHERE achievement_id = "+request.GET.get('id')
        item = query_one_dict(sql_query)
        resl = {
            'id': item["achievement_id"],
            'achievement_name': item["achievement_name"],
            'achievement_date': item["achievement_date"],
            'ranking': item["ranking"],
        }

        return BaseView.successData(resl)

    def getPageInfo(self, request):
        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        achievement_name = request.GET.get('achievement_name')

        sql_query = "SELECT * FROM achievement"
        # 加入查询条件
        if BaseView.isExit(achievement_name):
            sql_query +=" WHERE achievement_name = "+"\""+achievement_name+"\""
        with transaction.atomic():
            data = models.Achievement.objects.raw(sql_query)
        paginator = Paginator(data, pageSize)
        resl = []
        for item in list(paginator.page(pageIndex)):
            temp = {
                'id': item.achievement_id,
                'achievement_name': BaseView.check_exist(item.achievement_name),
                'achievement_date': BaseView.check_exist(item.achievement_date),
                'ranking': BaseView.check_exist(item.ranking),
            }
            resl.append(temp)

        pageData = BaseView.parasePage(pageIndex, pageSize,
                                   paginator.page(pageIndex).paginator.num_pages,
                                   paginator.count, resl)

        return BaseView.successData(pageData)

    def addInfo(self, request):
        with connection.cursor() as cursor:
            sql = "INSERT INTO achievement (achievement_name,achievement_date,ranking) VALUES (%s,%s,%s)"
            params =[request.POST.get('achievement_name'),
                     request.POST.get('achievement_date'),
                     request.POST.get('ranking')]
            cursor.execute(sql, params)
        return BaseView.success()


    def updInfo(self, request):
        with connection.cursor() as cursor:
            sql = "UPDATE achievement " \
                  "SET achievement_name = %s, achievement_date = %s, ranking = %s" \
                  "WHERE achievement_id= %s"
            params = [request.POST.get('achievement_name'),
                      request.POST.get('achievement_date'),
                      request.POST.get('ranking'),
                      request.POST.get('id')
                      ]
            cursor.execute(sql, params)
        return BaseView.success()

    def delInfo(self, request):
        # models.Achievement.objects.filter(achievement_id=request.POST.get('id')).delete()
        with connection.cursor() as cursor:
            sql = "DELETE FROM achievement WHERE achievement_id = %s"
            params = [request.POST.get('id')]
            cursor.execute(sql, params)
        return BaseView.success()

'''
项目成果——论文管理
'''
class AchievementsPapersView(BaseView):

    def get(self, request, module, *args, **kwargs):

        if module == 'show':
            achievements = models.Achievement.objects.all().values()
            return render(request, 'achievements_papers.html',{"achievements":achievements})
        elif module == 'info':
            return self.getInfo(request)
        elif module == 'page':
            return self.getPageInfo(request)
        else:
            return self.error()

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return self.addInfo(request)
        elif module == 'upd':
            return self.updInfo(request)
        elif module == 'del':
            return self.delInfo(request)
        else:
            return self.error()

    def getInfo(self, request):
        sql_query = "SELECT * FROM paper WHERE id = "+request.GET.get('id')
        item = query_one_dict(sql_query)

        resl = {
            'id': item["id"],
            'paper_name': item["paper_name"],
            'paper_date': item["paper_date"],
            'other_paper_details':item["other_paper_details"],
            'achievement_Id': item["achievement_id"]
        }

        return BaseView.successData(resl)

    def getPageInfo(self, request):
        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        s_paper_name = request.GET.get('paper_name')

        sql_query = "SELECT * FROM Paper"
        # 加入查询条件
        if BaseView.isExit(s_paper_name):
            sql_query +=" WHERE paper_name = "+"\""+s_paper_name+"\""
        with transaction.atomic():
            data = models.Paper.objects.raw(sql_query)
        paginator = Paginator(data, pageSize)
        resl = []
        for item in list(paginator.page(pageIndex)):
            achievement_name = "-" if not BaseView.isExit(item.achievement) else item.achievement.achievement_name
            temp = {
                'id': item.id,
                'paper_name': BaseView.check_exist(item.paper_name),
                'paper_date': BaseView.check_exist(item.paper_date),
                'other_paper_details': BaseView.check_exist(item.other_paper_details),
                'achievement_name': achievement_name,
            }
            resl.append(temp)

        pageData = BaseView.parasePage(pageIndex, pageSize,
                                   paginator.page(pageIndex).paginator.num_pages,
                                   paginator.count, resl)

        return BaseView.successData(pageData)

    def addInfo(self, request):
        with connection.cursor() as cursor:
            sql = "INSERT INTO Paper (paper_name,paper_date,other_paper_details,achievement_id) VALUES (%s,%s,%s,%s)"
            params =[request.POST.get('paper_name'),
                     request.POST.get('paper_date'),
                     request.POST.get('other_paper_details'),
                     request.POST.get('achievement_Id')]
            cursor.execute(sql, params)
        return BaseView.success()


    def updInfo(self, request):
        with connection.cursor() as cursor:
            sql = "UPDATE Paper " \
                  "SET paper_name = %s, paper_date = %s, other_paper_details = %s, achievement_Id = %s" \
                  "WHERE id= %s"
            params =[request.POST.get('paper_name'),
                     request.POST.get('paper_date'),
                     request.POST.get('other_paper_details'),
                     request.POST.get('achievement_Id'),
                     request.POST.get('id')]
            cursor.execute(sql, params)
        return BaseView.success()

    def delInfo(self, request):
        # models.Achievement.objects.filter(achievement_id=request.POST.get('id')).delete()
        with connection.cursor() as cursor:
            sql = "DELETE FROM Paper WHERE id = %s"
            params = [request.POST.get('id')]
            cursor.execute(sql, params)
        return BaseView.success()

'''
项目成果——专利管理
'''
class AchievementsPatentsPapersView(BaseView):

    def get(self, request, module, *args, **kwargs):

        if module == 'show':
            achievements = models.Achievement.objects.all().values()
            return render(request, 'achievements_patents.html',{"achievements":achievements})
        elif module == 'info':
            return self.getInfo(request)
        elif module == 'page':
            return self.getPageInfo(request)
        else:
            return self.error()

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return self.addInfo(request)
        elif module == 'upd':
            return self.updInfo(request)
        elif module == 'del':
            return self.delInfo(request)
        else:
            return self.error()

    def getInfo(self, request):
        sql_query = "SELECT * FROM Patents WHERE patent_id = "+request.GET.get('id')
        item = query_one_dict(sql_query)

        resl = {
            'id': item["patent_id"],
            'patent_name': item["patent_name"],
            'patent_type': item["patent_type"],
            'other_details':item["other_details"],
            'achievement_Id': item["achievement_id"]
        }
        return BaseView.successData(resl)

    def getPageInfo(self, request):
        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        s_patent_name = request.GET.get('patent_name')

        sql_query = "SELECT * FROM Patents"
        # 加入查询条件
        if BaseView.isExit(s_patent_name):
            sql_query +=" WHERE patent_name = "+"\""+s_patent_name+"\""
        with transaction.atomic():
            data = models.Patents.objects.raw(sql_query)
        paginator = Paginator(data, pageSize)
        resl = []
        for item in list(paginator.page(pageIndex)):
            achievement_name = "-" if not BaseView.isExit(item.achievement) else item.achievement.achievement_name
            temp = {
                'id': item.patent_id,
                'patent_name': BaseView.check_exist(item.patent_name),
                'patent_type': BaseView.check_exist(item.patent_type),
                'other_details': BaseView.check_exist(item.other_details),
                'achievement_name': achievement_name,
            }
            resl.append(temp)

        pageData = BaseView.parasePage(pageIndex, pageSize,
                                   paginator.page(pageIndex).paginator.num_pages,
                                   paginator.count, resl)

        return BaseView.successData(pageData)

    def addInfo(self, request):
        with connection.cursor() as cursor:
            sql = "INSERT INTO Patents (patent_name,patent_type,other_details,achievement_id) VALUES (%s,%s,%s,%s)"
            params =[request.POST.get('patent_name'),
                     request.POST.get('patent_type'),
                     request.POST.get('other_details'),
                     request.POST.get('achievement_Id')]
            cursor.execute(sql, params)
        return BaseView.success()


    def updInfo(self, request):
        with connection.cursor() as cursor:
            sql = "UPDATE Patents " \
                  "SET patent_name = %s, patent_type = %s, other_details = %s, achievement_Id = %s" \
                  "WHERE patent_id= %s"
            params =[request.POST.get('patent_name'),
                     request.POST.get('patent_type'),
                     request.POST.get('other_details'),
                     request.POST.get('achievement_Id'),
                     request.POST.get('id')]
            cursor.execute(sql, params)
        return BaseView.success()

    def delInfo(self, request):
        # models.Achievement.objects.filter(achievement_id=request.POST.get('id')).delete()
        with connection.cursor() as cursor:
            sql = "DELETE FROM Patents WHERE patent_id = %s"
            params = [request.POST.get('id')]
            cursor.execute(sql, params)
        return BaseView.success()


'''
项目成果——软件著作权管理
'''
class AchievementsSoftwareCopyrightsPapersView(BaseView):

    def get(self, request, module, *args, **kwargs):

        if module == 'show':
            achievements = models.Achievement.objects.all().values()
            return render(request, 'achievements_softwareCopyrights.html',{"achievements":achievements})
        elif module == 'info':
            return self.getInfo(request)
        elif module == 'page':
            return self.getPageInfo(request)
        else:
            return self.error()

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return self.addInfo(request)
        elif module == 'upd':
            return self.updInfo(request)
        elif module == 'del':
            return self.delInfo(request)
        else:
            return self.error()

    def getInfo(self, request):
        sql_query = "SELECT * FROM SoftwareCopyrights WHERE copyright_id = "+request.GET.get('id')
        item = query_one_dict(sql_query)

        resl = {
            'id': item["copyright_id"],
            'copyright_name': item["copyright_name"],
            'other_details':item["other_details"],
            'achievement_Id': item["achievement_id"]
        }
        return BaseView.successData(resl)

    def getPageInfo(self, request):
        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        s_copyright_name = request.GET.get('copyright_name')

        sql_query = "SELECT * FROM SoftwareCopyrights"
        # 加入查询条件
        if BaseView.isExit(s_copyright_name):
            sql_query +=" WHERE copyright_name = "+"\""+s_copyright_name+"\""
        with transaction.atomic():
            data = models.SoftwareCopyrights.objects.raw(sql_query)
        paginator = Paginator(data, pageSize)
        resl = []
        for item in list(paginator.page(pageIndex)):
            achievement_name = "-" if not BaseView.isExit(item.achievement) else item.achievement.achievement_name
            temp = {
                'id': item.copyright_id,
                'copyright_name': BaseView.check_exist(item.copyright_name),
                'other_details': BaseView.check_exist(item.other_details),
                'achievement_name': achievement_name,
            }
            resl.append(temp)

        pageData = BaseView.parasePage(pageIndex, pageSize,
                                   paginator.page(pageIndex).paginator.num_pages,
                                   paginator.count, resl)

        return BaseView.successData(pageData)

    def addInfo(self, request):
        with connection.cursor() as cursor:
            sql = "INSERT INTO SoftwareCopyrights (copyright_name,other_details,achievement_id) VALUES (%s,%s,%s)"
            params =[request.POST.get('copyright_name'),
                     request.POST.get('other_details'),
                     request.POST.get('achievement_Id')]
            cursor.execute(sql, params)
        return BaseView.success()


    def updInfo(self, request):
        with connection.cursor() as cursor:
            sql = "UPDATE SoftwareCopyrights " \
                  "SET copyright_name = %s, other_details = %s, achievement_Id = %s" \
                  "WHERE copyright_id= %s"
            params =[request.POST.get('copyright_name'),
                     request.POST.get('other_details'),
                     request.POST.get('achievement_Id'),
                     request.POST.get('id')]
            cursor.execute(sql, params)
        return BaseView.success()

    def delInfo(self, request):
        # models.Achievement.objects.filter(achievement_id=request.POST.get('id')).delete()
        with connection.cursor() as cursor:
            sql = "DELETE FROM SoftwareCopyrights WHERE copyright_id = %s"
            params = [request.POST.get('id')]
            cursor.execute(sql, params)
        return BaseView.success()
