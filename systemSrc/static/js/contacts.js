
function handle(){

	$("button[event=upd]").on("click", (e)=>{

        $.ajax({
            url: "/jobs/contacts/info/",
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
                url: "/jobs/contacts/del/",
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
        url: "/jobs/contacts/page/",
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
				title: "姓名",
				align: "center",
			},
            {
				field: "office_phone",
				title: "办公电话",
				align: "center",
			},
            {
				field: "mobile_phone",
				title: "移动电话",
				align: "center",
			},
            {
				field: "email",
				title: "邮件",
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
            url: "/jobs/contacts/add/",
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
            url: "/jobs/contacts/upd/",
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