//script to control how a user defines a new dataset: a new dataset is some 
//set of samples (treatments) and controls

var PaperModel = ModelFactory(['paperId'], []);

var paperObj = new PaperModel({'paperId':null});

/**
 * Function: PaperLstnrFactory
 * Description: when the paper changes, we need to generate two dialogues:
 * a dialogue to define treatments, and another to define controls.  
 * To reduce code redundancy, we define this factory
 * @param: container - html obj that holds the dialogue
 * @param: containers_list - list that will hold the pointers to the 
 * select menus this dialogue generates
 * @param: name - string "treatments" or "controls"
 */
function PaperLstnrFactory(container, containers_list, name) {
    return function() {
	//clear the container
	container.innerHTML = "";
	//remove any old samples if any
	for (var i = 0; i < containers_list.length; i++) {
	    containers_list[i].parentNode.removeChild(containers_list[i]);
	}
	containers_list.clear(); //NOTE: must use clear, rather than = []
	container.appendChild($D('label', {'innerHTML':'Define '+name+':'}));
	
	var tmp = $D('span', {'className':'a', 'innerHTML':'add a sample'});
	tmp.onclick = function(event) {
	    addSample(container, containers_list, name);
	}
	container.appendChild(tmp);
    }
}


/**
 * Function: addSample
 * Description: when we click "add a sample" in a treatment/control 
 * dialogue, tries to add another select menu in the appropriate place
 * @param: container - html obj that holds the treatment/control dialogue
 * @param: containers_list - list that will hold the pointers to the 
 * select menus this dialogue generates
 * NOTE: for the first one will add the select to the container, otherwise
 * to the last item in containers_list
 * @param: name - string "treatments" or "controls"
 */

function addSample(container, containers_list, name) {
    //tries to make a select menu for the samples associated w/ the curr paper
    var paperId = paperObj.getPaperId();
    var cbFn = function(req) {
	var samples = eval("("+req.responseText+")");
	var count = containers_list.length;
	var last = (count > 0) ? containers_list[count - 1] : container;
	var tmp = $D('p');
        containers_list.push(tmp);
	tmp.appendChild($D('label', {'innerHTML':'sample '+count}));
	var select = $D('select', {'name':name+count, 
				'id':'id_'+name+count});
	var opt = $D('option', {'value':'','selected':'selected', 
			     'innerHTML':'----------'});
	select.appendChild(opt);
	for (var i = 0; i < samples.length; i++) {
	    opt = $D('option', {'value':samples[i].id, 
			     'innerHTML':samples[i].gsmid});
	    select.appendChild(opt);
	}

	tmp.appendChild(select);

	//add before
	//last.parentNode.insertBefore(tmp, last);
	//add after
	last.parentNode.insertBefore(tmp, last.nextSibling);
    }
    if (paperId != null) {
	var getSamples =new Ajax.Request(SUB_SITE+"get_samples/"+paperId+"/",
					 {method:"get", onComplete: cbFn});
    }
}

/**
 * Function: enumerateSamples
 * Description: when user clicks "submit" btn, we want to enumerate the 
 * samples selected; returns a string of comma-separated sample ids.
 * IF one of the select menus is unselected, then the return is "" for 
 * invalid!
 * @param: containers_list - list of select menus in the dialogue
 * @param: name - treatment or control
 */
function enumerateSamples(containers_list, name) {
    var tmp = "";
    if (containers_list.length > 0) {
	tmp = $('id_'+name+'0').value;
	if ($('id_'+name+'0').value == "") {
	    return "";
	}
    }
    for (var i = 1; i < containers_list.length; i++) {
	tmp += ","+$('id_'+name+i).value;
	if ($('id_'+name+i).value == "") {
	    return "";
	}
    }
    return tmp;
}

var mySubmit;

function init(paperId) {
    var treatmentsContainers = [];
    var controlsContainers = [];
    treatmentsLstnr = PaperLstnrFactory($('treatments_p'), 
					treatmentsContainers, "treatments");
    controlsLstnr = PaperLstnrFactory($('controls_p'),
				      controlsContainers, "controls");
    paperObj.paperIdEvent.register(treatmentsLstnr);
    paperObj.paperIdEvent.register(controlsLstnr);

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
    
    //The submit fn is defined here b/c that's where treatmentContainers and
    //controlContainers have scope
    mySubmit = function() {
	var treatments = enumerateSamples(treatmentsContainers, "treatments");
	var controls = enumerateSamples(controlsContainers, "controls");
	if (treatments != "") {
	    $('id_treatments').value = treatments;
	} else {
	    alert("Please fill all treatment samples before submitting");
	    return;
	}
	//Allow controls to not be defined	
	if ((controls != "") || (controlsContainers.length == 0)) {
	    $('id_controls').value = controls;
	} else {
	    alert("Please fill all control samples before submitting");
	    return;
	}
	
	//fall through --> submit form!
	$('rep_form').submit();
    }
}
