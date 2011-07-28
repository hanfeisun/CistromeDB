//jscript to handle the checkbox UI

function model() {
    //tracks the checkboxes (and corresponding datasets) which the user selects
    this.datasets = [];
    var outer = this;

    this.add = function(id) {
	//try to add the id to the list IF it is not already there
	if (outer.datasets.indexOf(id) == -1) {
	    outer.datasets.push(id);
	}
    }

    this.remove = function(id) {
	//remove the id from the list
	var tmp = outer.datasets.indexOf(id);
	if (tmp != -1) {
	    outer.datasets.splice(tmp, 1);
	}
    }
}

function clickHandler(checkbox, datasetId) {
    if (checkbox.checked) {
	datasetModel.add(datasetId);
    } else {
	datasetModel.remove(datasetId);
    }
}

function masterHandler(masterChkBox) {
    for (var i = 0; i < rowSelects.length; i++) {
	rowSelects[i].checked = masterChkBox.checked;
	rowSelects[i].onclick();
    }
}

var rowSelects;
var datasetModel;

function init() {
    datasetModel = new model();
    rowSelects = $$('input.rowSelect');
    for (var i = 0; i < rowSelects.length; i++) {
	//rowSelects[i].checked=false; --maybe i don't want this
	rowSelects[i].onclick = function(chkbox, id) {
	    return function(event) {
		clickHandler(chkbox, id);
	    }
	} (rowSelects[i], rowSelects[i].id);
    }
    
    var tmp = $('masterCheckbox');
    tmp.onclick = function(event) {
	masterHandler(tmp);
    }

    var btn = $('batchEdit');
    btn.onclick = function(event) {
	//redirect
	if (datasetModel.datasets.length > 0) { //check for empty list
	    window.location = SUB_SITE + "batch_update_datasets/?datasets="+ datasetModel.datasets+"&next="+window.location;
	}
	//NOTE: TODO--acutally the best way to do it is to just run down the 
	//list of selected rows--i.e. generate dsetModel IN/AFTER onclick
	//and not rely on dsetModel, b/c if you hit the back btn, the 
	//item will still be checked but dsetModel is not populated.
    }

    var deleteBtn = $('deleteBtn');
    deleteBtn.onclick = function(event) {
	//confirm
	var resp = confirm("Are you sure you want to DELETE these papers?");
	if (resp && datasetModel.datasets.length > 0) {
	    window.location = SUB_SITE+"delete_datasets/?datasets="+datasetModel.datasets;
	}
    }
}

function checkRawFiles(datasetId, pg) {
    window.location = SUB_SITE+"check_raw_files/"+datasetId+"/?page="+pg;
}

function runAnalysis(datasetId, pg) {
    window.location = SUB_SITE+"run_analysis/"+datasetId+"/?page="+pg;
}
