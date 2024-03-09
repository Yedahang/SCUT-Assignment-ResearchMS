function handle(){

	$("button[event=upd]").on("click", (e)=>{

        $.ajax({
            url: "/researchMS/projects_participators/info/",
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
                      var dateValue = res.data.join_date; // 获取日期数据
                      $('#join_date').val(dateValue); // 将日期数据设置为表单字段的值
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
                url: "/researchMS/projects_participators/del/",
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
        url: "/researchMS/projects_participators/page/",
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
				field: "project_name",
				title: "所属项目",
				align: "center",
			},
			{
				field: "researcher_name",
				title: "科研人员",
				align: "center",
			},
			{
				field: "subproject_id",
				title: "参与子课题编号",
				align: "center",
			},
            {
				field: "join_date",
				title: "参加时间",
				align: "center",
			},
            {
				field: "workload",
				title: "工作量",
				align: "center",
			},
            {
				field: "discretionary_funds",
				title: "可支配经费",
				align: "center",
			},
			{
                title: "操作",
                template: (d)=>{

                    return `
                            <button type="button" event="upd" data="${d.id}" class="fater-btn fater-btn-primary fater-btn-sm">
                                <span data="${d.project_id}" class="fa fa-edit"></span>
                            </button>
                            <button type="button" event="del" data="${d.id}" class="fater-btn fater-btn-danger fater-btn-sm">
                                <span data="${d.project_id}" class="fa fa-trash"></span>
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

        tableView.where["project_id"] = $("[name=para1]").val();

        $.table(tableView);
    });

    $("button[event=add]").on("click", ()=>{

        $.model(".addWin");
    });

    $("#addFormBtn").on("click", ()=>{


        let formElement = document.forms["addForm"];

        let formData = new FormData(formElement);

        $.ajax({
            url: "/researchMS/projects_participators/add/",
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
            url: "/researchMS/projects_participators/upd/",
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