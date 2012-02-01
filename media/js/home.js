var Datasets = loadJSRecord('Datasets');

//create the class
var Model = ModelFactory(["papersList", "currPaper", "currResultsCol"],
			 ["currResultsAscending", "origPapersList"]);
var FactorsTabModel = ModelFactory(["factors", "models", "dsets", "currTd"], []);
//Instantiate the class
var pgModel = new Model({"papersList":null, "currPaper":null, 
			 "currResultsCol":null});
var factorsModel = new FactorsTabModel({'factors':null, 'models':null, 
					'dsets':null, 'currTd':null});
var cellsModel = new FactorsTabModel({'factors':null, 'models':null, 
				      'dsets':null, 'currTd':null});

//MENG asked me to remove this for now...but i like this so i'm just going to 
//disable it
var msg = "Search Cistrome PC";
//var msg = "                   ";

var homeCSS;
var papersTabLoad = true;
//NOTE: an empty search might mean "all" and not none.
function init() {
    /*
    var searchFld = $('search');
    searchFld.value = msg;
    searchFld.className = "searchWait"
    searchFld.onclick = function(event) {
	//IF the user is clicking for the first time
	if (this.value == msg) {
	    this.className = "searchIn";
	    this.value = "";
	}
    }

    searchFld.onblur = function(event) {
	if (this.value == "") {
	    this.className = "searchWait";
	    this.value = msg;
	}
    }
    
    var searchBtn = $('searchBtn');
    searchBtn.onclick = function(event) {
	if (searchFld.value != msg) {
	    var srch = new Ajax.Request(SUB_SITE+"search/", 
    {method:"get", parameters: {"q":searchFld.value}, onComplete: searchCb});
	    this.disabled = true;
	}
    }

    //Enter key invokes search --NOTE: this might not work across browsers
    searchFld.onkeydown = function(event) {
	if (event.keyCode == 13) {
	    searchBtn.onclick()
	}
    }
    */

    var resultsView = new ResultsView($('results'), pgModel);
    var paperInfoView = new PaperInfoView($('paper_info'), pgModel);
    var datasetsView = new DatasetsView($('datasets'), pgModel);
    var samplesView = new SamplesView($('samples'), pgModel);

    var factorsTableView = 
	new FactorsTableView($('factorsTable'), factorsModel, false);
    var factorInfoView = 
	new FactorInfoView($('factorInfo'), factorsModel);
    var cellsFactorsTableView = 
	new FactorsTableView($('cellsFactorsTable'), cellsModel, true);
    var cellsFactorInfoView = 
	new FactorInfoView($('cellsFactorInfo'), cellsModel);

    pgModel.papersListEvent.register(function() { resultsView.makeHTML();});
    //when a new paperList is set, clear the current paper
    pgModel.papersListEvent.register(function() {pgModel.setCurrPaper(null);});
    pgModel.currPaperEvent.register(function() { paperInfoView.makeHTML();});
    pgModel.currPaperEvent.register(function() { datasetsView.currPaperLstnr();});
    pgModel.currPaperEvent.register(function() { samplesView.currPaperLstnr();});
    factorsModel.dsetsEvent.register(function() { factorsTableView.makeHTML();});
    factorsModel.currTdEvent.register(function() { factorInfoView.makeHTML();});
    cellsModel.dsetsEvent.register(function() { cellsFactorsTableView.makeHTML();});
    cellsModel.currTdEvent.register(function() { cellsFactorInfoView.makeHTML();});
    
    //overrider the setter fn to account for ascending fld- optional field asc
    pgModel.setCurrResultsCol = function(field, asc) {
	var oldCol = pgModel.getCurrResultsCol();
	if (oldCol == field) {
	    //toggle
	    pgModel["currResultsAscending"] = !pgModel["currResultsAscending"];
	} else {
	    pgModel["currResultsCol"] = field;
	    pgModel["currResultsAscending"] = true;
	}
	if (asc != null) {
	    pgModel["currResultsAscending"] = asc;
	}
	pgModel["currResultsColEvent"].notify();
    }

    //a fn to listen for the currCol being set, and then tries to sort the 
    //results list accordingly
    var sortResultsCol = function() {
	var field = pgModel.getCurrResultsCol();
	var asc = pgModel.getCurrResultsAscending();
	var pList = pgModel.getPapersList();
	//NOTE: sort is destructive
	pList.sort(function(p1, p2) {
		//REMEMBER: -1 means put before, 0 put equal, 1 put after
		var val1 = getattr(p1, field);
		var val2 = getattr(p2, field);
		if (!val1 || val1.strip().length == 0) {
		    return 1;
		}
		if (!val2 || val2.strip().length == 0) {
		    return -1;
		}
		val1 = val1.toUpperCase();
		val2 = val2.toUpperCase();
		if (val1 == val2) {
		    return 0;
		} else if (val1 < val2) {
		    //-1 = put before
		    return asc ? -1 : 1;
		} else {
		    return asc ? 1 : -1;
		}
	    });
	//just re-draw the list w/o notifying the change
	resultsView.redraw();	
    }
    pgModel.currResultsColEvent.register(sortResultsCol);

    //Draw the results view
    //resultsView.makeHTML();

    //togglers
    var results_tog = new Toggler($('results_toggler'), 
				  $('results_wrapper'), false);
    var paper_info_tog = new Toggler($('paper_info_toggler'), 
				     $('paper_info_wrapper'));
    var datasets_tog = new Toggler($('datasets_toggler'), 
				   $('datasets_wrapper'), false);
    var samples_tog = new Toggler($('samples_toggler'), 
				  $('samples_wrapper'), false);

    //sidebar links
    /* These no longer exist
    $('all_papers').onclick = function(event) {
	getPapers("all", pgModel);
    }
    $('recent_papers').onclick = function(event) {
	getPapers("recent", pgModel);
    }
    */

    //tab functions
    var factorsTab = $('factorsTab');
    var papersTab = $('papersTab');
    var cellsTab = $('cellsTab');
    var factorsSect = $('factorsView');
    var papersSect = $('papersView');
    var cellsSect = $('cellsView');

    factorsTab.onclick = function(event) {
	//tab styling:
	factorsTab.className = "activeTab";
	factorsSect.style.display="block";
	papersTab.className = "tabHeader";
	papersSect.style.display="none";
	cellsTab.className = "tabHeader";
	cellsSect.style.display="none";	
    }
    factorsTab.onclick();

    papersTab.onclick = function(event) {
	//tab styling:
	papersTab.className = "activeTab";
	papersSect.style.display="block";
	factorsTab.className = "tabHeader";
	factorsSect.style.display="none";
	cellsTab.className = "tabHeader";
	cellsSect.style.display="none";	
	//Only do the following when the papersTab is clicked for 1st time
	if (papersTabLoad) {
	    //DEFAULT/only view for paper collection homepage is ALL papers
	    //TURNING THIS OFF FOR NOW! --REMEMBER TO TURN IT BACK ON!
	    getPapers("all", pgModel);
	    //wait 1.5 secs and then show the results pane
	    setTimeout(function() { results_tog.open();}, 1500);
	    papersTabLoad = false;
	}
    }

    cellsTab.onclick = function(event) {
	//tab styling:
	factorsTab.className = "tabHeader";
	factorsSect.style.display="none";
	papersTab.className = "tabHeader";
	papersSect.style.display="none";
	cellsTab.className = "activeTab";
	cellsSect.style.display="block";
    }

    var drawBtn = $('drawBtn');
    drawBtn.onclick = function(event) {
	//NOTE: i have to walk the list and see which onese are selected
	//NOTE: factor id = 0 means ALL factors; we check for this
	this.disabled = true;
	var factors = [];
	var fs = $('factorsSelect');
	for (var i = 0; i < fs.options.length; i++) {
	    if (fs.options[i].selected) {
		factors.push(fs.options[i].value);
	    }
	}
	/* THIS IS OBSOLETE!!!
	//Might be obsolete b/c we removed the all option
	if ((factors.indexOf("0") != -1) && (factors.length > 1)) {
	    //remove 0 from the list
	    factors.splice(factors.indexOf("0"), 1);
	}
	*/
	var fStr=(factors.length > 0)? factors[0]:"";
	//NOTE: limit to 10 selections
	for (var i = 1; i <factors.length && i < 10; i++) {
	    fStr += ","+factors[i];
	}
	
	var factors_view_cb = function(req) {
	    drawBtn.disabled = false;
	    var resp = eval("("+req.responseText+")");
	    factorsModel.setFactors(resp.factors);
	    factorsModel.setModels(resp.models);
	    factorsModel.setDsets(resp.dsets);
	    //CLEAR the factorInfoView
	    factorInfoView.clearHTML();
	}
	//MAKE the ajax call-
	var call = new Ajax.Request(SUB_SITE+"factors_view/", 
    {method:"get", parameters: {'factors':fStr}, 
     onComplete: factors_view_cb});
	
    }
    
    var cellsDrawBtn = $('cellsDrawBtn');
    cellsDrawBtn.onclick = function(event) {
	this.disabled = true;
	var cells = [];
	var cs = $('cellsSelect');
	for (var i = 0; i < cs.options.length; i++) {
	    if (cs.options[i].selected) {
		cells.push(cs.options[i].value);
	    }
	}
	
	//LIMIT 1
	var cStr = (cells.length > 0) ? cells[0]:"";
	/*
	for (var i = 1; i < cells.length && i < 10; i++) {
	    cStr += ","+cells[i];
	}
	*/

	var cells_view_cb = function(req) {
	    cellsDrawBtn.disabled = false;
	    var resp = eval("("+req.responseText+")");
	    cellsModel.setFactors(resp.factors);
	    cellsModel.setModels(resp.models);
	    cellsModel.setDsets(resp.dsets);
	    //CLEAR the factorInfoView
	    cellsFactorInfoView.clearHTML();
	}
	//MAKE the ajax call-
	var call = new Ajax.Request(SUB_SITE+"cells_view/", 
    {method:"get", parameters: {'cells':cStr}, 
     onComplete: cells_view_cb});

    }

    //base.css is the first [0], home.css is [1]
    homeCSS = document.styleSheets[1];
}

