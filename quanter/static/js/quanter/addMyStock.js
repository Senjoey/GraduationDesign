function addMyStock() {
    var stockCode = $("#stockCode").val();
    if(!stockCode){
        alert("请输入股票代码！")
    } else {
        // 利用正则表达式检查是否输入了6位数字
        var reg = new RegExp("^\\d{6}$");
        if(!reg.test(stockCode)) {
            alert("请输入6位数字！")
        } else {
            $.ajax({
                type: "GET",
                url: "check_database",
                data: {
                     code: stockCode
                },
                dataType: "json",
                success: function(data){
                    if(data['is_already_in_my_stock']){//已经在选股中了
                        alert("已经在选股中了！");
                    } else {//还不在选股中
                        if(data['is_in_stock']) {
                            window.location.href = "/quanter/add_my_stock?code=" + stockCode;
                            alert("成功添加到选股！");
                        } else {
                            alert("不在数据库中！");
                        }
                    }
                },
                error:function () {
                     alert("发生异常！");
                 }
            });
        }
    }
}