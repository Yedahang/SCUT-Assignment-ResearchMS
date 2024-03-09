function handle(){

	$("button[event=upd]").on("click", (e)=>{

        $.ajax({
            url: "/jobs/achievements_patents/info/",
            type: "GET",
            async: false,
            data:{
                id: $(e.target).attr("data"),
            },
            success: function(res){
                if(res.code == 0){

                    $.initForm("updForm", res.data);
                    $(document).ready(function() {
                      // 将日期数据应用到表单字段
                      var dateValue = res.data.achievement_date; // 获取日期数据
                      $('#achievement_date').val(dateValue); // 将日期数据设置为表单字段的值
                    });
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
                url: "/jobs/achievements_patents/del/",
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

    $("button[event=cancel]").on("click", (e)=>{

        $.ajax({
            url: "/jobs/achievements_patents/upd/",
            type: "POST",
            async: false,
            data:{
                id: $(e.target).attr("data"),
                status: 2
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
}

$(function (){

    let tableView =  {
        el: "#tableShow",
        url: "/jobs/achievements_patents/page/",
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
				field: "patent_name",
				title: "专利名",
				align: "center",
			},
            {
				field: "patent_type",
				title: "专利类型",
				align: "center",
			},
            {
				field: "achievement_name",
				title: "所属科研成果",
				align: "center",
			},
            {
				field: "other_details",
				title: "详细信息",
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

        tableView.where["patent_name"] = $("[name=para1]").val();

        $.table(tableView);
    });

    $("button[event=add]").on("click", ()=>{
        $.model(".addWin");
    });

    $("#addFormBtn").on("click", ()=>{

        let formElement = document.forms['addForm'];
        let formData = new FormData(formElement);
        $.ajax({
            url: "/jobs/achievements_patents/add/",
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
            url: "/jobs/achievements_patents/upd/",
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