/**
 * This function supports the sidebar links, e.g. get All papers or the most
 * recent papers
 */
function getPapers(type, model) {
    var cb = function(req) {
	var resp = eval("("+req.responseText+")");
	model.setPapersList(resp);
	//save the original b/c sorting will be destructive
	model.origPapersList = resp;
	//default ordering: pub_date, descending
	model.setCurrResultsCol("pub_date", false);

    }

    var call = new Ajax.Request(SUB_SITE+"front/"+type+"/", 
				{method:"get", parameters: {}, 
				 onComplete: cb});
    
}

/**
 * shortens the string
 *
 * len - optional param specifying max length
 **/
function shorten(s, len) {
    if (s == null) { return "";}

    var max_length = (len) ? len : 30;
    if (s.length > max_length) {
	return s.substr(0, max_length - 3) + "...";
    } else {
	return s;
    }
}

//draws the search results
function ResultsView(container, model) {
    this.prevTr = null;
    this.minPapers = 10;
    this.model = model;
    this.container = container;
    var outer = this;
    this.makeHTML = function() {
	//clear
	outer.container.innerHTML = "";

	//BEGIN: draw the title row
	var newTbl = $D('table', {"id":"resultsTable"});
	var titles = [["status", " "], ["authors", "Authors"], 
		      ["title", "Title"], ["journal.name", "Journal"], 
		      ["pub_date", "Date"]];

	//the following are not click-sortable
	var exceptions = ["status"];
	//var newTr = $D('tr', {'className': (i % 2 == 0)? "row":"altrow"});
	var newTr = $D('tr');
	for (var i = 0; i < titles.length; i++) {
	    var newTh = $D('th');
	    var newSpan = $D('span', {'innerHTML':titles[i][1]});
	    
	    newSpan._name = titles[i][0];
	    if (exceptions.indexOf(titles[i][0]) == -1) { //NOT an exception!
		newSpan.onclick = function (field) {
		    return function (event) {
			outer.model.setCurrResultsCol(field);
		    }
		} (titles[i][0]);
		newSpan.style.cursor = "pointer";
	    }

	    newSpan._draw = function() {
		var currCol = outer.model.getCurrResultsCol();
		if (this._name != currCol) {
		    this.style.textDecoration = "none";
		} else {
		    //check ascending
		    //NOTE: THIS GETS RE-DRAWN on the notify!
		    var asc = outer.model.getCurrResultsAscending();
		    this.style.textDecoration = (asc)? "underline":"overline";
		}
	    }
	    
	    outer.model.currResultsColEvent.register(function(span) {
		    return function() { span._draw();}
		} (newSpan)
		);
	    
	    newTh.appendChild(newSpan);
	    newTr.appendChild(newTh);
	}
	newTbl.appendChild(newTr);
	//END: draw the title row

	//MOVING the papers list to a new section so we can reuse it
	outer.makePaperRows(newTbl);

	//make the liquid cols for the tabl
	var iframe = $D('iframe');
	iframe.src="about:blank";
	iframe.width="99%";
	//NOTE: the iframe MUST be appended to the body of the doc, otherwise
	//iframe.contentDocument = undefined!
	outer.container.appendChild(iframe);
	//alert(iframe.contentDocument);
	//MOZILLA needs a delay--HACK ALERT!--IT needs an alert for some reason
	if (navigator.userAgent.match(/Firefox.*/) || 
	    navigator.userAgent.match(/MSIE\ 9.0.*/)) {
	    alert("Apologies for this annoying message but this is the only way that Firefox and IE9 will correctly render this page!");
	}
	//load the css
	iframe.contentDocument.head.appendChild($D('link', {'href':SUB_SITE+"static/css/home.css", 'rel':'stylesheet', 'type':'text/css'}));
	iframe.contentDocument.body.appendChild(newTbl);
	//the next line used in redraw!
	outer.iframe = iframe;
	

	//NOTE: this call to liquid cols MUST be AFTER we append the newTbl,
	//otherwise the widths of the elms will be 0
	var liquidCols = new LiquidCols(newTbl);
    }

    //adds the paper rows to the tableElm
    this.makePaperRows = function(tableElm) {
	var currPaper = outer.model.getCurrPaper();
	var papers = (outer.model.getPapersList() == null)? []:outer.model.getPapersList();	
	var fields = ["authors", "title", "journal.name", "pub_date"]

	//remove __AMBIGIOUS PAPER__==paper id = 1
	var found = false;
	var idx = -1;
	for (var i = 0; i < papers.length && !found; i++) {
	    //alert(papers[i].id);
	    if (papers[i].id == 1) {
		found = true;
		idx = i;
	    }
	}
	if (found) {
	    papers.splice(idx, 1);
	}
	//END: remove __AMBIGUOUS PAPER__

	for (var i = 0; i < papers.length; i++) {
	    newTr = $D('tr', {'className': (i % 2 == 0)? "row":"altrow"});
	    //try to save this information so we can restore it
	    newTr.rowInfo = newTr.className;
	    newTr.onmouseover = function() {
		if (this.className != "selected") {
		    this.className = "highlight";
		    this.style.cursor = "pointer";
		}
	    }
	    newTr.onmouseout = function() {
		if (this.className != "selected") {
		    this.className = this.rowInfo;
		    this.style.cursor = "auto";
		}
	    }

	    //note: we have to curry the paper obj in.
	    newTr.onclick = function(p) {
		return function() {
		    //restore previous click
		    if (outer.prevTr != null) {
			outer.prevTr.className = outer.prevTr.rowInfo;
		    }
		    outer.prevTr = this;
		    this.className = "selected";
		    outer.model.setCurrPaper(p);
		}
	    }(papers[i]);
	    
	    //handle selected rows: check if this is the current paper
	    if (currPaper && (papers[i].id == currPaper.id)) {
		newTr.className = "selected";
		outer.prevTr = newTr;
	    }

	    //add the icons
	    var iconTd = $D('td');
	    if (papers[i].status == "complete") {
		iconTd.appendChild($D('img', {'src':SUB_SITE+"static/img/full.png", className:"icon"}));
	    } else if (papers[i].status == "downloaded") {
		iconTd.appendChild($D('img', {'src':SUB_SITE+"static/img/half.png", className:"icon"}));
	    } else {
		iconTd.appendChild($D('img', {'src':SUB_SITE+"static/img/empty.png", className:"icon"}));
	    }
	    newTr.appendChild(iconTd);
	    
	    for (var j = 0; j < fields.length; j++) {
		val = getattr(papers[i], fields[j]);
		var shrt = shorten(val);
		newTr.appendChild($D('td', {'innerHTML':shrt, '_val':val}));
	    }

	    tableElm.appendChild(newTr);
	}
	/*
	//build until min papers
	for (; i < outer.minPapers; i++) {
	    newTr = $D('tr', {'className': (i % 2 == 0)? "row":"altrow"});
	    //stub for iconTd
	    newTr.appendChild($D('td', {'innerHTML':"&nbsp;"}));
	    for (var j = 0; j < fields.length; j++) {	       
		newTr.appendChild($D('td', {'innerHTML':"&nbsp;"}));
	    }
	    newTbl.appendChild(newTr);
	}
	*/
    }

    this.redraw = function() {
	//this is a fn we use to redraw the paper rows of the table w/o
	//creating a new table--used in the sorting cols
	//var rows = $$("#resultsTable tr");
	var rows = outer.iframe.contentDocument.getElementsByTagName("tr");
       
	//always skip the first
	var currTbl;
	if (rows.length > 0) {
	    currTbl = rows[0].parentNode;
	} else {
	    return;
	}

	//BUG: before we were trying to use removeChild--skipping over the 
	//first row--the TH.  BUT that presented errors; NOW we save the th
	//and reset the innerhtml of the table
	var th = rows[0];
	currTbl.innerHTML="";
	currTbl.appendChild(th);
	outer.makePaperRows(currTbl);
    }
}

