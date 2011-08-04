var PaperSubmissions = loadJSRecord('PaperSubmissions');

//------------------------------MODEL------------------------------

/**
 * Class: PaperSubmissionsList
 * Description:This model will contain all of the publicly submitted papers
 * 
 * @param: list - a json obj(? representation of the papersubmissions list
 * @param: currPaper - the current paper (that the user clicked)
 */
function PaperSubmissionsList(list, currPaper) {
    var outer = this;
    this.superclass = ModelFactory(['list', 'currPaper'],[]);
    this.superclass({'list':list,'currPaper':currPaper});

    this.originalList = this.list;
}

//------------------------------VIEW------------------------------

/**
 * Class: PaperSubmissions view
 * Description: Creates the table listing all of the submitted papers
 * 
 * @param: pslist - a PaperSubmissionList MODEL
 * @param: container - a div/section to draw the table
 */

//helper function, takes optional param, opts, which is a dict e.g. innerHTML; 
//tries to create the domElement, and set the innerHTML if provided
function createHelper(elmType, opts) {
    //NOTE: this has been renamed to $D in Utils.js
    return $D(elmType, opts);
}

function PaperSubmissionsView(pslist, container) {
    this.pslist = pslist;
    this.container = container;
    
    var outer = this;

    this.pslistLstnr = function() { outer.makeHTML(); }
    this.pslist.listEvent.register(this.pslistLstnr);

    //Sorting fn related things
    this.statusAscending = null; //True-ascending; false-descending

    this.statusSort = function() {
	var sortFn = function(a,b) {
	    if (a.status == b.status) {
		return 0;
	    } else if (a.status > b.status) {
		return 1;
	    } else {
		return -1;
	    }
	}

	if (outer.statusAscending) { 
	    //DESCENDING
	    outer.statusAscending = false;
	    var tmp = outer.pslist.list.sort(sortFn);
	    tmp.reverse();
	    outer.pslist.setList(tmp);
	} else { 
	    //ASCENDING
	    outer.statusAscending = true;
	    var tmp = outer.pslist.list.sort(sortFn);
	    outer.pslist.setList(tmp);	    
	}
    }

    this.makeHTML = function(pslist) {
	outer.container.innerHTML = ""; //clear the container
	var tmpSpan = createHelper("span", {'className':"section_hdr", 
					   'innerHTML':"Submitted papers:"});
	outer.container.appendChild(tmpSpan);
	
	var tbl = createHelper("table");
	var tr = createHelper("tr");
	tr.appendChild(createHelper('th', {'innerHTML':'pmid'}));
	tr.appendChild(createHelper('th', {'innerHTML':'gseid'}));
	tr.appendChild(createHelper('th', {'innerHTML':'ip addr of submitter'}));
	tr.appendChild(createHelper('th', {'innerHTML':'submitter name'}));
	tr.appendChild(createHelper('th', {'innerHTML':'comments'}));
	var th = createHelper('th', {'innerHTML':'status'});
	var img = createHelper('img');
	if (outer.statusAscending == null) {
	    img.src = SUB_SITE + "static/img/down.png";
	} else if (outer.statusAscending) {
	    img.src = SUB_SITE + "static/img/down-red.png";
	} else {
	    img.src = SUB_SITE + "static/img/up-red.png";
	}
	img.onclick = function(event) { outer.statusSort(img); }
	th.appendChild(img);
	tr.appendChild(th);
	//add a blank th
	tr.appendChild(createHelper('th', {'innerHTML':''}));

	//tr.appendChild(createHelper('th', {'innerHTML':'delete'}));

	tbl.appendChild(tr);
	outer.container.appendChild(tbl);
	
	for (var i = 0; i < outer.pslist.list.length; i++) {
	    var tr = createHelper('tr');
	    tr.appendChild(createHelper('td', {'innerHTML': 
					    outer.pslist.list[i].pmid}));
	    tr.appendChild(createHelper('td', {'innerHTML': 
					    outer.pslist.list[i].gseid}));
	    tr.appendChild(createHelper('td', {'innerHTML': 
					    outer.pslist.list[i].ip_addr}));
	    tr.appendChild(createHelper('td', {'innerHTML': 
					    outer.pslist.list[i].submitter_name}));

	    var commentTd = createHelper('td', {'innerHTML': 
					     outer.pslist.list[i].comments});
	    tr.appendChild(commentTd);

	    var statusTd = createHelper('td', {'innerHTML': 
					    outer.pslist.list[i].status});
	    tr.appendChild(statusTd);

	    var editTd = createHelper('td');
	    var editBtn = createHelper('input', {'type':'button', 
					       'value': 'edit'});
	    editBtn.onclick = function(ps, cTd, sTd, eTd, editB) {
		return function(event) {
		    //CHANGE the comment field to a textarea; status to 
		    //dropdown, and edits to save/cancel
		    var textArea = createHelper("input", {'type':"textarea",
							"value":ps.comments});
		    if (cTd.childNodes.length > 0) {
			cTd.replaceChild(textArea, cTd.childNodes[0]);
		    } else {
			cTd.appendChild(textArea);
		    }
		    
		    var opts = ["pending", "closed", "n/a"];
		    var select = createHelper("select");
		    for (var i = 0; i < opts.length; i++) {
			var opt = createHelper("option", {'value': opts[i],
						       'innerHTML': opts[i]});
			opt.selected = (opts[i] == ps.status) ?"selected":"";
			select.appendChild(opt);
		    }
		    
		    if (sTd.childNodes.length > 0) {
			sTd.replaceChild(select, sTd.childNodes[0]);
		    } else {
			sTd.appendChild(select);
		    }

		    var cancelBtn = createHelper("input", {'type':'button',
							 'value':'cancel'});
		    
		    cancelBtn.onclick = function(event) {
			//restore the ps's values
			cTd.innerHTML = ps.comments;
			sTd.innerHTML = ps.status;
			//remove the cancel and save btns
			eTd.replaceChild(editB, eTd.childNodes[0]);
			eTd.removeChild(eTd.childNodes[1]);
			//NOTE: this isn't eTd.childNodes[2], b/c the last
			//line had a side-effect!
			eTd.removeChild(eTd.childNodes[1]);
		    }
		    var saveBtn = createHelper("input", {"type":"button",
						       "value":"save"});
		    saveBtn.onclick = function(event) {
			ps.comments = cTd.childNodes[0].value;
			ps.status = sTd.childNodes[0].value;
			var cb = function(resp) {
			    //alert(resp.responseText);
			}
			tmp = PaperSubmissions.get(ps.id);
			tmp.setComments(ps.comments);
			tmp.setStatus(ps.status);
			tmp.save(cb);

			//remove the cancel and save btns
			cancelBtn.onclick();
		    }

		    var deleteBtn = createHelper("input", {"type":"button",
							 "value":"delete"});
		    deleteBtn.onclick = function(event) {
			var resp = confirm("Are you sure?");
			if (resp) {
			    //delete the row from pslist
			    var newList = outer.pslist.list.without(ps);
			    outer.pslist.setList(newList);
			    //delete the row from the db
			    tmp = PaperSubmissions.get(ps.id);
			    tmp.Delete();
			} 
		    }

		    eTd.replaceChild(cancelBtn, eTd.childNodes[0]);
		    eTd.appendChild(saveBtn);
		    eTd.appendChild(deleteBtn);
		}
	    } (outer.pslist.list[i], commentTd, statusTd, editTd, editBtn);

	    editTd.appendChild(editBtn);
	    tr.appendChild(editTd);

	    tbl.appendChild(tr);

	}
    }    
}


function init() {
    var paperSubmissionsList = 
	new PaperSubmissionsList(null, null);
    var paperSubmissionsView = 
	new PaperSubmissionsView(paperSubmissionsList, $('main'));

    paperSubmissionsList.setList(PaperSubmissions.all());
}

