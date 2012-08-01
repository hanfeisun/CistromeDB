//jscript to handle the checkbox UI
var Datasets = loadJSRecord('Datasets');

function model() {
    //tracks the checkboxes (and corresponding datasets) which the user selects
    this.dsets = [];
    var outer = this;

    this.add = function(id) {
	//try to add the id to the list IF it is not already there
	if (outer.dsets.indexOf(id) == -1) {
	    outer.dsets.push(id);
	}
    }

    this.remove = function(id) {
	//remove the id from the list
	var tmp = outer.dsets.indexOf(id);
	if (tmp != -1) {
	    outer.dsets.splice(tmp, 1);
	}
    }
}

function clickHandler(checkbox, datasetId) {
    if (checkbox.checked) {
	dsetModel.add(datasetId);
    } else {
	dsetModel.remove(datasetId);
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

    var createBtn = $('createBtn');
    createBtn.onclick = function(event) {
	createDataset();
    }

    var deleteBtn = $('deleteBtn');
    deleteBtn.onclick = function(event) {
	//confirm
	var resp = confirm("Are you sure you want to DELETE these datasets?");
	if (resp && dsetModel.dsets.length > 0) {
	    window.location = SUB_SITE+"delete_datasets/?datasets="+dsetModel.dsets;
	}
    }

    //SET the overlay height and width:
    var overlay = $('overlay');
    overlay.style.width = document.width+"px";
    overlay.style.height = document.height+"px";
    //HIDE the overlay:
    $('overlay').style.display="none";
}
/* OBSOLETE
function downloadFile(datasetId, pg) {
    window.location = SUB_SITE+"download_file/"+datasetId+"/?page="+pg;
}

*/

//draws and handles the create new dataset dialogue
function createDataset() {
    //show the overlay:
    var overlay = $('overlay');
    overlay.style.display="block";
    
    //clear the overlay
    overlay.innerHTML = "";
    
    //create the dialogue:
    var dialogue = $D('div', {id:'overlayDialogue'});
    //NEED to create the dialogue in the current window frame-50px from top
    dialogue.style.position="relative";
    dialogue.style.top = (window.pageYOffset+ 50)+"px";
    dialogue.style.width = "25%";
    overlay.appendChild(dialogue);
    
    //build header
    var p = $D('p');
    var sp = $D('span', {innerHTML:"Create a new Dataset:",className:'label2'});
    p.appendChild(sp);
    p.style.paddingTop="10px";
    p.style.paddingBottom="5px";
    p.style.borderBottom="3px solid #c9c9c9";
    dialogue.appendChild(p);

    //add the inputs: TREATS
    p = $D('p');
    p.appendChild($D('span', {innerHTML:"Treatment Sample IDs:", className:'label2'}));
    var input = $D('input', {type:'text', id:'treats', className:'textInput'});
    sp = $D('span', {className:'value2'});
    sp.appendChild(input);
    p.appendChild(sp);
    dialogue.appendChild(p);
    //add the inputs: Conts
    p = $D('p');
    p.appendChild($D('span', {innerHTML:"Control Sample IDs:", className:'label2'}));
    input = $D('input', {type:'text', id:'conts', className:'textInput'});
    sp = $D('span', {className:'value2'});
    sp.appendChild(input);
    p.appendChild(sp);
    dialogue.appendChild(p);

    //add buttons
    p = $D('p');
    //a spacer to move the buttons to the right
    p.appendChild($D('span', {className:'diagBtnSpacer'}));
    var cancel = $D('input', {type:'button', value:'cancel', className:'diagBtn'});
    cancel.onclick = function(){destroyOverlay();}

    p.appendChild(cancel);
    var save = $D('input', {type:'button',value:'save',className:'diagBtn'});
    save.onclick = function() {
	var cb = function(req) {
	    console.log(req.responseText);
	    var resp = eval("("+req.responseText+")");
	    if (resp.success) {
		//go to the last page
		window.location = SUB_SITE+"datasets/?page=-1"
	    } else {
		console.log(resp.err);
	    }
	}
	var dset = new Datasets({id:null});
	//NOTE: WE NEED to set the new id to null so that jsrecords will know
	//that we're trying to create/save a new obj!
	dset.id = "null";
	//NOTE: NO ERROR CHECKING?!?!
	dset.treats = $('treats').value;
	dset.conts = $('conts').value;
	//NOTE: status can't be null--so we need to set it here
	dset.status = "new";
	dset.save(cb);
    }
    p.appendChild(save);
    dialogue.appendChild(p);

}

function showInfo(id) {
    //NOTE: in CHROME, for some reason my global vars aren't global! so models
    //is null!!
    var dset = Datasets.get(id);
    
    //show the overlay:
    var overlay = $('overlay');
    overlay.style.display="block";

    //clear the overlay
    overlay.innerHTML = "";

    //create the dialogue:
    var dialogue = $D('div', {id:'overlayDialogue'});
    //NEED to create the dialogue in the current window frame--50px from top
    dialogue.style.position="relative";
    dialogue.style.top = (window.pageYOffset+ 50)+"px";
    overlay.appendChild(dialogue);
    
    //build header
    var p = $D('p');
    p.appendChild($D('span', {innerHTML:"Datasets:", className:'label'}));
    p.appendChild($D('span', {innerHTML:id, className:'value'}));
    p.appendChild($D('br'));
    p.appendChild($D('br'));
    //build treats and controls
    p.appendChild($D('span', {innerHTML:"Treatment Sample IDs:", className:'label'}));
    p.appendChild($D('span', {innerHTML:dset.treats, className:'value'}));
    //p.appendChild($D('br'));
    p.appendChild($D('br'));
    p.appendChild($D('span', {innerHTML:"Control Sample IDs:", className:'label'}));
    p.appendChild($D('span', {innerHTML:dset.conts, className:'value'}));
    p.style.paddingTop="10px";
    p.style.paddingBottom="5px";
    p.style.borderBottom="3px solid #c9c9c9";
    dialogue.appendChild(p);

    

    //BUILD paper info:
    if (dset.paper && dset.paper.pmid) {
	p = $D('p');
	var sp = $D('span', {innerHTML:'paper:', className:'label'});
	p.appendChild(sp);
	//build a (pubmed) link
	var a = $D('a', {innerHTML:dset.paper.reference,
			 href:'http://www.ncbi.nlm.nih.gov/pubmed?term='+dset.paper.pmid, target:"_blank"});
	a.style.display="inline";
	sp = $D('span', {className:'value'});
	sp.style.width="65%";
	sp.appendChild(a);
	p.appendChild(sp);
	//p.style.paddingBottom="10px";
	dialogue.appendChild(p);
    }

    if (dset.paper && dset.paper.unique_id) {
	p = $D('p');
	p.appendChild($D('span', {innerHTML:'unique id:', className:'label'}));
	//build a (geo) link
	var a = $D('a', {innerHTML:dset.paper.unique_id, 
			 href:'http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc='+dset.paper.unique_id, target:"_blank"});
	var sp = $D('span', {className:'value'});
	sp.appendChild(a);
	p.appendChild(sp);
	p.style.paddingBottom="10px";
	dialogue.appendChild(p);
    }

    //add a spacer
    p = $D('p', {innerHTML:''});
    dialogue.appendChild(p);

    //build meta info: IF the name is to be different, then use the 2nd elm
    var fields = [['factor'],['species'], ['cell_line', 'cell line'],
		  ['cell_type', 'cell type'], ['cell_pop', 'cell pop'],
		  ['tissue_type', 'tissue type'], ['strain'], ['condition'],
		  ['disease_state', 'disease state']]
    for (var i = 0; i < fields.length; i++) {
	var fld = fields[i][0];
	var name = fields[i].length > 1 ? fields[i][1]:fields[i][0];
	if (dset[fld]) {
	    p.appendChild($D('span', {innerHTML:name+":", className:'label'}));
	    p.appendChild($D('span', {innerHTML:dset[fld], className:'value'}));
	    p.appendChild($D('br'));
	    dialogue.appendChild(p);
	}
    }
    //add buttons
    p = $D('p');
    //a spacer to move the buttons to the right
    p.appendChild($D('span', {className:'diagBtnSpacer'}));
    var edit = $D('input', {type:'button', value:'edit', className:'diagBtn'});
    edit.onclick = function () { editDialogue(id);};
    p.appendChild(edit);
    var close = $D('input', {type:'button',value:'close',className:'diagBtn'});
    close.onclick = function(){destroyOverlay();}
    p.appendChild(close);
    dialogue.appendChild(p);
}

//THIS is duplicated--lots of the stuff is just copied over from showInfo!
function editDialogue(id) {
    //NOTE: in CHROME, for some reason my global vars aren't global! so models
    //is null!!
    var dset = Datasets.get(id);
    
    //show the overlay:
    var overlay = $('overlay');
    overlay.style.display="block";

    //clear the overlay
    overlay.innerHTML = "";

    //create the dialogue:
    var dialogue = $D('div', {id:'overlayDialogue'});
    //NEED to create the dialogue in the current window frame--50px from top
    dialogue.style.position="relative";
    dialogue.style.top = (window.pageYOffset+ 50)+"px";
    overlay.appendChild(dialogue);
    
    //build header -- TAKEN from createDataset rather than showInfo
    var p = $D('p');
    p.appendChild($D('span', {innerHTML:"Datasets:", className:'label'}));
    p.appendChild($D('span', {innerHTML:id, className:'value'}));
    p.appendChild($D('br'));
    p.appendChild($D('br'));
    //build treats and controls
    //add the inputs: TREATS
    p.appendChild($D('span', {innerHTML:"Treatment Sample IDs:", className:'label2'}));
    var input = $D('input', {type:'text', id:'treats', value:dset.treats, className:'textInput'});
    sp = $D('span', {className:'value2'});
    sp.appendChild(input);
    p.appendChild(sp);
    dialogue.appendChild(p);
    //add the inputs: Conts
    p = $D('p');
    p.appendChild($D('span', {innerHTML:"Control Sample IDs:", className:'label2'}));
    input = $D('input', {type:'text', id:'conts', value:dset.conts, className:'textInput'});
    sp = $D('span', {className:'value2'});
    sp.appendChild(input);
    p.appendChild(sp);
    dialogue.appendChild(p);
    p.style.paddingTop="10px";
    p.style.paddingBottom="5px";
    p.style.borderBottom="3px solid #c9c9c9";
    dialogue.appendChild(p);

    //NOW back to showInfo stuff
    //BUILD paper info:
    if (dset.paper && dset.paper.pmid) {
	p = $D('p');
	var sp = $D('span', {innerHTML:'paper:', className:'label'});
	p.appendChild(sp);
	//build a (pubmed) link
	var a = $D('a', {innerHTML:dset.paper.reference,
			 href:'http://www.ncbi.nlm.nih.gov/pubmed?term='+dset.paper.pmid, target:"_blank"});
	a.style.display="inline";
	sp = $D('span', {className:'value'});
	sp.style.width="65%";
	sp.appendChild(a);
	p.appendChild(sp);
	//p.style.paddingBottom="10px";
	dialogue.appendChild(p);
    }

    if (dset.paper && dset.paper.unique_id) {
	p = $D('p');
	p.appendChild($D('span', {innerHTML:'unique id:', className:'label'}));
	//build a (geo) link
	var a = $D('a', {innerHTML:dset.paper.unique_id, 
			 href:'http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc='+dset.paper.unique_id, target:"_blank"});
	var sp = $D('span', {className:'value'});
	sp.appendChild(a);
	p.appendChild(sp);
	p.style.paddingBottom="10px";
	dialogue.appendChild(p);
    }

    //add a spacer
    p = $D('p', {innerHTML:''});
    dialogue.appendChild(p);

    //build meta info: IF the name is to be different, then use the 2nd elm
    var fields = [['factor'],['species'], ['cell_line', 'cell line'],
		  ['cell_type', 'cell type'], ['cell_pop', 'cell pop'],
		  ['tissue_type', 'tissue type'], ['strain'], ['condition'],
		  ['disease_state', 'disease state']]
    for (var i = 0; i < fields.length; i++) {
	var fld = fields[i][0];
	var name = fields[i].length > 1 ? fields[i][1]:fields[i][0];
	if (dset[fld]) {
	    p.appendChild($D('span', {innerHTML:name+":", className:'label'}));
	    p.appendChild($D('span', {innerHTML:dset[fld], className:'value'}));
	    p.appendChild($D('br'));
	    dialogue.appendChild(p);
	}
    }

    //add buttons
    p = $D('p');
    //a spacer to move the buttons to the right
    p.appendChild($D('span', {className:'diagBtnSpacer'}));
    var cancel = $D('input', {type:'button',value:'cancel',className:'diagBtn'});
    cancel.onclick = function(){destroyOverlay();}
    p.appendChild(cancel);

    p.appendChild(cancel);
    var save = $D('input', {type:'button',value:'save',className:'diagBtn'});
    save.onclick = function() {
	var cb = function(req) {
	    console.log(req.responseText);
	    var resp = eval("("+req.responseText+")");
	    if (resp.success) {
		//refresh the page
		window.location = window.location.href;
	    } else {
		console.log(resp.err);
	    }
	}
	//NOTE: NO ERROR CHECKING?!?!
	dset.treats = $('treats').value;
	dset.conts = $('conts').value;
	dset.save(cb);
    }
    p.appendChild(save);

    dialogue.appendChild(p);
}

function destroyOverlay() {
    //show the overlay:
    var overlay = $('overlay');
    overlay.style.display="none";    
}