function searchCb(req) {
    var resp = eval("("+req.responseText+")");
    pgModel.setPapersList(resp);
    //save the original b/c sorting will be destructive
    pgModel.origPapersList = resp;
    //default ordering: pub_date, descending
    pgModel.setCurrResultsCol("pub_date", false);

    //reset the search btn
    $('searchBtn').disabled = false;
}

function PaperInfoView(container, model) {
    this.container = container;
    this.model = model;
    var outer = this;
    
    this.makeHTML = function() {
	//clear the container
	outer.container.innerHTML = "";
	var currPaper = outer.model.getCurrPaper();
	
	//check for null
	if (!currPaper) { return; }

	var fields1 = ["title", "authors", "abstract"];

	for (var i = 0; i < fields1.length; i++) {
	    var tmp = $D('p', {'className':'info'});
	    tmp.appendChild($D('span', {'className':'label',
			    'innerHTML':upperCase1stLtr(fields1[i])+':'}));
	    tmp.appendChild($D('span', {'className':'value',
			    'innerHTML':currPaper[fields1[i]]}));
	    outer.container.appendChild(tmp);
	}

	//[[field, label], ...]
	var fields2 = [//["pmid", "Pubmed ID:"], ["gseid", "GEO Series ID:"],
		       //['gsmids', 'Data:'],
		       ['journal.name', "Journal:"], 
		       ['pub_date', 'Published:'], //['factors', 'Factors:'],
		       ['species', 'Species:']];

	var tmp = $D('p', {'className':'info'});
	//deal with the pmid and gseid separately--they need links like this:
	//<a href="http://www.ncbi.nlm.nih.gov/pubmed?term={{p.pmid}}" target="_ blank">{{ p.pmid }}</a>
	tmp.appendChild($D('span', {'className':'label', 'innerHTML':"Pubmed ID:"}));
	tmp.appendChild($D('a', {innerHTML:currPaper.pmid, target:'_blank',
			href:'http://www.ncbi.nlm.nih.gov/pubmed?term='+currPaper.pmid}));
	tmp.appendChild($D('br'))
	
	tmp.appendChild($D('span', {'className':'label', 'innerHTML':"GEO Series ID:"}));
	tmp.appendChild($D('a', {innerHTML:currPaper.gseid, target:'_blank',
			href:'http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc='+currPaper.gseid}));
	tmp.appendChild($D('br'));
	//BUILD the GSMIDS
	tmp.appendChild($D('span', {'className':'label', 'innerHTML':"Data:"}));
	//FOR ENCODE papers, have a link to the data
	if (currPaper['title'].match(/ENCODE.*/)) {
	    var sp =$D('span', {className:'value2'});
	    var href = (currPaper['species'] == 'Homo sapiens') ? "http://genome.ucsc.edu/ENCODE/downloads.html" : "http://genome.ucsc.edu/ENCODE/downloadsMouse.html";
	    sp.appendChild($D('a', {innerHTML:'ENCODE Link', href: href, target:'_blank'}));
	    tmp.appendChild(sp);
	}

	//NOTE: GSMIDS is an array of tuples (or the jscript equiv--arrays), 
	//where the first field is the gsmid, and the second is the factor
	var gsmids = getattr(currPaper, "gsmids");
	for (var i = 0; i < gsmids.length; i++) {
	    var sp = $D('span', {className:'value'});
	    if (gsmids[i][0]) {
		sp.appendChild($D('a', {innerHTML:gsmids[i][0], target:'_blank',
			    href:'http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc='+gsmids[i][0]}));
	    } else { //try the generic_id
		sp.appendChild($D('span', {innerHTML:gsmids[i][2]}));
	    }
	    sp.appendChild($D('span', {innerHTML:"  ("+gsmids[i][1]+")"}));
	    tmp.appendChild(sp);
	}
	
	for (var i = 0; i < fields2.length; i++) {
	    var fieldVals = getattr(currPaper, fields2[i][0]);
	    if (fieldVals) {
		tmp.appendChild($D('span', {'className':'label',
				'innerHTML':fields2[i][1]}));
		if (typeof(fieldVals) == 'string') {
		    tmp.appendChild($D('span', {'className':'value2',
				    'innerHTML':fieldVals}));
		} else {
		    //assume it's an array
		    if (fieldVals.length > 1) {
			for (var j = 0; j < fieldVals.length; j++) {
			    tmp.appendChild($D('span', {'className':'value',
					    'innerHTML':fieldVals[j]}));
			}
		    } else {
			tmp.appendChild($D('span', {'className':'value2',
					'innerHTML':fieldVals}));
		    }
		}
		tmp.appendChild($D('br'));
	    }
	}
	outer.container.appendChild(tmp);
    }
}

