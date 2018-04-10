function backTest() {
    var startDate = $("#startDate").val();
    var endDate = $("#endDate").val();
    var totalMoney = $("#totalMoney").val();

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
             url: "back_test_nulti_code",
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
                // alert(dates);

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
                            type: 'value'
                        },
                    series: [
                            {
                                name:'收益率(%)',
                                type:'line',
                                data:profits
                            },
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
//     $.get("backtest?code="+code+"&start="+startDate+"&end="+endDate+"&totalMoney="+totalMoney,function(data,status){
//
//         // var res = data['profitRate_day'];
//         console.log(data);
//         var opts = {
//       lines: 13 // The number of lines to draw
//     , length: 28 // The length of each line
//     , width: 14 // The line thickness
//     , radius: 42 // The radius of the inner circle
//     , scale: 1 // Scales overall size of the spinner
//     , corners: 1 // Corner roundness (0..1)
//     , color: '#000' // #rgb or #rrggbb or array of colors
//     , opacity: 0.25 // Opacity of the lines
//     , rotate: 0 // The rotation offset
//     , direction: 1 // 1: clockwise, -1: counterclockwise
//     , speed: 1 // Rounds per second
//     , trail: 60 // Afterglow percentage
//     , fps: 20 // Frames per second when using setTimeout() as a fallback for CSS
//     , zIndex: 2e9 // The z-index (defaults to 2000000000)
//     , className: 'spinner' // The CSS class to assign to the spinner
//     , top: '50%' // Top position relative to parent
//     , left: '50%' // Left position relative to parent
//     , shadow: false // Whether to render a shadow
//     , hwaccel: false // Whether to use hardware acceleration
//     , position: 'absolute' // Element positioning
//     };
//     var target = document.getElementById('charts');
//     var spinner = new Spinner(opts).spin(target);
//     spinner.spin();
//         var myChart = echarts.init(document.getElementById('charts'));
//         alert('成功了么...');
//         var dates = data['index'];
//         var profits = data['data'];
//         var option = {
//             tooltip: {
//                 trigger: 'axis'
//             },
//             legend: {
//                 data:['收益率(%)']
//             },
//             grid: {
//                 left: '3%',
//                 right: '4%',
//                 bottom: '3%',
//                 containLabel: true
//             },
//             toolbox: {
//                 feature: {
//                     saveAsImage: {}
//                 }
//             },
//             xAxis: {
//                 type: 'category',
//                 boundaryGap: false,
//                 data: dates
//             },
//             yAxis: {
//                 type: 'value'
//             },
//             series: [
//                 {
//                     name:'收益率(%)',
//                     type:'line',
//                     data:profits
//                 },
//             ]
//         };
//         $(window).resize(function() {
//             myChart.resize()
//         });
//         myChart.setOption(option);
// });
}

$(function() {
    var myChart = echarts.init(document.getElementById('charts'));
    var dates = rawData.map(function(item) {
            return item[0]
            });
    var profits = rawData.map(function(item) {
            return item[1]
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
                type: 'value'
            },
        series: [
                {
                    name:'收益率(%)',
                    type:'line',
                    data:profits
                },
            ]
        };
    $(window).resize(function() {
        myChart.resize()
    });
    myChart.setOption(option);
});
