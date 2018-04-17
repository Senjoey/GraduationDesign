function changeFilterTime() {
    var startDate = $("#poolStartDate").val();
    var endDate = $("#poolEndDate").val();

    window.location.href = "/quanter/change_filter_time?start=" + startDate +"&end=" + endDate;
}