function DatasetsView(container, model) {
    this.container = container;
    this.model = model;
    this.datasets = null;
    var outer = this;
    
    this.makeHTML = function() {
	//clear
	outer.container.innerHTML = "";
	//build the table
	var tbl = $D('table');
	var tr = $D('tr');
	tbl.appendChild(tr);

	//build the table.th
	var titles = ["GSMID", "Info", " ", "Files", "Rating"];
	for (var i = 0; i < titles.length; i++) {
	    tr.appendChild($D('th', {'innerHTML':titles[i]}));
	}

	//build the fields
	var files = [["raw_file", "Raw"], ["treatment_file", "Treatment"], 
		     ["peak_file", "Peak"], ["wig_file", "Wig"], 
		     ["bw_file", "Big Wig"]];
	var info1 = [
		     ["species.name", "Species:"],
		     ["assembly.name", "Assembly:"],		    
		     ["factor.name", "Factor:"], 
		     ["factor.antibody", "Antibody:"], 
		     ["factor.type", "Factor Type:"],
		     ["cell_type.name", "Cell Type:"],
		     ["cell_type.tissue_type", "Cell Tissue Type:"],
		     ["cell_line.name", "Cell Line:"],
		     ["cell_pop.name", "Cell Pop.:"]
		     ];
	var info2 = [
		     ["strain.name", "Strain:"],
		     ["condition.name", "Condition:"],
		     ["disease_state.name", "Disease State:"],
		     ["platform.gplid", "GPLID:"],
		     ["platform.name", "Platform Name:"],
		     ["platform.technology", "Technology:"],
		     ["platform.experiment_type", "Experiment Type:"]

		     ];

	//LIKE this:
	//	  <tr class="row">
	//	    <td>GSM1234</td>
	//	    <td><span class="value"><a href="">view</a></span>
	//	        <span class="value"><a href="">download</a></span>
	//	    </td>
	//alert(outer.datasets.length);
	for (var i = 0; i < outer.datasets.length; i++) {
	    var d = outer.datasets[i];
	    tr = $D('tr', {"className":(i % 2 == 0)? "row":"altrow"});
	    var gsmid = getattr(d, "gsmid");
	    var newA = $D('a', {innerHTML:gsmid, target:'_blank',
				href:'http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc='+gsmid});
	    tr.appendChild($D('td').appendChild(newA));

	    //build the info tds
	    var info = [info1, info2];
	    for (var z = 0; z < info.length; z++) {
		var newTd = $D('td');
		for (var j = 0; j < info[z].length; j++) {
		    var val = getattr(d, info[z][j][0], true);
		    //NOTE: null evals to false
		    if (val && val != "") {
			newTd.appendChild($D('span', {'className':'label',
					'innerHTML':info[z][j][1]}));
			newTd.appendChild($D('span', {'className':'value2',
					'innerHTML':val}));
			newTd.appendChild($D('br'));
		    }
		}
		tr.appendChild(newTd);
	    }

	    //Build the files
	    var td = $D('td');
	    for (var j = 0; j < files.length; j++) {
		var url = getattr(d, files[j][0]);
		if (url && url != "") {
		    var tmp = $D('span', {'className':'label',
					  'innerHTML':files[j][1]+":"});
		    td.appendChild(tmp);

		    tmp = $D('span', {'className':'value'});
		    tmp.appendChild($D('a', {href:'', 
				    innerHTML:'view'}));
		    tmp.appendChild($D('span', {'innerHTML':'|'}));
		    tmp.appendChild($D('a', {href:SUB_SITE+"static/"+url, 
				    innerHTML:'download'}));

		    td.appendChild(tmp);
		}
	    }
	    tr.appendChild(td);

	    //Stub for ratings
	    tr.appendChild($D('td'));

	    tbl.appendChild(tr);
	}
	outer.container.appendChild(tbl);
    }
    
    this.cb = function(req) {
	var resp = eval("("+req.responseText+")");
	outer.datasets = resp;
	outer.makeHTML();
    }

    this.currPaperLstnr = function() {
	var currPaper = outer.model.getCurrPaper();
	if (currPaper != null) {
	    var dsets = 
		new Ajax.Request(SUB_SITE+"jsrecord/Datasets/find/",
				 {method:"get",
				  parameters:{"paper":currPaper.id}, 
				  onComplete: outer.cb});
	} else {
	    //clear
	    outer.container.innerHTML = "";
	}

    }

}

