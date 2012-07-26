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

    /* OBSOLETE
    var btn = $('batchEdit');
    btn.onclick = function(event) {
	//redirect
	if (dsetModel.dsets.length > 0) { //check for empty list
	    window.location = SUB_SITE + "batch_update_datasets/?datasets="+ dsetModel.dsets+"&next="+window.location;
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
    p.appendChild($D('span', {innerHTML:dset.treatments, className:'value'}));
    //p.appendChild($D('br'));
    p.appendChild($D('br'));
    p.appendChild($D('span', {innerHTML:"Control Sample IDs:", className:'label'}));
    p.appendChild($D('span', {innerHTML:dset.controls, className:'value'}));
    p.style.paddingTop="10px";
    p.style.paddingBottom="5px";
    p.style.borderBottom="3px solid #c9c9c9";
    dialogue.appendChild(p);

    

    //BUILD paper info:
    if (dset.paper.pmid) {
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

    if (dset.paper.unique_id) {
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
    edit.disabled = "true";
    p.appendChild(edit);
    var close = $D('input', {type:'button',value:'close',className:'diagBtn'});
    close.onclick = function(){destroyOverlay();}
    p.appendChild(close);
    dialogue.appendChild(p);


}

function destroyOverlay() {
    //show the overlay:
    var overlay = $('overlay');
    overlay.style.display="none";    
}
