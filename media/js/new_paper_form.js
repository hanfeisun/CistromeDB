function init() {
    //create the journal choices
    var cb = function(req) {
	var journals = eval("("+req.responseText+")");

	var container = $('journal');
	container.appendChild($D('label', {'for':'journal', 
					 'innerHTML':'Journal'}));
	
	var select = $D('select', {'name':'journal', 'id':'journal'})
	select.appendChild($D('option',{'value':'','innerHTML':'----------'}));
	for (var i = 0; i < journals.length; i++) {
	    select.appendChild($D('option',{'value':journals[i].id,
					  'innerHTML':journals[i].name}));
	}
	container.appendChild(select);

	var a = $D('a', {'href':SUB_SITE+"new_journal_form/",
			   'innerHTML':"add new journal"});
	container.appendChild(a);
    }
    var getJournals = 
	new Ajax.Request(SUB_SITE+"jsrecord/Journals/all/", 
			 {method:"get", onSuccess: cb});
}

/*
var containers;

function init() {
    containers = ModelFormHooks("Papers");

    fields = ["platform", "cell_type", "cell_line", "cell_pop",
	      "strain", "condition", "journal"];
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

*/