function SamplesView(container, model) {
    this.container = container;
    this.model = model;
    this.samples = null;
    var outer = this;
    
    this.makeHTML = function() {
	//clear
	outer.container.innerHTML = "";
	//build the table
	var tbl = $D('table');
	var tr = $D('tr');
	tbl.appendChild(tr);

	//build the table.th
	var titles = ["Treaments", "Controls", "Files", " ", " ", " ", " ",
		      " ", " ", "Rating"];
	for (var i = 0; i < titles.length; i++) {
	    tr.appendChild($D('th', {'innerHTML':titles[i]}));
	}

	var files1 = [
		      ["treatment_file", "Treatment"],
		      ["peak_file", "Peak"],
		      ["peak_xls_file", "Peak XLS"]
		      ];

	var files2 = [
		      ["summit_file", "Summit"],
		      ["wig_file", "Wig"],
		      ["bw_file", "Big Wig"]
		      ];
	var files3 = [
		      ["bed_graph_file", "Bed Graph"],
		      ["control_bed_graph_file", "Control Bed Graph"]
		      ];
	var files4 = [
		      ["conservation_file", "Conservation"],
		      ["conservation_r_file", "Conservation R"]
		      ];
	var files5 = [
		      ["qc_file", "QC"],
		      ["qc_r_file", "QC R"]
		      ];
	var files6 = [
		      ["ceas_file", "CEAS"],
		      ["ceas_r_file", "CEAS R"]
		      ];
	var files7 = [
		      ["venn_file", "Venn Diagram"],
		      ["seqpos_file", "Motif"]
		      ];
	for (var i = 0; i < outer.samples.length; i++) {
	    var s = outer.samples[i];
	    tr = $D('tr', {"className":(i % 2 == 0)? "row":"altrow"});
	    //Treatments & Controles
	    tr.appendChild($D('td', {'innerHTML':s.treatments}));
	    tr.appendChild($D('td', {'innerHTML':s.controls}));

	    //Build the files
	    var ls = [files1, files2, files3, files4, files5, files6, files7];
	    for (var z = 0; z < ls.length; z++) {
		var files = ls[z];
		var td = $D('td');
		for (var j = 0; j < files.length; j++) {
		    var url = getattr(s, files[j][0]);
		    if (url && url != "") {
			var tmp = $D('span', {'className':'label',
					      'innerHTML':files[j][1]+":"});
			td.appendChild(tmp);
			
			tmp = $D('span', {'className':'value'});
			tmp.appendChild($D('a', {href:'', 
					innerHTML:'view'}));
			tmp.appendChild($D('span', {'innerHTML':'|'}));
			tmp.appendChild($D('a', {href:SUB_SITE+"static/"+url, 
					innerHTML:'download'}));
			
			td.appendChild(tmp);
		    }
		}
		tr.appendChild(td);
	    }


	    //stubb sample ratings
	    tr.appendChild($D('td'));

	    tbl.appendChild(tr);
	}

	outer.container.appendChild(tbl);
    }

    this.cb = function(req) {
	var resp = eval("("+req.responseText+")");
	outer.samples = resp;
	outer.makeHTML();
    }

    this.currPaperLstnr = function() {
	var currPaper = outer.model.getCurrPaper();
	if (currPaper != null) {
	    var samples = 
		new Ajax.Request(SUB_SITE+"jsrecord/Samples/find/",
				 {method:"get", 
				  parameters:{"paper":currPaper.id}, 
				  onComplete: outer.cb});
	} else {
	    //clear
	    outer.container.innerHTML = "";
	}
	
    }
}

