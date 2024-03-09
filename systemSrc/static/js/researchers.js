function handle(){

	$("button[event=upd]").on("click", (e)=>{

        $.ajax({
            url: "/researchMS/researchers/info/",
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
                url: "/researchMS/researchers/del/",
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
        url: "/researchMS/researchers/page/",
        method: "GET",
        where: {
            pageIndex: 1,
            pageSize: 10
        },
        page: true,
        cols: [
			{
				title: "序号",
				type: "number",
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
				field: "title",
				title: "职称",
				align: "center",
			},
            {
				field: "age",
				title: "年龄",
				align: "center",
			},

			{
				field: "research_area",
				title: "研究方向",
				align: "center",
			},
			{
				field: "research_roomName",
				title: "所属研究室",
				align: "center",
			},
			{
                title: "操作",
                template: (d)=>{

                    return `
                            <button type="button" event="upd" data="${d.researcher_id}" class="fater-btn fater-btn-primary fater-btn-sm">
                                <span data="${d.researcher_id}" class="fa fa-edit"></span>
                            </button>
                            <button type="button" event="del" data="${d.researcher_id}" class="fater-btn fater-btn-danger fater-btn-sm">
                                <span data="${d.researcher_id}" class="fa fa-trash"></span>
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

        tableView.where["employee_id"] = $("[name=para1]").val();
        tableView.where["name"] = $("[name=para2]").val();
        tableView.where["research_room_id"] = $("[name=para3]").val();

        $.table(tableView);
    });

    $("button[event=add]").on("click", ()=>{

        $.model(".addWin");
    });

    $("#addFormBtn").on("click", ()=>{

        let formVal = $.getFrom("addForm");

        $.ajax({
            url: "/researchMS/researchers/add/",
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
            url: "/researchMS/researchers/upd/",
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