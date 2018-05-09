function toEdit() {
    $("#positiveDepartureDiv").removeClass("readonly").find(":input").attr("readonly", false);
    $("#negativeDepartureDiv").removeClass("readonly").find(":input").attr("readonly", false);
    $("#stopProfitDiv").removeClass("readonly").find(":input").attr("readonly", false);
    $("#stopLossDiv").removeClass("readonly").find(":input").attr("readonly", false);
    $("#negativeDepartureOperationBtns").css("visibility", "visible");
    $("#negativeDepartureEditBtn").css("visibility", "hidden");
}

function toCancel() {
    //修改回原来的值
    $("#positiveDeparture").val(strategyDict['positive_departure']);
    $("#negativeDeparture").val(strategyDict['negative_departure']);
    $("#stopProfit").val(strategyDict['stop_profit']);
    $("#stopLoss").val(strategyDict['stop_loss']);

    $("#negativeDepartureOperationBtns").css("visibility", "hidden");
    $("#negativeDepartureEditBtn").css("visibility", "visible");
    $("#positiveDepartureDiv").addClass("readonly").find(":input").attr("readonly", true);
    $("#negativeDepartureDiv").addClass("readonly").find(":input").attr("readonly", true);
    $("#stopProfitDiv").addClass("readonly").find(":input").attr("readonly", true);
    $("#stopLossDiv").addClass("readonly").find(":input").attr("readonly", true);

}

function toSave() {
    var positiveDeparture = $("#positiveDeparture").val();
    if(parseInt(positiveDeparture)<5.0) {
        alert("正乖离参数需大于等于5.0！");
        return;
    }
    var negativeDeparture = $("#negativeDeparture").val();
    if(parseInt(negativeDeparture)>-5.0) {
        alert("负乖离参数需小于等于-5.0！");
        return;
    }
    $("#negativeDepartureOperationBtns").css("visibility", "hidden");
    $("#negativeDepartureEditBtn").css("visibility", "visible");
    $("#positiveDepartureDiv").addClass("readonly").find(":input").attr("readonly", true);
    $("#negativeDepartureDiv").addClass("readonly").find(":input").attr("readonly", true);
    $("#stopProfitDiv").addClass("readonly").find(":input").attr("readonly", true);
    $("#stopLossDiv").addClass("readonly").find(":input").attr("readonly", true);
    // 读取参数，发起请求，存入数据库
    var stopProfit = $("#stopProfit").val();
    var stopLoss = $("#stopLoss").val();
    window.location.href = "/quanter/strategy_setting_modify?positiveDeparture=" + positiveDeparture + "&negativeDeparture=" +
        negativeDeparture + "&stopProfit=" + stopProfit + "&stopLoss=" + stopLoss;

}