function Toggler(toggleSpan, container, isOpen) {
    this.toggleSpan = toggleSpan;
    this.isOpen = (isOpen == null) ? true : isOpen;
    this.container = container;
    var outer = this;

    this.close = function() {
	Effect.SlideUp(outer.container);
	outer.toggleSpan.innerHTML = "+";
	outer.isOpen = false;
    }

    this.open = function() {
	Effect.SlideDown(outer.container);
	outer.toggleSpan.innerHTML = "-";
	outer.isOpen = true;
    }

    this.toggleSpan.onclick = function() {
	if (outer.isOpen) {
	    //close
	    outer.close();
	} else {
	    //open
	    outer.open();
	}
    }

    //init the display
    if (this.isOpen) {
	this.open();
    } else {
	this.close();
    }

}

//Liquid Columns class: -- THIS might be reusable...
function LiquidCols(table) {
    this.table = table;
    //get the table's th's
    this.ths = this.table.getElementsByTagName('th');
    this.trs = this.table.getElementsByTagName('tr');

    //NOTE: tds[0] is an array of all of the td elms in the 0th column
    var tmp = [];
    for (var i = 0; i < this.trs.length; i++) {
	tmp.push(this.trs[i].getElementsByTagName('td'));
    }
    //transpose tmp to get tds
    this.tds = [];
    //init the transpose w/ empty rows
    for (var i = 0; i < this.ths.length; i++) {
	this.tds.push([]);
    }
    for (var r = 0; r < tmp.length; r++) {
	var foo = tmp[r];
	for (var c = 0; c < foo.length; c++) {
	    this.tds[c].push(tmp[r][c]);
	}
    }

    this.widths = [];
    var outer = this;
    
    this.startX = 0;
    this.curr = null;
    this.scale = 7.0;

    this.table.onmouseup = function(event) {
	Event.stopObserving(outer.table, "mousemove");
	//sett the new width--not pretty but hey.
	if (outer.curr) {
	    outer.widths[outer.curr] = outer.ths[outer.curr].getWidth();
	}
    }

    for (var i = 0; i < this.ths.length; i++) {
	var tmp = $D('span', {innerHTML:"|"});
	tmp.style['float'] = "right";
	tmp.style['cursor'] = "pointer";
	
	tmp.onmousedown = function(i) {
	    return function(event) {
		outer.startX = event.x;
		outer.curr = i;
		
		outer.table.observe("mousemove", function(event) {
			outer.ths[i].style.width = 
			    outer.widths[i] + (event.x - outer.startX) +"px";
			
			//shorten the td's text content to fit the new width
			for (var z = 0; z < outer.tds[i].length; z++) {
			    //we store the full string in the td's _val attrib
			    if (outer.tds[i][z]['_val']) {
				var max=Math.round(outer.tds[i][z].getWidth() /
						   outer.scale);
				outer.tds[i][z].innerHTML = 
				    shorten(outer.tds[i][z]['_val'], max);
			    }
			}
		    });
	    }
	}(i);
	this.ths[i].appendChild(tmp);
	this.widths.push(this.ths[i].getWidth());
    }
}

