//NOTE: very important: todo- have to change the submit btn to just a regular
//btn; onclick--compose the datasets hidden input, then submit


var PaperModel = ModelFactory(['paperId'], []);

var paperObj = new PaperModel({'paperId':null});

var replicateContainers = [];

var paperIdLstnr = function() { 
    //makes the initial "add replicate" link
    var container = $('dataset_p');
    //clear the container
    container.innerHTML = "";
    //remove any old replicates if any
    for (var i = 0; i < replicateContainers.length; i++) {
	replicateContainers[i].parentNode.removeChild(replicateContainers[i]);
    }
    replicateContainers = [];

    container.appendChild($D('label', {'innerHTML':'.'}));
    
    var tmp = $D('span', {'className':'a', 'innerHTML':'add a replicate'});
    tmp.onclick = function(event) {
	addReplicate();
    }
    container.appendChild(tmp);
}
    
paperObj.paperIdEvent.register(paperIdLstnr);

function addReplicate() {
    //tries to make a select menu for the datasets associated w/ the curr paper
    var paperId = paperObj.getPaperId();
    var cbFn = function(req) {
	//alert(req.responseText);
	var datasets = eval("("+req.responseText+")");
	var numReps = replicateContainers.length;
	var lastRep =(numReps > 0) ? 
	replicateContainers[numReps - 1] : $('dataset_p');
	var newRep = $D('p');
	replicateContainers.push(newRep);
	newRep.appendChild($D('label', {'innerHTML':'Replicate '+numReps}));
	var select = $D('select', {'name':'replicate'+numReps, 
				'id':'id_replicate'+numReps});
	var opt = $D('option', {'value':'','selected':'selected', 
			     'innerHTML':'----------'});
	select.appendChild(opt);
	for (var i = 0; i < datasets.length; i++) {
	    opt = $D('option', {'value':datasets[i].id, 
			     'innerHTML':datasets[i].gsmid});
	    select.appendChild(opt);
	}

	newRep.appendChild(select);

	//add before
	//lastRep.parentNode.insertBefore(newRep, lastRep);
	//add after
	lastRep.parentNode.insertBefore(newRep, lastRep.nextSibling);
    }
    if (paperId != null) {
	var getDatasets =new Ajax.Request(SUB_SITE+"get_datasets/"+paperId+"/",
					 {method:"get", onComplete: cbFn});
    }
}


function init(paperId) {
    var setPaper = function(pId) { 
	//sets the paperObj value
	if (pId != "") {
	    paperObj.setPaperId(pId);
	} else {
	    paperObj.setPaperId(null);
	}
    }

    if (paperId == null) {
	//need to create the paper_select
	var cbFn = function(req) {
	    var papers = eval("("+req.responseText+")");
	    //build the select
	    var container = $('paper_p');
	    container.appendChild($D('label', {'for':'id_paper', 
					     'innerHTML':'Paper:'}));
	    var select = $D('select', {'name':'paper', 'id':'id_paper'});
	    select.onchange = function(event) { setPaper(this.value); }
	    var opt = $D('option', {'value':'','selected':'selected', 
				 'innerHTML':'----------'});
	    select.appendChild(opt);

	    for (var i = 0; i < papers.length; i++) {
		opt = $D('option', {'value':papers[i].id, 
				 'innerHTML':papers[i].pmid});
		select.appendChild(opt);
	    }
	    container.appendChild(select);
	}
	var getPapers = new Ajax.Request(SUB_SITE+"jsrecord/Papers/all/",
					 {method:"get", onComplete: cbFn});
    } else {
	//set the initial paper value
	setPaper(paperId);
    }
    
}

function mySubmit() {
    var tmp = "";
    var valid = true;
    if (replicateContainers.length > 0) {
	tmp = $('id_replicate0').value;
	if ($('id_replicate0').value == "") {
	    valid = false;
	}
    }
    for (var i = 1; i < replicateContainers.length; i++) {
	tmp += ","+$('id_replicate'+i).value;
	if ($('id_replicate'+i).value == "") {
	    valid = false;
	}
    }

    if (valid) {
	//set the datasetvalue
	$('id_datasets').value = tmp;
	//submit the form
	$('rep_form').submit();
    } else {
	alert("Please select fill all replicates before submitting");
    }

    //alert(
}
