//jscript to handle the checkbox UI

function model() {
    //tracks the checkboxes (and corresponding papers) which the user selects
    this.papers = [];
    var outer = this;

    this.add = function(id) {
	//try to add the id to the list IF it is not already there
	if (outer.papers.indexOf(id) == -1) {
	    outer.papers.push(id);
	}
    }

    this.remove = function(id) {
	//remove the id from the list
	var tmp = outer.papers.indexOf(id);
	if (tmp != -1) {
	    outer.papers.splice(tmp, 1);
	}
    }
}

function clickHandler(checkbox, paperId) {
    if (checkbox.checked) {
	paperModel.add(paperId);
    } else {
	paperModel.remove(paperId);
    }
}

function masterHandler(masterChkBox) {
    for (var i = 0; i < rowSelects.length; i++) {
	rowSelects[i].checked = masterChkBox.checked;
	rowSelects[i].onclick();
    }
}

var rowSelects;
var paperModel;

function init() {
    paperModel = new model();
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

    /*
    var btn = $('batchEdit');
    btn.onclick = function(event) {
	//redirect
	if (paperModel.papers.length > 0) { //check for empty list
	    window.location = SUB_SITE + "batch_update_papers/?papers="+ paperModel.papers;
	}
	//NOTE: TODO--acutally the best way to do it is to just run down the 
	//list of selected rows--i.e. generate dsetModel IN/AFTER onclick
	//and not rely on dsetModel, b/c if you hit the back btn, the 
	//item will still be checked but dsetModel is not populated.
    }
    */

    var deleteBtn = $('deleteBtn');
    deleteBtn.onclick = function(event) {
	//confirm
	var resp = confirm("Are you sure you want to DELETE these papers?");
	if (resp && paperModel.papers.length > 0) {
	    window.location = SUB_SITE+"delete_papers/?papers="+paperModel.papers;
	}
    }
}

function importDatasets(paperId, pg) {
    window.location = SUB_SITE+"import_datasets/"+paperId+"/?page="+pg;
}
