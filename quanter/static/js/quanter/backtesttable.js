function exportToExcel() {
	$("#table").table2excel({
		exclude: ".excludeThisClass",
    	name: "Worksheet Name",
    	filename: "result.xls" //do not include extension
	});
}