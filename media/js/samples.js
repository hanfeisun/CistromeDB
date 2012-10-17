//jscript to handle the checkbox UI
var Samples = loadJSRecord('Samples');

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
	sampleModel.add(sampleId);
    } else {
	sampleModel.remove(sampleId);
    }
}

function masterHandler(masterChkBox) {
    for (var i = 0; i < rowSelects.length; i++) {
	rowSelects[i].checked = masterChkBox.checked;
	rowSelects[i].onclick();
    }
}

var rowSelects;
var sampleModel;
var Y;

function init() { 
    Y = YUI();
    sampleModel = new model();
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
	var resp = confirm("Are you sure you want to DELETE these papers?");
	if (resp && sampleModel.samples.length > 0) {
	    window.location = SUB_SITE+"delete_samples/?samples="+sampleModel.samples;
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
function checkRawFiles(sampleId, pg) {
    window.location = SUB_SITE+"check_raw_files/"+sampleId+"/?page="+pg;
}

function runAnalysis(sampleId, pg) {
    window.location = SUB_SITE+"run_analysis/"+sampleId+"/?page="+pg;
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
}

function destroyOverlay() {
    //show the overlay:
    var overlay = $('overlay');
    overlay.style.display="none";    
}

function showInfo(id) {
    //NOTE: in CHROME, for some reason my global vars aren't global! so models
    //is null!!
    var sample = Samples.get(id);
    
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
    p.appendChild($D('span', {innerHTML:"Sample:", className:'label'}));
    p.appendChild($D('span', {innerHTML:id, className:'value'}));
    p.appendChild($D('br'));
    p.style.paddingTop="10px";
    p.style.paddingBottom="5px";
    p.style.borderBottom="3px solid #c9c9c9";
    dialogue.appendChild(p);

    //BUILD paper info:
    if (sample.paper && sample.paper.pmid) {
	p = $D('p');
	var sp = $D('span', {innerHTML:'paper:', className:'label'});
	p.appendChild(sp);
	//build a (pubmed) link
	var a = $D('a', {innerHTML:sample.paper.reference,
			 href:'http://www.ncbi.nlm.nih.gov/pubmed?term='+sample.paper.pmid, target:"_blank"});
	a.style.display="inline";
	sp = $D('span', {className:'value'});
	sp.style.width="65%";
	sp.appendChild(a);
	p.appendChild(sp);
	//p.style.paddingBottom="10px";
	dialogue.appendChild(p);
    }

    if (sample && sample.unique_id) {
	p = $D('p');
	p.appendChild($D('span', {innerHTML:'unique id:', className:'label'}));
	//build a (geo) link
	var a = $D('a', {innerHTML:sample.unique_id, 
			 href:'http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc='+sample.paper.unique_id, target:"_blank"});
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
	if (sample[fld]) {
	    p.appendChild($D('span', {innerHTML:name+":", className:'label'}));
	    p.appendChild($D('span', {innerHTML:sample[fld].name, className:'value'}));
	    p.appendChild($D('br'));
	    dialogue.appendChild(p);
	}
    }
    //add buttons
    p = $D('p');
    //a spacer to move the buttons to the right
    p.appendChild($D('span', {className:'diagBtnSpacer'}));
    var edit = $D('input', {type:'button', value:'edit', className:'diagBtn'});
    edit.onclick = function () {editDialogue(id);}
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
    var sample = Samples.get(id);
    
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
    p.appendChild($D('span', {innerHTML:"Sample:", className:'label'}));
    p.appendChild($D('span', {innerHTML:id, className:'value'}));
    p.appendChild($D('br'));
    p.style.paddingTop="10px";
    p.style.paddingBottom="5px";
    p.style.borderBottom="3px solid #c9c9c9";
    dialogue.appendChild(p);

    //TODO: REBUILD THIS
    //BUILD paper info:
    if (sample.paper && sample.paper.pmid) {
	p = $D('p');
	var sp = $D('span', {innerHTML:'paper:', className:'label'});
	p.appendChild(sp);
	//build a (pubmed) link
	var a = $D('a', {innerHTML:sample.paper.reference,
			 href:'http://www.ncbi.nlm.nih.gov/pubmed?term='+sample.paper.pmid, target:"_blank"});
	a.style.display="inline";
	sp = $D('span', {className:'value'});
	sp.style.width="65%";
	sp.appendChild(a);
	p.appendChild(sp);
	//p.style.paddingBottom="10px";
	dialogue.appendChild(p);
    }

    if (sample && sample.unique_id) {
	p = $D('p');
	p.appendChild($D('span', {innerHTML:'unique id:', className:'label'}));

	var input = $D('input', {type:'text', id:'unique_id', value:sample.unique_id, className:'textInput'});
	sp = $D('span', {className:'value2'});
	sp.appendChild(input);
	p.appendChild(sp);
	dialogue.appendChild(p);
    }

    //add a spacer
    p = $D('p', {innerHTML:''});
    dialogue.appendChild(p);

    //build meta info: [field, name/label, django model
    var fields = [['factor', 'factor', 'Factors'],
		  ['species', 'species', 'Species'], 
		  ['cell_line', 'cell line', 'CellLines'],
		  ['cell_type', 'cell type', 'CellTypes'], 
		  ['cell_pop', 'cell pop', 'CellPops'],
		  ['tissue_type', 'tissue type', 'TissueTypes'], 
		  ['strain', 'strain', 'Strains'], 
		  ['condition','condition', 'Conditions'],
		  ['disease_state', 'disease state', 'DiseaseStates']]

    for (var i = 0; i < fields.length; i++) {
	var fld = fields[i][0];
	var name = fields[i][1];
	var mdl = fields[i][2];

	p.appendChild($D('span', {innerHTML:name+":", className:'label'}));
	var input;
	if (sample[fld]) {	    
	    input = $D('input', {type:'text', id:fld+'_id', value:sample[fld].name, className:'textInput'});
	} else {
	    input = $D('input', {type:'text', id:fld+'_id', value:'', className:'textInput'});
	}
	

	//TODO: CONDITION SHOULD NOT GET A DROPDOWN BOX!!

	//NOTE: we're going to save the ids as a hidden input--which we will
	//rely on
	var hidden = $D('input', {type:'hidden',id:fld+'_id_hidden',value:''});
	p.appendChild(hidden);

	//clear the hidden input everytime we go into the input:
	input.onfocus = function(hdn) {
	    return function(e) { hdn.value="";}
	}(hidden);

	var autocomplete = function(inputName, mmodel, hiddenIn) {
	    var map;
	    Y.use("autocomplete", "autocomplete-highlighters", function(Y) {
		Y.one("#"+inputName).plug(Y.Plugin.AutoComplete, {
		    resultHighlighter: 'phraseMatch',
		    resultTextLocator: 'name',
		    source: SUB_SITE+"swami/"+mmodel+"/?q={query}&maxResults=10",
		    //render:true
		    on:  {
			select : function(e) {
			    //SELECTED object is in e.result.raw
			    //console.log(e.result.raw);
			    hiddenIn.value = e.result.raw.id;
			},
			/* THIS is useful if we want a CB listener
			resultsChange: function(e) {
			    //Swami's results are in e.newVal[i].raw
			    map = {};
			    for (var rr = 0; rr < e.newVal.length; rr++) {
				//map names to ids
				map[e.newVal[rr].raw['name']] = e.newVal[rr].raw['id'];
			    }
			    //console.log(map);
			}
			*/
		    }
		});
	    });
	}
	autocomplete(fld+"_id", mdl, hidden);

	sp = $D('span', {className:'value2'});
	sp.appendChild(input);
	p.appendChild(sp);
	p.appendChild($D('br'));
	dialogue.appendChild(p);
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
	//check for change/new value
	for (var i = 0; i < fields.length; i++) {
	    var hiddenIn = $(fields[i][0]+"_id_hidden");
	    if (hiddenIn.value) {
		console.log(fields[i][0]);
		sample[fields[i][0]] = hiddenIn.value;
	    }
	    
	}
	var cb = function(req) {
	    console.log(req.responseText);
	    var resp = eval("("+req.responseText+")");
	    if (resp.success) {
		//refresh the page
		window.location = window.location.href;
		//console.log(req.responseText);
	    } else {
		console.log(resp.err);
	    }
	}
	//NOTE: NO ERROR CHECKING?!?!
	//NOTE: fastq_file and status must be set
	// BUG BUG BUG!!!
	sample.fastq_file_url = ""; //THIS is a bug, b/c it is overwriting!
        sample.status = "new"
	sample.save(cb);

    }
    p.appendChild(save);

    dialogue.appendChild(p);

}
