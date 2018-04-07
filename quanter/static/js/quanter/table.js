$(function() {
    window.onload = function () {
        console.log(testData);
        var data = [{
            'name': '中山公用',
            'code': '000685',
            'profit': 24,
            'checked': 1
        },{
            'name': '中山公用',
            'code': '000685',
            'profit': 23,
            'checked': 0
        },{
            'name': '中山公用',
            'code': '000685',
            'profit': 25,
            'checked': 1
        }];
        var item;
        $.each(data, function (i, result) {
            var nameAndCodeAndProfit = "<tr><td>"+result['name']+"</td>" + "<td>"+result['code']+"</td>" +
                "<td>"+result['profit']+"</td>";
            var checked;
            if(result['checked'] === 1) {
                checked = "<td><a><span class=\"glyphicon glyphicon-star\" aria-hidden=\"true\"></span></a></td>"
            } else {
                checked = "<td><a><span class=\"glyphicon glyphicon-star-empty\" aria-hidden=\"true\"></span></a></td>"
            }
            item = nameAndCodeAndProfit + checked + "</tr>";
            $('#table').append(item)
        })
    }
});