function handle(){

	$("button[event=upd]").on("click", (e)=>{

        $.ajax({
            url: "/jobs/secretaries/info/",
            type: "GET",
            async: false,
            data:{
                id: $(e.target).attr("data"),
            },
            success: function(res){
                if(res.code == 0){

                    $.initForm("updForm", res.data);
                    $.model(".updWin");
                }else{
                    $.msg("error", res.msg);
                }
            }
        });
    });

    $("button[event=sned]").on("click", (e)=>{

        $.ajax({
            url: "/jobs/secretaries/add/",
            type: "POST",
            async: false,
            data:{
                status: 0,
                jobId: $(e.target).attr("data"),
            },
            success: function(res){
                if(res.code == 0){

                    $.alert('投递成功', () =>{

                        window.location.reload();
                    });
                }else{
                    $.msg("error", res.msg);
                }
            }
        });
    });

    $("button[event=del]").on("click", (e)=>{

        $.confirm("确认要删除吗", () =>{

            $.ajax({
                url: "/jobs/secretaries/del/",
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
        url: "/jobs/secretaries/page/",
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
				field: "employee_id",
				title: "工号",
				align: "center",
			},
			{
				field: "name",
				title: "姓名",
				align: "center",
			},
			{
				field: "gender",
				title: "性别",
				align: "center",
			},
			{
				field: "age",
				title: "年龄",
				align: "center",
			},
            {
				field: "hire_date",
				title: "聘用时间",
				align: "center",
			},
            {
				field: "responsibilities",
				title: "职责",
				align: "center",
			},
            {
                title: "操作",
                template: (d)=>{

                    return `
                            <button type="button" event="upd" data="${d.secretary_id}" class="fater-btn fater-btn-primary fater-btn-sm">
                                <span data="${d.secretary_id}" class="fa fa-edit"></span>
                            </button>
                            <button type="button" event="del" data="${d.secretary_id}" class="fater-btn fater-btn-danger fater-btn-sm">
                                <span data="${d.secretary_id}" class="fa fa-trash"></span>
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
        let formElement = document.forms["addForm"];
        // let hire_date = formElement.elements["hire_date"].value;
        // let formVal = $.getFrom("addForm");
        let formData = new FormData(formElement);
        // formVal.append("hire_date", hire_date)
        $.ajax({
            url: "/jobs/secretaries/add/",
            type: "POST",
            data: formData,
            processData: false,  // 禁止将数据处理为查询字符串
            contentType: false,  // 禁止设置Content-Type头部
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

        let formElement = document.forms["updForm"];

        let formData = new FormData(formElement);
        $.ajax({
            url: "/jobs/secretaries/upd/",
            type: "POST",
            data: formData,
            processData: false,  // 禁止将数据处理为查询字符串
            contentType: false,  // 禁止设置Content-Type头部
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