//Factors Tab Views
function FactorsTableView(container, model, factorsAsRow) {
    this.prevTd = null;
    this.container = container;
    this.model = model;
    this.factorsAsRow = factorsAsRow;//boolean: print factors as rows: if false, print as cols--default: false--FACTOR view: false, cell view: true
    var outer = this;
    //How many columns before we rotate
    var maxCols = 15;
    
    //Function to draw the factors table
    this.makeHTML = function() {
	//clear the factors table
	outer.container.innerHTML = "";
	var factors = outer.model.getFactors();
	var mnames = outer.model.getModels();
	var dsets = outer.model.getDsets();

	var fields = (outer.factorsAsRow)? [mnames,factors]:[factors,mnames];
	//BUILD the table!
	var tbl = $D('table');
	var tr = $D('tr');	
	//TABLE HEADER
	var tmpTh = $D('th', {'innerHTML':'Cells<br/>(h = human; m = mouse)<br/><span style=\'color:gray\'>click numbers for details</span>'});
	tr.appendChild(tmpTh);
	for (var i = 0; i < fields[0].length; i++) {
	    var th = $D('th', {'innerHTML':fields[0][i]});
	    th.className = "no_r2th";
	    tr.appendChild(th);

	    //HACK: color in the TH for cellsView--
	    if(outer.factorsAsRow) {
		var found = false;
		//find the first factor that hits
		for (var f = 0; f < factors.length && !found; f++) {
		    if (dsets[factors[f]][mnames[i]] && 
			dsets[factors[f]][mnames[i]].length > 0) {
			found = true;
			//TAKE THE FIRST SPECIES-- this seems to be ok!
			var foo =eval("("+dsets[factors[f]][mnames[i]][0]+")");
			spec = foo.species.id;
			if (spec && spec == 1) { //Human - Blue
			    th.style.backgroundColor = "#424da4";
			} else if (spec && spec == 2) { //Mouse - Red
			    th.style.backgroundColor = "#a64340";
			}

		    }
		}
	    }
	}
	tbl.appendChild(tr);

	//BUILD rest of table
	var td;
	for (var i = 0; i < fields[1].length; i++) {
	    tr = $D('tr');
	    //first item is the model name
	    var cellTd =$D('td',{'innerHTML':fields[1][i],'className':'no_r2td'});
	    tr.appendChild(cellTd);

	    var spec = null;
	    for (var j = 0; j < fields[0].length; j++) {
		td = $D('td', {'className':'no_r2td'});
		var m = (outer.factorsAsRow)? mnames[j]:mnames[i];
		var fact = (outer.factorsAsRow)? factors[i]:factors[j];
		if (dsets[fact] && dsets[fact][m]) {
		    //add to species list
		    if (dsets[fact][m].length > 0) {
			//TAKE THE FIRST SPECIES-- this seems to be ok!
			var foo =eval("("+dsets[fact][m][0]+")");
			spec = foo.species.id;
		    }

		    td.innerHTML = dsets[fact][m].length;
		    //NICE TRICK!
		    td["_data"] = {'factor':fact,
				   'mname': m,
				   'dsets': dsets[fact][m]};
		    
		    td.onclick = function(t) {
			return function(event) {
			    outer.model.setCurrTd(t);
			    //VIOLATION OF MVC HERE!!!
			    t.style.backgroundColor="#0e162a";//"#cad0fc";
			    t.style.color="#fff";
			    if (outer.prevTd) {
				//clear prev
				outer.prevTd.style.backgroundColor = "#fff";
				outer.prevTd.style.color="#000";
			    }
			    outer.prevTd = t;
			    //Jump to the factorInfoTable
			    window.location.href = (outer.factorsAsRow) ? "#cellsFactorInfo" : "#factorInfo";
			}
		    }(td);
		    //DOING the mouse over events here rather than in css
		    //to only highlight the filled-in boxes!
		    td.onmouseover = function(event) {
			if (outer.prevTd != this) {
			    this.style.cursor = "pointer";
			    this.style.backgroundColor = "#cad0fc";
			}
		    }
		    td.onmouseout = function(event) {
			if (outer.prevTd != this) {
			    this.style.cursor = "default";
			    this.style.backgroundColor = "#fff";
			}
		    }
		    
		} else {
		    td.innerHTML = "";
		}
		
		//HACK: only color if factorsView--i.e. factorsAsRow is false
		if (!outer.factorsAsRow) {
		    if (spec && spec == 1) { //Human - Blue
			cellTd.style.backgroundColor = "#424da4";
		    } else if (spec && spec == 2) { //Mouse - Red
			cellTd.style.backgroundColor = "#a64340";
		    }
		}
		    
		tr.appendChild(td);
	    }

	    tbl.appendChild(tr);
	}
	 
	outer.container.appendChild(tbl);
    }
}

