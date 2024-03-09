from django.db import models
employee_id_max_length = 12
class Secretary(models.Model):
    secretary_id = models.AutoField("ID",primary_key=True) #秘书编号
    employee_id = models.CharField("工号",max_length=employee_id_max_length) #工号
    name = models.CharField("名字",max_length=100) #姓名
    GENDER_TYPES = [
        ('男', '男'),
        ('女', '女'),
    ]
    gender = models.CharField("性别",choices=GENDER_TYPES,max_length=10,null=True,blank=True) #性别
    age = models.IntegerField("年龄",null=True,blank=True) #年龄
    hire_date = models.DateField("聘用时间",null=True,blank=True)  #聘用时间
    responsibilities = models.TextField("职责",null=True,blank=True)   #职责

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'secretary'
        verbose_name = '秘书信息'     # 模型名称(单数)
        verbose_name_plural = verbose_name  # 模型名称(复数)

class Contact(models.Model):
    contact_id = models.AutoField("ID",primary_key = True)
    name = models.CharField("名字",max_length=100,unique=True)#姓名
    office_phone = models.CharField("办公电话",max_length=20,null=True,blank=True)
    mobile_phone = models.CharField("移动电话",max_length=20,null=True,blank=True)
    email = models.EmailField("邮箱",null=True,blank=True)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = '联系人信息'     # 模型名称(单数)
        verbose_name_plural = verbose_name  # 模型名称(复数)
        db_table = 'Contact' # 自定义数据库表名

# 单位信息表
class Organization(models.Model):
    organization_id = models.AutoField("ID",primary_key=True)
    organization_name = models.CharField("单位名称",max_length=100,unique=True)
    address = models.CharField("地址",max_length=200,blank=True)
    leader = models.ForeignKey(Contact,
                               on_delete=models.CASCADE,
                               null=True,
                               related_name='organizations_as_leader',
                               verbose_name='负责人',blank=True
                               ) #负责人
    contacts = models.ManyToManyField(Contact, related_name='organizations_as_contact_persons'
                                      ,verbose_name='联系人',blank=True)  # 联系人
    def __str__(self):
        return self.organization_name
    class Meta:
        verbose_name = '单位信息'     # 模型名称(单数)
        verbose_name_plural = verbose_name  # 模型名称(复数)
        db_table = 'Organization' # 自定义数据库表名

class RearchRooms(models.Model):
    id = models.AutoField('研究室编号', primary_key=True)
    name = models.CharField('研究室名称',  max_length=32, null=False,unique=True)
    introduction = models.TextField('研究方向介绍', db_column='introduction', max_length=19,null=True,blank=True)
    secretary = models.ForeignKey(Secretary,on_delete=models.CASCADE,null=True,blank=True,
                                  verbose_name='秘书') #每个研究室设秘书一人
    director = models.ForeignKey("Researcher",on_delete=models.CASCADE,null=True,blank=True,
                                 verbose_name='主任')#每个研究室设主任一人
    director_start_date = models.DateField(null=True,blank=True,verbose_name='主任_上任时间')  # 上任时间
    director_tenure = models.IntegerField(null=True,blank=True,verbose_name='主任_任期(年)')  # 任期
    def __str__(self):
        return self.name

    class Meta:
        db_table = 'researchRoom'
        verbose_name = '研究室信息'     # 模型名称(单数)
        verbose_name_plural = verbose_name  # 模型名称(复数)


class Office(models.Model):
    id = models.AutoField('办公场地编号', primary_key=True)
    research_room = models.ForeignKey(RearchRooms, on_delete=models.CASCADE,null=True,blank=True,verbose_name='所属研究室')  # 研究室编号（外键）
    office_area = models.DecimalField("办公面积(m\u00B2)",max_digits=8, decimal_places=2,null=True,blank=True)  # 办公面积
    address = models.CharField("地址",max_length=100)  # 地址
    class Meta:
        db_table = 'office'
        verbose_name ='办公场地信息'
        verbose_name_plural = verbose_name  # 模型名称(复数)
