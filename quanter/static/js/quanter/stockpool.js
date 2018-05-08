function changeFilterYear() {
    var startYear = $("#poolStartYear").val();
    var endYear = $("#poolEndYear").val();

    var start = parseInt(startYear);
    var end = parseInt(endYear);
    if(end < start) {
        alert("结束年份不能小于开始年份！");
        return;
    }
    window.location.href = "/quanter/change_filter_year?start=" + startYear +"&end=" + endYear;
}

function changeFilterDate() {
    var startDate = $("#poolStartDate").val();
    var endDate = $("#poolEndDate").val();

    // var arys1 = startDate.split('-');
    // var sdate = new Date(arys1[0],parseInt(arys1[1]-1),arys1[2]);
    // var arys2 = endDate.split('-');
    // var edate = new Date(arys2[0],parseInt(arys2[1]-1),arys2[2]);
    // if(sdate > edate) {
    //     alert("结束日期不能小于开始日期！");
    //     return;
    // }
    if(!validateDate(startDate, endDate)) {
        alert("结束日期不能小于开始日期！");
        return;
    }
    window.location.href = "/quanter/change_filter_date?start=" + startDate + "&end=" + endDate;
}

function validateDate(startDate, endDate) {
    var arys1 = startDate.split('-');
    var sdate = new Date(arys1[0],parseInt(arys1[1]-1),arys1[2]);
    var arys2 = endDate.split('-');
    var edate = new Date(arys2[0],parseInt(arys2[1]-1),arys2[2]);
    if(sdate > edate) {
        return false;
    } else {
        return true;
    }
}