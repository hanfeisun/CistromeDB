var Papers = loadJSRecord('Papers');
var Users = loadJSRecord('User');
var usersList;

//-----------------------------------MODELS------------------------------------
/**
 * Class: PapersList
 * Description: the set of papers to display
 * 
 * @param: list - list of all papers
 */
function PapersList(list) {
    this.superclass = ModelFactory(['list'],[]);
    this.superclass({'list':list});   
    this.originalList = this.list;
}
 
/**
 * Class: PapersView
 * Description: Creates the table listings of the papers
 *
 * @param: papersList - PapersList obj
 * @param: container - The div/section to draw the table 
 */
function PapersView(plist, container) {
    this.plist = plist;
    this.container = container;
    var outer = this;

    this.plistLstnr = function() { outer.makeHTML(); }
    this.plist.listEvent.register(this.plistLstnr);

    this.makeHTML = function() {
	outer.container.innerHTML = "";
	var tbl = $D('table', {'className':'datatable', 'id':'papers_table'});
	var tr = $D('tr');
	tr.appendChild($D('th', {'innerHTML':'ID'}));
	tr.appendChild($D('th', {'innerHTML':'Pubmed ID'}));
	tr.appendChild($D('th', {'innerHTML':'GSEID'}));
	tr.appendChild($D('th', {'innerHTML':'Status'}));
	tr.appendChild($D('th', {'innerHTML':'Comments'}));
	tr.appendChild($D('th', {'innerHTML':'Curator'}));
	tr.appendChild($D('th', {'innerHTML':'Action'}));
	tr.appendChild($D('th', {'innerHTML':''}));
	tbl.appendChild(tr);
	outer.container.appendChild(tbl);

	for (var i = 0; i < outer.plist.list.length; i++) {
	    var p = outer.plist.list[i];
	    tr = $D('tr');
	    //id
	    var td = $D('td');
	    td.appendChild($D('a', {'href':SUB_SITE+'paper_profile/'+p.id+'/',
			    'innerHTML':p.id}));
	    tr.appendChild(td);
	    //pmid
	    td = $D('td');
	    td.appendChild($D('a', {'href':"http://www.ncbi.nlm.nih.gov/pubmed?term="+p.pmid, 
			    'target':'_blank', 'innerHTML':p.pmid}));
	    tr.appendChild(td);
	    //gseid
	    td = $D('td');
	    td.appendChild($D('a', {'href':"http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc="+p.gseid, 
			    'target':'_blank', 'innerHTML':p.gseid}));
	    tr.appendChild(td);
	    //status -- NOTE: should we print out the long ver. of status?
	    statusTd = $D('td', {'className':p.status+'_row',
				  'innerHTML':p.status});
	    tr.appendChild(statusTd);
	    //comments
	    commentTd = $D('td', {'innerHTML':p.comments});
	    tr.appendChild(commentTd);
	    //curator
	    curratorTd = $D('td', {'innerHTML':getUser(p.user).username});
	    tr.appendChild(curratorTd);
	    //action
	    actionTd = $D('td');
	    //create an actionBtn
	    if (p.status == "imported") {
		actionTd.appendChild(makeImportBtn(p, statusTd));
	    } else if (p.status == "primed") {
		actionTd.appendChild(makeDownloadBtn(p, statusTd));
	    }
	    tr.appendChild(actionTd);
	    //edit
	    var editTd = $D('td');
	    var editBtn = $D('input', {'type':'button', 'value':'edit'});
	    
	    editBtn.onclick = function(p, cmTd, crTd, eTd, editB) {
		return function(event) {
		    //change the comment field to a textarea; currator to 
		    //dropdown and edits to save/cancel
		    var textArea = $D('input', {'type':'textarea',
					      'value':p.comments});
		    if (cmTd.childNodes.length > 0) {
			cmTd.replaceChild(textArea, cmTd.childNodes[0]);
		    } else {
			cmTd.appendChild(textArea);
		    }
		    var select = $D('select');
		    for (var i = 0; i < usersList.length; i++) {
			var opt = $D('option', {'value': usersList[i].id,
					   'innerHTML':usersList[i].username});
			opt.selected = (p.user==usersList[i].id)?"selected":"";
			select.appendChild(opt);
		    }
		    if (crTd.childNodes.length > 0) {
			crTd.replaceChild(select, crTd.childNodes[0]);
		    } else {
			crTd.appendChild(select);
		    }
		    
		    var cancelBtn = $D('input', {'type':'button', 
					       'value':'cancel'});
		    cancelBtn.onclick = function(event) {
			//restore the previous values
			cmTd.innerHTML = p.comments;
			crTd.innerHTML = getUser(p.user).username;
			//remove the cancel, save, and del btns
			eTd.replaceChild(editB, eTd.childNodes[0]);
			eTd.removeChild(eTd.childNodes[1]);
			//NOTE: this is [1] not [2]! b/c prev. line side-effect
			eTd.removeChild(eTd.childNodes[1]);
		    }
		    
		    var saveBtn = $D('input', {'type':'button', 
					     'value':'save'});
		    saveBtn.onclick = function(event) {
			p.comments = cmTd.childNodes[0].value;
			p.user = crTd.childNodes[0].value;
			var cb = function(req) {
			    //alert(req.responseText);
			}
			var tmp = Papers.get(p.id);
			tmp.setComments(p.comments);
			tmp.setUser(p.user);
			//alert(tmp.getUser());
			tmp.save(cb);
			cancelBtn.onclick();
		    }

		    var deleteBtn = $D("input", {"type":"button",
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
	    } (p, commentTd, curratorTd, editTd, editBtn);

	    editTd.appendChild(editBtn);
	    tr.appendChild(editTd);

	    tbl.appendChild(tr);
	}

    }
}

//NOTE: usersList is a global
function getUser(id) {
    for (var i = 0; i < usersList.length; i++) {
	if (usersList[i].id == id) {
	    return usersList[i];
	}
    } 
    return null;
}

function makeDownloadBtn(p, statusTd) {
    var dnldBtn = $D('input', {'type':'button', 'value':'download samples'});
    dnldBtn.onclick = function(p, statusTd, downloadBtn) {
	return function(event) {
	    var cb = function(req) {
		var resp = eval("("+req.responseText+")");
		if (resp.success) {
		    //update the status and remove the dnld btn
		    p.status = "transfer";
		    statusTd.innerHTML = p.status;
		    statusTd.className = p.status+"_row";
		    //save to the db
		    var tmp = Papers.get(p.id);
		    tmp.setStatus(p.status);
		    tmp.save();

		    downloadBtn.parentNode.removeChild(downloadBtn);
		}
	    }
	    downloadBtn.disabled=true;
	    var dnldDsets = 
	    new Ajax.Request(SUB_SITE+"download_samples/"+p.id+"/",
	    		     {method:"get", onComplete: cb});
	}
    } (p, statusTd, dnldBtn);
    return dnldBtn;
}

function makeImportBtn(p, statusTd) {
    var importBtn = $D('input', {'type':'button', 'value':'import samples'});
    importBtn.onclick = function(p, sTd, importB) {
	return function(event) {
	    //disable the btn, make the ajax call,
	    //oncb: either fail silently or update the status
	    var cb = function(req) {
		//alert(req.responseText);
		resp = eval("("+req.responseText+")");
		if (resp.success) {
		    //update the status, and make a new dnlddsets btn.
		    p.status = "primed";
		    sTd.innerHTML = p.status;
		    sTd.className = p.status+"_row";
		    
		    //save to the db
		    var tmp = Papers.get(p.id);
		    tmp.setStatus(p.status);
		    tmp.save();
		    
		    var dnldBtn = makeDownloadBtn(p, sTd);
		    importB.parentNode.replaceChild(dnldBtn,
						    importB);
		    
		}
	    }
	    importB.disabled=true;
	    var getDsets = 
	    new Ajax.Request(SUB_SITE+"import_samples/"+p.id+"/",
	    		     {method:"get", onComplete: cb});
	}
    } (p, statusTd, importBtn);
    return importBtn;
}

function init() {
    var papersList = new PapersList(null);
    var papersView = new PapersView(papersList, $('main'));
    
    usersList = Users.all();
    papersList.setList(Papers.all());

    //alert(usersList);
    
}