class Researcher(models.Model):
    researcher_id = models.AutoField(primary_key=True,verbose_name='ID')  # 科研人员编号（主键）
    employee_id = models.CharField(max_length=employee_id_max_length,verbose_name='工号')  # 工号
    name = models.CharField(max_length=100,verbose_name='姓名')  # 姓名
    GENDER_TYPES = [
        ('男', '男'),
        ('女', '女'),
    ]
    gender = models.CharField(max_length=10,choices=GENDER_TYPES,null=True,verbose_name='性别')  # 性别
    title = models.CharField(max_length=100,null=True,verbose_name='职称')  # 职称
    age = models.IntegerField(null=True,verbose_name='年龄')  # 年龄
    research_area = models.CharField(max_length=200,null=True,verbose_name='研究方向')  # 研究方向
    research_room = models.ForeignKey(RearchRooms, on_delete=models.CASCADE,null=True,verbose_name='所属研究室')  # 研究室编号（外键）

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Researcher'  # 自定义数据库表名
        verbose_name = '科研人员信息'     # 模型名称(单数)
        verbose_name_plural = verbose_name  # 模型名称(复数)



# 科研项目
class Project(models.Model):
    project_id = models.AutoField(primary_key=True,verbose_name ="ID")  # 项目编号（主键）
    projectCode = models.CharField(max_length=100,verbose_name ="项目号",unique=True) #项目号
    researcher = models.ManyToManyField(Researcher,through="ProjectResearcher",related_name='in_project',verbose_name ="参与人员")
    project_leader = models.ForeignKey(Researcher,related_name='leading_projects', on_delete=models.CASCADE,null=True,blank=True)  # 项目负责人
    project_name = models.CharField(max_length=100,verbose_name ="项目名")  # 项目名
    research_content = models.TextField(null=True,verbose_name ="研究内容")  # 研究内容
    total_funding = models.DecimalField(max_digits=10, decimal_places=2,null=True, verbose_name ="经费总额(元)")  # 经费总额
    start_date = models.DateField(null=True,verbose_name ="开工时间")  # 开工时间
    completion_date = models.DateField(null=True,verbose_name ="完成时间")  # 完成时间

    client = models.ForeignKey(Organization, related_name="client_project",
                               on_delete=models.CASCADE,null=True, verbose_name ="唯一委托方")# 唯一委托方
    qualityMonitor = models.ForeignKey(Organization, related_name="qualityMonitor_project",
                                       on_delete=models.CASCADE,null=True, verbose_name ="唯一监测方")  # 唯一监测方
    collaborators = models.ManyToManyField(Organization,through="ProjectCollaborators",verbose_name ="合作方")# 多个合作方
    def __str__(self):
        return self.project_name

    class Meta:
        db_table = 'Projects'  # 自定义数据库表名
        verbose_name = '科研项目信息'     # 模型名称(单数)
        verbose_name_plural = verbose_name  # 模型名称(复数)

# 科研项目合作方
class ProjectCollaborators(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)  # 项目编号（外键，关联Project表）
    collaborators = models.ForeignKey(Organization, on_delete=models.CASCADE)

    def __str__(self):
        return ""

    class Meta:
        unique_together = ['project','collaborators']

class Subproject(models.Model):
    subproject_id = models.AutoField(primary_key = True,verbose_name ="ID") #子课题编号(主键)
    project = models.ForeignKey(Project,on_delete=models.CASCADE,
                                verbose_name ="所属项目")# 项目编号（外键，关联Project表）
    leader = models.ForeignKey(Researcher,on_delete=models.CASCADE,
                               null=True,blank=True,verbose_name ="负责人")# 子课题负责人编号（外键，关联Researcher表）
    completion_time = models.DateField(null=True,blank=True,verbose_name ="完成时间要求") #完成时间要求
    discretionary_funds = models.DecimalField(max_digits=10,decimal_places=2,
                                              null=True,blank=True,verbose_name ="支配经费") #可支配经费
    tech_specification = models.TextField(null=True,blank=True,verbose_name ="技术指标") #技术指标
    def __str__(self):
        return self.subproject_id.__str__()

    class Meta:
        db_table = 'Subproject' # 自定义数据库表名
        verbose_name = '科研项目信息_子课题'     # 模型名称(单数)
        verbose_name_plural = verbose_name  # 模型名称(复数)

