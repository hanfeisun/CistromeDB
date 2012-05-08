var PapersModel = ModelFactory(["papersList", "currPaper", "currResultsCol"],
			       ["currResultsAscending", "origPapersList"]);
var papersModel = new PapersModel({"papersList":null, "currPaper":null, 
				   "currResultsCol":null});
var pgModel = papersModel;

//var msg = "Search Cistrome PC";
var papers_msg = msg;
var allPapers = [];

var result_tog;
function init_papers() {
    var papersSearchCb = function(req) {
	var resp = eval("("+req.responseText+")");
	papersModel.setPapersList(resp);
	//save the original b/c sorting will be destructive
	papersModel.origPapersList = resp;
	//default ordering: pub_date, descending
	papersModel.setCurrResultsCol("pub_date", false);
	
	$('papers_cancelBtn').style.display="inline";
    }

    var papersSearchURL = SUB_SITE + "search_papers";
    var papersSearch = new SearchView($('papers_search'), 
				       $('papers_searchBtn'), 
				       papers_msg, papersSearchURL, 
				       papersSearchCb);


    var resultsView = new ResultsView($('results'), papersModel);
    var paperInfoView = new PaperInfoView($('paper_info'), papersModel);
    //var datasetsView = new DatasetsView($('datasets'), papersModel); //OBS?
    //var samplesView = new SamplesView($('samples'), papersModel); //OBS?

    papersModel.papersListEvent.register(function() { resultsView.makeHTML();});
    //when a new paperList is set, clear the current paper
    papersModel.papersListEvent.register(function() {papersModel.setCurrPaper(null);});
    papersModel.currPaperEvent.register(function() { paperInfoView.makeHTML();});
    //papersModel.currPaperEvent.register(function() { datasetsView.currPaperLstnr();});
    //papersModel.currPaperEvent.register(function() { samplesView.currPaperLstnr();});

    //overrider the setter fn to account for ascending fld- optional field asc
    papersModel.setCurrResultsCol = function(field, asc) {
	var oldCol = papersModel.getCurrResultsCol();
	if (oldCol == field) {
	    //toggle
	    papersModel["currResultsAscending"] = !papersModel["currResultsAscending"];
	} else {
	    papersModel["currResultsCol"] = field;
	    papersModel["currResultsAscending"] = true;
	}
	if (asc != null) {
	    papersModel["currResultsAscending"] = asc;
	}
	papersModel["currResultsColEvent"].notify();
    }

    //a fn to listen for the currCol being set, and then tries to sort the 
    //results list accordingly
    var sortResultsCol = function() {
	var field = papersModel.getCurrResultsCol();
	var asc = papersModel.getCurrResultsAscending();
	var pList = papersModel.getPapersList();
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
    papersModel.currResultsColEvent.register(sortResultsCol);

    //set the action for the cancelBtn
    var cancelBtn = $('papers_cancelBtn');
    cancelBtn.onclick = function(event) {
	//arrange the model
	papersModel.setPapersList(allPapers);
	papersModel.origPapersList = allPapers;
	//default ordering: pub_date, descending
	papersModel.setCurrResultsCol("pub_date", false);

	//reset the search fld and search btn
	$('papers_searchBtn').disabled = false;
	$('papers_search').disabled = false;
	$('papers_search').value = "";
	$('papers_search').className = "searchIn";
	cancelBtn.style.display="none";
	//HACK: to get the msg displayed, set the focus on the search, then 
	//move it to the select
	$('papers_search').focus();
	$('results').focus();
    }

    //default is ALL papers
    var allPapers = getPapers("all", papersModel);

}

/**
 * This function supports the sidebar links, e.g. get All papers or the most
 * recent papers
 */
function getPapers(type, model) {
    var returnVal = null;
    var cb = function(req) {
	var resp = eval("("+req.responseText+")");
	model.setPapersList(resp);
	//save the original b/c sorting will be destructive
	model.origPapersList = resp;
	//default ordering: pub_date, descending
	model.setCurrResultsCol("pub_date", false);
	returnVal = resp;
    }

    var call = new Ajax.Request(SUB_SITE+"front/"+type+"/", 
				{method:"get", parameters: {}, 
				 onComplete: cb, asynchronous:false});
    return returnVal
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
	iframe.height="250px";
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

	//remove __AMBIGIOUS PAPER__==paper id = 1 / 470
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
	//DO IT AGAIN! ugly!!!!
	//remove __AMBIGIOUS PAPER__==paper id = 470 
	var found = false;
	var idx = -1;
	for (var i = 0; i < papers.length && !found; i++) {
	    //alert(papers[i].id);
	    if (papers[i].id == 470) {
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

/*
function papersSearchCb(req) {
    var resp = eval("("+req.responseText+")");
    papersModel.setPapersList(resp);
    //save the original b/c sorting will be destructive
    papersModel.origPapersList = resp;
    //default ordering: pub_date, descending
    papersModel.setCurrResultsCol("pub_date", false);

    //reset the search fld and search btn
    $('searchBtn').disabled = false;
    var search = $('search');
    search.disabled = false;
    search.style.color = "#000";
}
*/

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

	if (currPaper.unique_id && currPaper.unique_id.match(/GSE\d{9}/)) {
	    tmp.appendChild($D('span', {'className':'label', 'innerHTML':"GEO Series ID:"}));
	    tmp.appendChild($D('a', {innerHTML:currPaper.unique_id, target:'_blank',
			href:'http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc='+currPaper.gseid}));
	    tmp.appendChild($D('br'));
	}

	//BUILD the DATA
	tmp.appendChild($D('span', {'className':'label', 'innerHTML':"Data:"}));
	//FOR ENCODE papers, have a link to the data
	if (currPaper['title'].match(/ENCODE.*/)) {
	    var sp =$D('span', {className:'value2'});
	    var href = (currPaper['species'] == 'Homo sapiens') ? "http://genome.ucsc.edu/ENCODE/downloads.html" : "http://genome.ucsc.edu/ENCODE/downloadsMouse.html";
	    sp.appendChild($D('a', {innerHTML:'ENCODE Link', href: href, target:'_blank'}));
	    tmp.appendChild(sp);
	}

	//NOTE: uniqueIds is an array of tuples (or the jscript equiv-arrays), 
	//where the first field is the uniqueId, and the second is the factor
	var uniqueIds = getattr(currPaper, "sample_unique_ids");
	for (var i = 0; i < uniqueIds.length; i++) {
	    var sp = $D('span', {className:'value'});
	    if (uniqueIds[i][0]) {
		if (uniqueIds[i][0].match(/GSM\d{6}/)) {
		    sp.appendChild($D('a', {innerHTML:uniqueIds[i][0], target:'_blank',
			    href:'http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc='+uniqueIds[i][0]}));
		} else {
		    sp.appendChild($D('span', {innerHTML:uniqueIds[i][0]}));
		}
	    }
	    sp.appendChild($D('span', {innerHTML:"  ("+uniqueIds[i][1]+")"}));
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

/*
TURNED off for now!
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
*/
/*
function Toggler(toggleSpan, container, isOpen) {
    //alert(toggleSpan+"\n"+container);
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
*/

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
