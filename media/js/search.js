var Species = loadJSRecord('Species');
var Factors = loadJSRecord('Factors');
var CellTypes = loadJSRecord('CellTypes');
var Platforms = loadJSRecord('Platforms');
var CellLines = loadJSRecord('CellLines');
var CellPops = loadJSRecord('CellPops');
var Strains = loadJSRecord('Strains');
var Conditions = loadJSRecord('Conditions');
/** 
 * Params:
 * list - list of objects to make the select out of
 * field - the field in the object used to describe the object, e.g. "name",
 *         or "antibody"--see the json
 * selectName -  how to print out the option, e.g. factor
 * 
 * Returns: a p that contains the populated select; with no duplicate entries
 */
function helper(list, field, selectName) {
    var MAXLENGTH = 50;
    var p = $D('p');
    p.appendChild($D('label', {'for':'id_'+selectName, 
			     'innerHTML':upperCase1stLtr(selectName)+":"}));
    var select = $D('select', {'name':selectName, 'id':'id_'+selectName});
    select.appendChild($D('option', {'value':'', 'innerHTML':"----"}));
    added = []
    for (var i = 0; i < list.length; i++) {
	if (list[i][field] != "" && added.indexOf(list[i][field]) == -1) {
	    var val = list[i][field];

	    //options can only be MAXLENGTH chars
	    if (val.length > MAXLENGTH) {
		val = val.substring(0, MAXLENGTH)+"...";
	    }

	    select.appendChild($D('option', {'value':list[i].id, 
					   'innerHTML':val}));
	    added.push(list[i][field]);
	}
    }
    p.appendChild(select);
    return p;
}

function init() {
    var container = $('main');
    //build the table/form
    var form = $D('form', {'action':SUB_SITE+'datasets/', 'method':'get'});
    var species = Species.all();
    var factors = Factors.all();
    var cellTypes = CellTypes.all();
    var modelDict = {'platform':Platforms.all(), 'cellline':CellLines.all(),
		     'cellpop':CellPops.all(), 'strain':Strains.all(),
		     'condition':Conditions.all()}
    form.appendChild(helper(species, 'name', 'species'));
    form.appendChild(helper(factors, 'name', 'factor'));
    form.appendChild(helper(factors, 'antibody', 'antibody'));
    form.appendChild(helper(cellTypes, 'name', 'celltype'));
    form.appendChild(helper(cellTypes, 'tissue_type', 'tissuetype'));
    //do the rest w/ the modelDict
    for (m in modelDict) {
	form.appendChild(helper(modelDict[m], 'name', m));
    }

    //submitBtn
    form.appendChild($D('input', {'type':'button', 'value':'Submit',
				'id':'submitBtn', 
				'onclick':function(){submit()}}));
    container.appendChild(form);
}

function submit() {
    var fields=['species', 'factor', 'antibody', 'celltype', 'tissuetype', 
		'platform', 'cellline', 'cellpop', 'strain', 'condition'];
    var urlStr = "";
    var first = true;
    //skip the first
    for (var i = 0; i < fields.length; i++) {
	if ($('id_'+fields[i]).value != "") {
	    if (first) {
		urlStr += fields[i]+"="+$('id_'+fields[i]).value;
		first = false;
	    } else {
		urlStr += "&"+fields[i]+"="+$('id_'+fields[i]).value;
	    }
	}
    }
    //redirect
    window.location = SUB_SITE+"datasets/?"+urlStr;
}
