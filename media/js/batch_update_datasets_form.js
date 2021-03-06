var containers;

function init(dsets) {
    containers = ModelFormHooks("Datasets");

    fields = ["factor", "platform", "species", "assembly",
	      "cell_type", "cell_line", "cell_pop",
	      "strain", "condition", "disease_state"];
    exceptions = ["cell_type", "cell_line", "cell_pop", "disease_state"]
    for (var i = 0; i < fields.length; i++) {
	var newA = document.createElement("a");
	//NOTE: we have to treat cell_type, cell_line and cell_pop differently;
	//e.g. the url is new_celltype_form
	var urlName = fields[i];
	if (exceptions.indexOf(fields[i]) != -1) {
	    urlName = fields[i].sub('_','');
	}
	var thisPage = SUB_SITE+"batch_update_datasets/?datasets="+dsets;
	newA.href = SUB_SITE+"new_"+urlName+"_form/?next="+thisPage;
	newA.innerHTML = "add new "+fields[i];
	containers[fields[i]].appendChild(newA);
    }
}

