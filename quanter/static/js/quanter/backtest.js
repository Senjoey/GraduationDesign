function backTest() {
    var startDate = $("#startDate").val();
    var endDate = $("#endDate").val();
    var totalMoney = $("#totalMoney").val();

    if(!validateDate(startDate, endDate)) {
        alert("结束日期不能小于开始日期！");
        return;
    }

    if(parseInt(totalMoney) <= 0.0) {
        alert("资金数额必须大于0！");
        return;
    }

    if(myStockList.length === 0){
        alert("无选股！");
        return;
    }

    // myStockList
    var code_to_test = "";
    var i = 0;
    for(i = 0; i < myStockList.length; i++) {
        if (i < myStockList.length-1) {
            var s=myStockList[i].code+",";
            code_to_test+=s;
        } else {
            var s=myStockList[i].code;
            code_to_test+=s;
        }
    }
    alert("codetotest: "+ code_to_test);
    $.ajax({
             type: "GET",
             url: "back_test_multi_code",
             data: {
                 code: code_to_test,
                 start: startDate,
                 end: endDate,
                 totalMoney: totalMoney
             },
             dataType: "json",
             success: function(data){
                 alert("返回成功");

                var myChart = echarts.init(document.getElementById('charts'));
                var dates = data['date_list'];
                var profits = data['profit_list'];
                var flags = data['flag_list'];

                var option = {
                    tooltip: {
                            trigger: 'axis'
                        },
                    legend: {
                            data:['收益率(%)']
                        },
                    grid: {
                            left: '3%',
                            right: '4%',
                            bottom: '3%',
                            containLabel: true
                        },
                    toolbox: {
                            feature: {
                                saveAsImage: {}
                            }
                        },
                    xAxis: {
                            type: 'category',
                            boundaryGap: false,
                            data: dates
                        },
                    yAxis: {
                            type: 'value',
                            axisLabel: {
                                formatter: '{value} %'
                            }
                        },
                    series: [
                            {
                                name:'收益率(%)',
                                type:'line',
                                data:profits,
                                markPoint: {
                                    symbolSize: 12,
                                    data: addMarkPoint(dates, profits, flags)
                                }
                            }
                        ]
                    };
                    $(window).resize(function() {
                        myChart.resize();
                    });
                    myChart.setOption(option);
             },
             error:function () {
                 alert("发生异常");
             }
    });
}

$(function() {
    var myChart = echarts.init(document.getElementById('charts'));
    var dates = rawData.map(function(item) {
            return item[0]
            });
    var profits = rawData.map(function(item) {
            return item[1]
            });
    var flags = rawData.map(function (item) {
            return item[2]
            });

    var option = {
        tooltip: {
                trigger: 'axis'
        },
        legend: {
                data:['收益率(%)']
            },
        grid: {
                left: '3%',
                right: '4%',
                bottom: '3%',
                containLabel: true
            },
        toolbox: {
                feature: {
                    saveAsImage: {}
                }
            },
        xAxis: {
                type: 'category',
                boundaryGap: false,
                data: dates
            },
        yAxis: {
                type: 'value',
                axisLabel: {
                    formatter: '{value} %'
                }
            },
        series: [
                {
                    name:'收益率(%)',
                    type:'line',
                    data:profits,
                    markPoint: {
                        symbolSize: 12,
                        data: addMarkPoint(dates, profits, flags)
                    }
                }
            ]
        };
    $(window).resize(function() {
        myChart.resize()
    });
    myChart.setOption(option);
});

function addMarkPoint(dates, profits, flags) {
    var points = [];
    for(var i=0;i<dates.length;i++){
        var buyTag = flags[i].indexOf("买入");
        var sellTag = flags[i].indexOf("卖出");
        if(buyTag !== -1){
            points.push({
                name:"买入标记点",//这个只是名称，不会显示出来
                xAxis:dates[i],
                yAxis:profits[i],
                symbol:'pin'
            })
        }else if(sellTag !== -1){
            points.push({
                name:"卖出标记点",//这个只是名称，不会显示出来
                xAxis:dates[i],
                yAxis:profits[i],
                symbol:'diamond'
            })
        }
    }
    return points;
}
