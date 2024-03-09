function handle(){

	$("button[event=upd]").on("click", (e)=>{

        $.ajax({
            url: "/jobs/researchRooms/info/",
            type: "GET",
            async: false,
            data:{
                id: $(e.target).attr("data"),
            },
            success: function(res){
                if(res.code == 0){
                    var selectElement = document.getElementsByName("director_id")[0];
                    // 循环遍历 directors 数组，创建并添加每个主任的选项
                    var directors = res.data['directors']
                    for (var i = 0; i < directors.length; i++) {
                      var director = directors[i];
                      var option = document.createElement("option");
                      option.value = director.researcher_id;
                      option.text = director.name;
                      selectElement.appendChild(option);
                    }
                    // 获取日期输入框的DOM对象
                    var directorStartDateInput = document.getElementById("director_start_date_upd");
                    // 设置日期值
                    directorStartDateInput.value = res.data['director_start_date'];

                    $.initForm("updForm", res.data);
                    $.model(".updWin");
                }else{
                    $.msg("error", res.msg);
                }
            }
        });
    });

    $("button[event=del]").on("click", (e)=>{

        $.confirm("确认要删除吗", () =>{

            $.ajax({
                url: "/jobs/researchRooms/del/",
                type: "POST",
                async: false,
                data:{
                    id: $(e.target).attr("data"),
                },
                success: function(res){
                    if(res.code == 0){
                        $.alert(res.msg, () =>{

                            window.location.reload();
                        });
                    }else{
                        $.msg("error", res.msg);
                    }
                }
            });
        });
    });
}

$(function (){

    let tableView =  {
        el: "#tableShow",
        url: "/jobs/researchRooms/page/",
        method: "GET",
        where: {
            pageIndex: 1,
            pageSize: 10
        },
        page: true,
        cols: [
            {
                type: "number",
                title: "序号",
            },
			{
				field: "name",
				title: "研究室名称",
				align: "center",
			},
			{
				field: "introduction",
				title: "研究方向介绍",
				align: "center",
			},
            {
				field: "secretary_name",
				title: "秘书",
				align: "center",
			},
            {
				field: "director_name",
				title: "主任",
				align: "center",
			},
            {
				field: "director_start_date",
				title: "主任_上任时间",
				align: "center",
			},
            {
				field: "director_tenure",
				title: "主任_任期(年)",
				align: "center",
			},
			{
                title: "操作",
                template: (d)=>{

                    return `
                            <button type="button" event="upd" data="${d.id}" class="fater-btn fater-btn-primary fater-btn-sm">
                                <span data="${d.id}" class="fa fa-edit"></span>
                            </button>
                            <button type="button" event="del" data="${d.id}" class="fater-btn fater-btn-danger fater-btn-sm">
                                <span data="${d.id}" class="fa fa-trash"></span>
                            </button>
                            `;
                }
            }
        ],
        binds: (d) =>{

            handle();
        }
    }
    $.table(tableView);

    $(".fater-btn-form-qry").on("click", ()=>{

        tableView.where["name"] = $("[name=para1]").val();

        $.table(tableView);
    });

    $("button[event=add]").on("click", ()=>{

        $.model(".addWin");
    });

    $("#addFormBtn").on("click", ()=>{

        let formElement = document.forms['addForm'];
        let formData = new FormData(formElement);
        $.ajax({
            url: "/jobs/researchRooms/add/",
            type: "POST",
            data: formData,
            processData: false,// 禁止将数据处理为查询字符串
            contentType: false, // 禁止设置Content-Type头部
            success: function(res){
                if(res.code == 0){
                    $.alert(res.msg, () =>{

                        window.location.reload();
                    });
                }else{
                    $.msg("error", res.msg);
                }
            }
        });
    });

    $("#updFormBtn").on("click", ()=>{

        let formElement = document.forms['updForm'];
        let formData = new FormData(formElement);
        $.ajax({
            url: "/jobs/researchRooms/upd/",
            type: "POST",
            data: formData,
            processData: false,// 禁止将数据处理为查询字符串
            contentType: false, // 禁止设置Content-Type头部
            success: function(res){
                if(res.code == 0){
                    $.alert(res.msg, () =>{
                        window.location.reload();
                    });
                }else{
                    $.msg("error", res.msg);
                }
            }
        });
    });
});