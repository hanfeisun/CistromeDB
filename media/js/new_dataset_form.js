
function init() {
    containers = ModelFormHooks("Datasets");

    fields = ["factor", "platform", "cell_type", "cell_line", "cell_pop",
	      "strain", "condition"];
    exceptions = ["cell_type", "cell_line", "cell_pop"]
    for (var i = 0; i < fields.length; i++) {
	var newA = document.createElement("a");
	//NOTE: we have to treat cell_type, cell_line and cell_pop differently;
	//e.g. the url is new_celltype_form
	var urlName = fields[i];
	if (exceptions.indexOf(fields[i]) != -1) {
	    urlName = fields[i].sub('_','');
	}
	newA.href = SUB_SITE+"new_"+urlName+"_form/";
	newA.innerHTML = "new "+fields[i];
	containers[fields[i]].appendChild(newA);
    }
}

