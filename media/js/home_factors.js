var FactorsTabModel = ModelFactory(["factors", "factorsList", "models", 
				    "dsets", "currTd", 'currSearchTerm'],[]);
var factorsModel = new FactorsTabModel({'factors':null, 'factorsList':null,
					'models':null, 'dsets':null, 
					'currTd':null, 'currSearchTerm':null});
var allFactors = [];
//NOTE: this is a global defined in home.js
var factors_msg = msg;

var drawFactorsSelect = function(list) {
    var factorsSelect = $('factorsSelect');
    //CLEAR!
    factorsSelect.innerHTML = "";
    for (var i = 0; i < list.length; i++) {
	var tmp = $D('option', {'value':list[i].id, 
				'className': ((i % 2) == 0)? 'row':'altrow',
				'innerHTML':list[i].name});
	factorsSelect.appendChild(tmp);
    }
}

function init_factors() {
    var factorsListLstnr = function() {
	var list = factorsModel.getFactorsList();
	drawFactorsSelect(list);
    }
    var jumpView= new JumpView($('factors_jump'), "getFactorsList", 
			       drawFactorsSelect);
    factorsModel.factorsListEvent.register(function() {factorsListLstnr();});
    factorsModel.factorsListEvent.register(jumpView.listener);

    //init allFactors to the set given by django in the select menu
    var fs = $('factorsSelect');
    allFactors = [];
    for (var i = 0; i < fs.options.length; i++) {
	allFactors.push({"id":fs.options[i].value, 
		    "name":fs.options[i].innerHTML});
    }
    //trigger the jumpView
    factorsModel.setFactorsList(allFactors);
    
    var factorsSearchCb = function(req) {
	var resp = eval("("+req.responseText+")");
	factorsModel.setFactorsList(resp);
	factorsModel.setCurrSearchTerm($('factors_search').value);
	$('factors_cancelBtn').style.display="inline";
    }

    var factorsSearchURL = SUB_SITE + "search_factors";
    var factorsSearch = new SearchView($('factors_search'), 
				       $('factors_searchBtn'), 
				       factors_msg, factorsSearchURL, 
				       factorsSearchCb);

    var factorsTableView = 
	new FactorsTableView($('factorsTable'), factorsModel, false);
    var factorInfoView = 
	new FactorInfoView($('factorInfo'), factorsModel);

    factorsModel.dsetsEvent.register(function() { factorsTableView.makeHTML();});
    factorsModel.currTdEvent.register(function() { factorInfoView.makeHTML();});

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
	if (factorsModel.getCurrSearchTerm()) {
	    search = factorsModel.getCurrSearchTerm();
	    var call = new Ajax.Request(SUB_SITE+"factors_view/", 
    {method:"get", parameters: {'factors':fStr, 'search':"\""+search+"\""}, 
     onComplete: factors_view_cb});
	} else {
	    var call = new Ajax.Request(SUB_SITE+"factors_view/", 
    {method:"get", parameters: {'factors':fStr}, 
     onComplete: factors_view_cb});
	}
	
    }   
    //set the action for the cancelBtn
    var cancelBtn = $('factors_cancelBtn');
    cancelBtn.onclick = function(event) {
	factorsModel.setFactorsList(allFactors);
	factorsModel.setCurrSearchTerm(null);
	//reset the search fld and search btn
	$('factors_searchBtn').disabled = false;
	$('factors_search').disabled = false;
	$('factors_search').value = "";
	$('factors_search').className = "searchIn";
	cancelBtn.style.display="none";
	//HACK: to get the msg displayed, set the focus on the search, then 
	//move it to the select
	$('factors_search').focus();
	$('factorsSelect').focus();
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
	var tmpTh = $D('th', {'innerHTML':'Cells<br/>(h = human-blue; m = mouse-red)<br/><span style=\'color:gray\'>click numbers for details</span>'});
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
			var foo=eval("("+dsets[factors[f]][mnames[i]][0]+")");
			spec = foo.species;
			if (spec && spec == "Homo sapiens") { //Human - Blue
			    th.style.backgroundColor = "#424da4";
			} else if (spec && spec == "Mus musculus") { //Mouse - Red
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
			spec = foo.species;
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
		    if (spec && spec == "Homo sapiens") { //Human - Blue
			cellTd.style.backgroundColor = "#424da4";
		    } else if (spec && spec == "Mus musculus") { //Mouse - Red
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
	    } else { //PMID is null; may be 1. ENCODE OR 2. unpublished paper
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
		} else { // unpublished data		
		
		    var span = $D('span', {innerHTML:'reference:',className:'label'});
		    td1.appendChild(span);
		    span = $D('span', {innerHTML:"paper awaiting publication", className:'reference'});
		    td1.appendChild(span);
		    td1.appendChild($D('br'));
		    tr.appendChild(td1);
		}
	    }

	    if (dset.unique_id) {
		var span = $D('span', {innerHTML:'data:',className:'label'});
		td1.appendChild(span);
		if (dset.unique_id && !dset.unique_id.match(/SRA.*/)) {
		    span = $D('span', {className:'value2'});
		    var newA = $D('a',{innerHTML:dset.unique_id, href:'http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc='+dset.unique_id, target:"_blank"});
		    span.appendChild(newA);
		    td1.appendChild(span);
		    //space
		    td1.appendChild($D('span',{innerHTML:' '}));
		}

		/*LEN: 2012-05-17 dset.unique_id = Paper.unique_id;
		  this part seems to be using samples.unique_id
		if (dset.unique_id){
		    //if (dset.unique_id.match(/.RX.[KLENE_STAR]/)) {
			span = $D('span', {className:'value2'});
			var newA = $D('a',{innerHTML:dset.unique_id, href:'http://sra.dnanexus.com/experiments/'+dset.unique_id, target:"_blank"});
			span.appendChild(newA);
			td1.appendChild(span);		    
		    } else {
			span = $D('span', {className:'value2'});
			var newA = $D('a',{innerHTML:dset.unique_id, href:'http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc='+dset.unique_id, target:"_blank"});
			span.appendChild(newA);
			td1.appendChild(span);
		    }
		}
		*/		
		td1.appendChild($D('br'));
	    }

	    if (dset.authors) {
		var span = $D('span', {innerHTML:'last author:',className:'label'});
		td1.appendChild(span);
		var authors = dset.authors.split(",");
		span = $D('span', {innerHTML:authors[authors.length - 1], className:'value2'});
		td1.appendChild(span);
		td1.appendChild($D('br'));
	    }

	    //ADD the QC measures!
	    var qc_names = [['reads','Reads QC: Pass if > 5M unique reads'], 
			    ['model','Model QC: Pass if Model and d>2*tag size'], 
			    ['folds', 'Folds QC: The ratio of peaks\' fold change > 20. We use 50% as cutoff to say whether it works or not.'], 
			    ['fdr', 'Fdr QC: Pass if > 500 peaks with q=0.01 cutoff'],
			    ['replic.',  'Replicate QC: Pass if wig corr> 0.6'],
			    ['DNase','DNase QC: Pass if overlap> 80%'], 
			    ['velcro', 'Velcro QC: Pass if peaks overlap velcro region/ all peaks. less than 10%'],
			    ['conserv', 'Conservation QC: Pass by inspecting plot'],
			    ['ceas', 'Ceas QC: depends on what kind of TF or histone mark, should be enriched at different region'],
			    ['motif','Motif QC: Pass if known motif within top 5 and zscore < -15 (from top 1K peaks)']];

	    if (dset['qc']) {
		td1.appendChild($D('span',{innerHTML:'QC:',className:'label'}));
		td1.appendChild($D('br'));
		for (var j = 0; j < dset['qc'].length; j++) {
		    var zzz = $D('span', {innerHTML:'QC'+(j+1)+' ('+qc_names[j][0]+'):', title:qc_names[j][1], className:'label'});
		    zzz.onmouseover = function(){this.style.cursor="pointer"}
		    td1.appendChild(zzz);
		    td1.appendChild($D('span', {innerHTML:dset['qc'][j],
						className:'value2'}));
		    td1.appendChild($D('br'));

		}
	    }

	    tr.appendChild(td1);

	    //other info
	    var fields = ['species', 'cell_line', 'tissue_type', 
			  'cell_type', 'cell_pop', 'strain', 'disease_state'];
	    var td2 = $D('td');
	    for (var j = 0; j < fields.length; j++) {
//		if (dset[fields[j]] && dset[fields[j]].name) {
		if (dset[fields[j]]) {
		    //replace underscores in the name
		    var fldName = fields[j].replace("_", " ");

		    td2.appendChild($D('span', {innerHTML:fldName+':',
				    className:'label'}));
		    td2.appendChild($D('span', {innerHTML:dset[fields[j]], className:'value2'}));
		    td2.appendChild($D('br'));
		}
	    }

	    //Dump the files! in a new row
	    var group1 = [['peak_file','peak file'], 
			  ['peak_xls_file', 'peak xls file'], 
			  ['summit_file', 'summit file'],
			  ['treat_bw_file', 'treatment big wig'],
			  ['cont_bw_file', 'control big wig'],
			  ['conservation_file', 'conservation file'],
			  ['ceas_file', 'ceas file'],
			  ['venn_file', 'venn diagram'],
			  ['seqpos_file', 'motif'],
			  ['cor_pdf_file', 'correlation'],
			 ]
	    for (var j = 0; j < group1.length; j++) {
		if (dset[group1[j][0]]) {
		    //replace underscores in the name
		    var fldName = group1[j][1]

		    td2.appendChild($D('span', {innerHTML:fldName+':',
				    className:'label'}));
		    //td2.appendChild($D('span', {innerHTML:'view', className:'value2'}));
		    var a = $D('a', {innerHTML:'download', href:"static/data/"+dset[group1[j][0]]});
		    var sp = $D('span', {className:'value2'});
		    sp.appendChild(a)
		    td2.appendChild(sp)
		    //td2.appendChild($D('span', {innerHTML:'import', className:'value2'}));
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
