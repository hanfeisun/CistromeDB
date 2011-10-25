
var rowSelects, model, next;

function init(model, this_pg) {
    model = model;
    next = this_pg;
    rowSelects = $$('input.rowSelect');

    var tmp = $('masterCheckbox');
    tmp.onclick = function(event) {
	for (var i=0; i < rowSelects.length; i++) {
	    rowSelects[i].checked = tmp.checked;
	}
	masterHandler(tmp);
    }

    var addBtn = $('addBtn');
    addBtn.onclick = function(event) {
	//model = Factors
	//we want to redirect to new_factor_form
	var tmp = model.toLowerCase();
	if (tmp != "species" && tmp != "assembly") {
	    tmp = tmp.substring(0, tmp.length-1);
	}
	//alert(SUB_SITE+"new_"+tmp+"_form/?next="+this_pg);
	window.location = SUB_SITE+"new_"+tmp+"_form/?next="+this_pg;
    }

    var deleteBtn = $('deleteBtn');
    deleteBtn.onclick = function(event) {
	//confirm
	var resp = confirm("Are you sure you want to DELETE these "+model+"?");
	if (resp) {
	    var tmp = [];
	    for (var i = 0; i < rowSelects.length; i++) {
		if (rowSelects[i].checked) {
		    tmp.push(rowSelects[i].id);
		}
	    }
	    var m = model;
	    if (model == "Assembly") {
		m = "Assemblies";
	    }
	    window.location = SUB_SITE+"generic_delete/"+m+"/?objects="+tmp+"&next="+next;
	}
    }
}
