function handle(){

	$("button[event=upd]").on("click", (e)=>{

        $.ajax({
            url: "/researchMS/projectLogs/info/",
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

    $("button[event=del]").on("click", (e)=>{

        $.confirm("确认要删除吗", () =>{

            $.ajax({
                url: "/researchMS/projectLogs/del/",
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

let colsShow = [];

if($('#sessionUserType').val() == 2){

      colsShow =  [
            {
                type: "number",
                title: "序号",
            },
			{
				field: "name",
				title: "项目名称",
				align: "center",
			},
			{
				field: "duty",
				title: "岗位职责",
				align: "center",
			},
			{
				field: "detail",
				title: "项目详情",
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
        ]
}else{
    colsShow =  [
            {
                type: "number",
                title: "序号",
            },
			{
				field: "director_id",
				title: "主任编号",
				align: "center",
			},
			{
				field: "lab_id",
				title: "研究室编号",
				align: "center",
			},
			{
				field: "start_date",
				title: "任期",
				align: "center",
			},
			{
				field: "tenure",
				title: "tenure",
				align: "center",
			},
			{
				field: "detail",
				title: "项目详情",
				align: "center",
			}
        ]
}

$(function (){

    let tableView =  {
        el: "#tableShow",
        url: "/researchMS/projectLogs/page/",
        method: "GET",
        where: {
            pageIndex: 1,
            pageSize: 10
        },
        page: true,
        cols: colsShow,
        binds: (d) =>{

            handle();
        }
    }
    $.table(tableView);

    $(".fater-btn-form-qry").on("click", ()=>{

        tableView.where["name"] = $("[name=para1]").val();
        tableView.where["studentName"] = $("[name=para2]").val();

        $.table(tableView);
    });

    $("button[event=add]").on("click", ()=>{

        $.model(".addWin");
    });

    $("#addFormBtn").on("click", ()=>{

        let formVal = $.getFrom("addForm");

        $.ajax({
            url: "/researchMS/projectLogs/add/",
            type: "POST",
            data: formVal,
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

        let formVal = $.getFrom("updForm");

        $.ajax({
            url: "/researchMS/projectLogs/upd/",
            type: "POST",
            data: formVal,
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