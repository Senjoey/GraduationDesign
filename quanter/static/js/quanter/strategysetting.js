function toEdit() {
    $("#positiveDepartureDiv").removeClass("readonly").find(":input").attr("readonly", false);
    $("#negativeDepartureDiv").removeClass("readonly").find(":input").attr("readonly", false);
    $("#stopProfitDiv").removeClass("readonly").find(":input").attr("readonly", false);
    $("#stopLossDiv").removeClass("readonly").find(":input").attr("readonly", false);
    $("#negativeDepartureOperationBtns").css("visibility", "visible");
    $("#negativeDepartureEditBtn").css("visibility", "hidden");
}

function toCancel() {
    $("#negativeDepartureOperationBtns").css("visibility", "hidden");
    $("#negativeDepartureEditBtn").css("visibility", "visible");
    $("#positiveDepartureDiv").addClass("readonly").find(":input").attr("readonly", true);
    $("#negativeDepartureDiv").addClass("readonly").find(":input").attr("readonly", true);
    $("#stopProfitDiv").addClass("readonly").find(":input").attr("readonly", true);
    $("#stopLossDiv").addClass("readonly").find(":input").attr("readonly", true);
}

function toSave() {
    $("#negativeDepartureOperationBtns").css("visibility", "hidden");
    $("#negativeDepartureEditBtn").css("visibility", "visible");
    $("#positiveDepartureDiv").addClass("readonly").find(":input").attr("readonly", true);
    $("#negativeDepartureDiv").addClass("readonly").find(":input").attr("readonly", true);
    $("#stopProfitDiv").addClass("readonly").find(":input").attr("readonly", true);
    $("#stopLossDiv").addClass("readonly").find(":input").attr("readonly", true);
    // 读取参数，发起请求，存入数据库
    var positiveDeparture = $("#positiveDeparture").val();
    var negativeDeparture = $("#negativeDeparture").val();
    var stopProfit = $("#stopProfit").val();
    var stopLoss = $("#stopLoss").val();
    window.location.href = "/quanter/strategy_setting?positiveDeparture=" + positiveDeparture + "&negativeDeparture=" +
        negativeDeparture + "&stopProfit=" + stopProfit + "&stopLoss=" + stopLoss;

}

