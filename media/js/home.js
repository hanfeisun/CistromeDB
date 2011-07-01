//create the class
var Model = ModelFactory(["papersList", "currPaper"],[]);
//Instantiate the class
var pgModel = new Model({"papersList":null, "currPaper":null});

var msg = "Search Cistrome DC";

//NOTE: an empty search might mean "all" and not none.
function init() {
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


    var resultsView = new ResultsView($('results'), pgModel);
    var paperInfoView = new PaperInfoView($('paper_info'), pgModel);
    var datasetsView = new DatasetsView($('datasets'), pgModel);
    var samplesView = new SamplesView($('samples'), pgModel);

    pgModel.papersListEvent.register(function() { resultsView.makeHTML();});
    //when a new paperList is set, clear the current paper
    pgModel.papersListEvent.register(function() {pgModel.setCurrPaper(null);});
    pgModel.currPaperEvent.register(function() { paperInfoView.makeHTML();});
    pgModel.currPaperEvent.register(function() { datasetsView.currPaperLstnr();});
    pgModel.currPaperEvent.register(function() { samplesView.currPaperLstnr();});
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
    $('all_papers').onclick = function(event) {
	getPapers("all", pgModel);
    }
    $('recent_papers').onclick = function(event) {
	getPapers("recent", pgModel);
    }

    //init the results to just the most recent
    $('recent_papers').onclick();
    //wait 1.5 secs and then show the results pane
    setTimeout(function() { results_tog.open();}, 1500);
}

/**
 * This function supports the sidebar links, e.g. get All papers or the most
 * recent papers
 */
function getPapers(type, model) {
    var cb = function(req) {
	var resp = eval("("+req.responseText+")");
	model.setPapersList(resp);
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
	var newTbl = $D('table');
	var titles = [" ", "Authors", "Title", "Journal", "Date", "Rating",
		      "Last Viewed"];
	var newTr = $D('tr', {'className': (i % 2 == 0)? "row":"altrow"});
	for (var i = 0; i < titles.length; i++) {
	    newTr.appendChild($D('th',{'innerHTML':titles[i]}));
	}
	newTbl.appendChild(newTr);
	//END: draw the title row

	var i = 0;
	var papers = (outer.model.getPapersList() == null)? []:outer.model.getPapersList();
	var fields = ["authors", "title", "journal.name", "pub_date", "", ""]
	for (; i < papers.length; i++) {
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

	    newTbl.appendChild(newTr);
	}
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
	//make the liquid cols for the tabl
	outer.container.appendChild(newTbl);
	//NOTE: this call to liquid cols MUST be AFTER we append the newTbl,
	//otherwise the widths of the elms will be 0
	var liquidCols = new LiquidCols(newTbl);
    }
}

function searchCb(req) {
    var resp = eval("("+req.responseText+")");
    pgModel.setPapersList(resp);
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
		       ['journal.name', "Journal:"], 
		       ['pub_date', 'Published:'], ['factors', 'Factors:']];
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
	tmp.appendChild($D('br'))


	for (var i = 0; i < fields2.length; i++) {
	    tmp.appendChild($D('span', {'className':'label',
			    'innerHTML':fields2[i][1]}));
	    tmp.appendChild($D('span', {'className':'value2',
			    'innerHTML':getattr(currPaper, fields2[i][0])}));
	    tmp.appendChild($D('br'));
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