# 项目参与科研人员
class ProjectResearcher(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID")
    project = models.ForeignKey(Project, on_delete=models.CASCADE,verbose_name ="所属项目")  # 项目编号（外键，关联Project表）
    researcher = models.ForeignKey(Researcher, on_delete=models.CASCADE,verbose_name ="科研人员")  # 科研人员编号（外键，关联Researcher表)
    subproject = models.ForeignKey(Subproject, on_delete=models.CASCADE,verbose_name ="参与子课题编号")# 参与子课题
    join_date = models.DateField(verbose_name ="参加时间",null=True,blank=True)  # 参加时间
    workload = models.FloatField(verbose_name ="工作量",null=True,blank=True)  # 工作量
    discretionary_funds = models.DecimalField(max_digits=10, decimal_places=2,verbose_name ="可支配经费",null=True,blank=True)  # 可支配经费

    def __str__(self):
        return f"ProjectResearcher {self.id}"

    class Meta:
        unique_together = ['project','researcher']
        verbose_name = '科研项目信息_参与人员'     # 模型名称(单数)
        verbose_name_plural = verbose_name  # 模型名称(复数)

# 项目成果
class Achievement(models.Model):
    achievement_id = models.AutoField(primary_key=True,verbose_name ="ID")
    achievement_name = models.CharField(max_length=100,verbose_name ="成果名",unique=True)#成果名
    achievement_date = models.DateField(verbose_name ="取得时间",null=True)   #取得时间
    contributors = models.ManyToManyField(Researcher,verbose_name ="成果贡献人",null=True,blank=True)
    ranking = models.PositiveIntegerField(verbose_name ="排名",null=True) #排名
    project = models.ForeignKey(Project, on_delete=models.CASCADE,verbose_name ="所属项目",null=True,blank=True) #所属项目

    def __str__(self):
        return self.achievement_name

    class Meta:
        db_table = 'Achievement'  # 自定义数据库表名
        verbose_name = '项目成果信息'     # 模型名称(单数)
        verbose_name_plural = verbose_name  # 模型名称(复数)

class Paper(models.Model):
    id = models.AutoField(primary_key=True,verbose_name ="论文编号")
    paper_name = models.CharField(max_length=100, verbose_name="论文题目")
    paper_date = models.DateField(verbose_name ="取得时间",null=True,blank=True)   #取得时间
    other_paper_details = models.CharField(max_length=200, verbose_name="详细信息",null=True,blank=True)  #
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE,verbose_name ="所属项目成果") #所属项目成果

    def __str__(self):
        return self.paper_name

    class Meta:
        db_table = 'Paper'  # 自定义数据库表名
        verbose_name = '项目成果信息_论文'     # 模型名称(单数)
        verbose_name_plural = verbose_name  # 模型名称(复数)

class Patents(models.Model):
    patent_id = models.AutoField(primary_key=True,verbose_name ="专利编号")
    patent_name = models.CharField(max_length=100, verbose_name="专利名字")
    PATENT_TYPES = [
        ('发明', '发明'),
        ('实用新型', '实用新型'),
        ('外观', '外观'),
    ]

    patent_type = models.CharField(max_length=100, choices=PATENT_TYPES,
                                   verbose_name="专利类型",null=True,blank=True) #发明、实用新型或外观。
    other_details = models.TextField(max_length=200, verbose_name="详细信息",null=True,blank=True)  #
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE,
                                    verbose_name ="所属项目成果",null=True,blank=True) #所属项目成果

    def __str__(self):
        return self.patent_name

    class Meta:
        db_table = 'Patents'  # 自定义数据库表名
        verbose_name = '项目成果信息_专利'     # 模型名称(单数)
        verbose_name_plural = verbose_name  # 模型名称(复数)

# 项目成果
class SoftwareCopyrights(models.Model):
    copyright_id = models.AutoField(primary_key=True,verbose_name ="著作权编号")
    copyright_name = models.CharField(max_length=100, verbose_name="著作权名字")
    other_details = models.TextField(max_length=200, verbose_name="详细信息",null=True,blank=True)  #
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE,verbose_name ="所属项目成果") #所属项目成果

    def __str__(self):
        return self.copyright_name

    class Meta:
        db_table = 'SoftwareCopyrights'  # 自定义数据库表名
        verbose_name = '项目成果信息_软件著作权'     # 模型名称(单数)
        verbose_name_plural = verbose_name  # 模型名称(复数)

class Users(models.Model):
    id = models.AutoField('记录编号', primary_key=True)
    userName = models.CharField('用户账号', db_column='user_name', max_length=32, null=False,unique = True)
    passWord = models.CharField('用户密码', db_column='pass_word', max_length=32, null=False)
    name = models.CharField('用户姓名', max_length=20, null=False)
    gender = models.CharField('用户性别', max_length=4, null=False)
    age = models.IntegerField('用户年龄', null=False)
    phone = models.CharField('联系电话', max_length=11, null=False)
    type = models.IntegerField('用户身份', null=False)
    class Meta:
        db_table = 'users'


