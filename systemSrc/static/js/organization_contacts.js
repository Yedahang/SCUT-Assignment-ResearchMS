
function handle(){

	$("button[event=upd]").on("click", (e)=>{

        $.ajax({
            url: "/researchMS/organization_contacts/info/",
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
                      var dateValue = res.data.completion_time; // 获取日期数据
                      $('#completion_time').val(dateValue); // 将日期数据设置为表单字段的值
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
                url: "/researchMS/organization_contacts/del/",
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
        url: "/researchMS/organization_contacts/page/",
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
				field: "id",
				title: "单位编号",
				align: "center",
			},
			{
				field: "organization_name",
				title: "单位名称",
				align: "center",
			},
            {
				field: "contact_name",
				title: "联系人",
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
            url: "/researchMS/organization_contacts/add/",
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
            url: "/researchMS/organization_contacts/upd/",
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