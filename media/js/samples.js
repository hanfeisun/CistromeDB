//jscript to handle the checkbox UI

function model() {
    //tracks the checkboxes (and corresponding samples) which the user selects
    this.samples = [];
    var outer = this;

    this.add = function(id) {
	//try to add the id to the list IF it is not already there
	if (outer.samples.indexOf(id) == -1) {
	    outer.samples.push(id);
	}
    }

    this.remove = function(id) {
	//remove the id from the list
	var tmp = outer.samples.indexOf(id);
	if (tmp != -1) {
	    outer.samples.splice(tmp, 1);
	}
    }
}

function clickHandler(checkbox, sampleId) {
    if (checkbox.checked) {
	dsetModel.add(sampleId);
    } else {
	dsetModel.remove(sampleId);
    }
}

function masterHandler(masterChkBox) {
    for (var i = 0; i < rowSelects.length; i++) {
	rowSelects[i].checked = masterChkBox.checked;
	rowSelects[i].onclick();
    }
}

var rowSelects;
var dsetModel;

function init() {
    dsetModel = new model();
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
	if (dsetModel.samples.length > 0) { //check for empty list
	    window.location = SUB_SITE + "batch_update_samples/?samples="+ dsetModel.samples+"&next="+window.location;
	}
	//NOTE: TODO--acutally the best way to do it is to just run down the 
	//list of selected rows--i.e. generate dsetModel IN/AFTER onclick
	//and not rely on dsetModel, b/c if you hit the back btn, the 
	//item will still be checked but dsetModel is not populated.
    }

    var deleteBtn = $('deleteBtn');
    deleteBtn.onclick = function(event) {
	//confirm
	var resp = confirm("Are you sure you want to DELETE these samples?");
	if (resp && dsetModel.samples.length > 0) {
	    window.location = SUB_SITE+"delete_samples/?samples="+dsetModel.samples;
	}
    }
}

function downloadFile(sampleId, pg) {
    window.location = SUB_SITE+"download_file/"+sampleId+"/?page="+pg;
}