function FactorInfoView(container, model) {
    this.container = container;
    this.model = model;
    var outer = this;
    
    this.makeHTML = function() {
	outer.clearHTML();
	//NOTE:getCurrTd returns the table CELL!--we stored it under _data
	var data = outer.model.getCurrTd()['_data'];
	//make tag line
	var hdr = $D('header');
	hdr.appendChild($D('span', {innerHTML:'Factor:', className:'label'}));
	hdr.appendChild($D('span', {innerHTML:data.factor, className:'value2'}));
	//hdr.appendChild($D('span', {innerHTML:data.model+':', className:'label'}));
	hdr.appendChild($D('span', {innerHTML:'Cells:', className:'label'}));
	hdr.appendChild($D('span', {innerHTML:data.mname, className:'value2'}));
	outer.container.appendChild(hdr);

	//make the table:
	
	var tbl = $D('table');
	for (var i = 0; i < data.dsets.length; i++) {
	    //NOTE: when we do our trick, by storing the data in the dom el
	    //IT gets stored as a string....to get the jscript back we have to
	    //evaluate the string
	    var dset = eval("("+data.dsets[i]+")");
	    var tr = $D('tr');
	    var td1 = $D('td');

	    if (dset.pmid) {
		var span = $D('span', {innerHTML:'reference:',className:'label'});		      
		td1.appendChild(span);
		var p = $D('p', {className:'reference'});
		
		//CLEAN REFERENCE: double dots
		var ref = "";
		if (dset.reference) {
		    var refAr = dset.reference.split(".");
		    for (var jj = 0; jj < refAr.length; jj++) {
			//alert("$"+refAr[jj].strip()+"#");
			if (refAr[jj].strip().length != 0) {
			    ref += refAr[jj] + ".";
			}
		    }
		}

		var newA = $D('a',{innerHTML:ref, href:'http://www.ncbi.nlm.nih.gov/pubmed?term='+dset.pmid, target:"_blank"});
		p.appendChild(newA);
		td1.appendChild(p);
		//td1.appendChild($D('br'));

		//MAKING the reference line span the columns
		td1.colSpan = "2";
		tr.appendChild(td1);
		//remove the tr's bottom border
		tr.style.borderBottom = "0px";
		td1 = $D('td');
		tbl.appendChild(tr);
		tr = $D('tr');
		//remove the new tr's top border
		tr.style.borderTop = "0px";
	    }

	    if (dset.gseid || dset.gsmid) {
		var span = $D('span', {innerHTML:'data:',className:'label'});
		td1.appendChild(span);
		if (dset.gseid) {
		    span = $D('span', {className:'value2'});
		    var newA = $D('a',{innerHTML:dset.gseid, href:'http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc='+dset.gseid, target:"_blank"});
		    span.appendChild(newA);
		    td1.appendChild(span);
		    //space
		    td1.appendChild($D('span',{innerHTML:' '}));
		}
		if (dset.gsmid){
		    span = $D('span', {className:'value2'});
		    var newA = $D('a',{innerHTML:dset.gsmid, href:'http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc='+dset.gsmid, target:"_blank"});
		    span.appendChild(newA);
		    td1.appendChild(span);
		}
		td1.appendChild($D('br'));
	    }

	    //hack for ENCODE data
	    if (dset.reference && dset.reference.match(/ENCODE.*/)) {
		var span = $D('span', {innerHTML:'reference:',className:'label'});
		td1.appendChild(span);
		
		span = $D('span', {innerHTML:dset.reference, className:'value2'});
		td1.appendChild(span);
		//td1.appendChild($D('br'));
		//MAKING the reference line span the columns
		td1.colSpan = "2";
		tr.appendChild(td1);
		//remove the tr's bottom border
		tr.style.borderBottom = "0px";
		td1 = $D('td');
		tbl.appendChild(tr);
		tr = $D('tr');
		//remove the new tr's top border
		tr.style.borderTop = "0px";

		//Build the data section
		td1 = $D('td');
		span = $D('span', {innerHTML:'data:', className:'label'});
		td1.appendChild(span);
		span = $D('span', {className:'value2'});
		//NOTE: 1 = human, 2 = mouse
		var href = (dset.species.id == 1) ? "http://genome.ucsc.edu/ENCODE/downloads.html" : "http://genome.ucsc.edu/ENCODE/downloadsMouse.html";
		span.appendChild($D('a', {innerHTML:'ENCODE Link', href:href, target:'_blank'}));
		td1.appendChild(span);
		td1.appendChild($D('br'));
		tr.appendChild(td1);
	    }
		

	    if (dset.authors) {
		var span = $D('span', {innerHTML:'last author:',className:'label'});
		td1.appendChild(span);
		var authors = dset.authors.split(",");
		span = $D('span', {innerHTML:authors[authors.length - 1], className:'value2'});
		td1.appendChild(span);
		td1.appendChild($D('br'));
	    }

	    tr.appendChild(td1);

	    //other info
	    var fields = ['species', 'cell_line', 'tissue_type', 
			  'cell_type', 'cell_pop', 'strain', 'disease_state'];
	    var td2 = $D('td');
	    for (var j = 0; j < fields.length; j++) {
		if (dset[fields[j]] && dset[fields[j]].name) {
		    //replace underscores in the name
		    var fldName = fields[j].replace("_", " ");

		    td2.appendChild($D('span', {innerHTML:fldName+':',
				    className:'label'}));
		    td2.appendChild($D('span', {innerHTML:dset[fields[j]].name, className:'value2'}));
		    td2.appendChild($D('br'));
		}
	    }
	    tr.appendChild(td2);
	    tbl.appendChild(tr);
	}
	outer.container.appendChild(tbl);
    }
    
    this.clearHTML = function() {
	outer.container.innerHTML = "";
    }
}

/* getStyle- fn to get the COMPUTED css value of an element 
 * ref: http://robertnyman.com/2006/04/24/get-the-rendered-style-of-an-element/
 * NOTE: the elm must be part of the DOM (e.g. appended somewhere on the tree!)
 */
function getStyle(oElm, strCssRule){
    var strValue = "";
    if(document.defaultView && document.defaultView.getComputedStyle){
	strValue = document.defaultView.getComputedStyle(oElm, "").getPropertyValue(strCssRule);
    }
    else if(oElm.currentStyle){
	strCssRule = strCssRule.replace(/\-(\w)/g, function (strMatch, p1){
		return p1.toUpperCase();
	    });
	strValue = oElm.currentStyle[strCssRule];
    }
    return strValue;
}

/*given a css, returns the css rule using the selector, e.g. selector="a:hover"
 */
function getStyleRule(css, selector) {
    var rules = css.cssRules ? css.cssRules: css.rules;
    for (var i = 0; i < rules.length; i++){
	if(rules[i].selectorText == selector) { 
	    return rules[i];
	}
    }
    return null;
}
