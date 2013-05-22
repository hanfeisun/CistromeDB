
var rowSelects;
var model = null;
var next = null;

function masterHandler(masterChkBox) {
    for (var i = 0; i < rowSelects.length; i++) {
	rowSelects[i].checked = masterChkBox.checked;
	//rowSelects[i].onclick();
    }
}

function init(mdl, this_pg) {
    model = loadJSRecord(mdl);
    next = this_pg;
    rowSelects = $$('input.rowSelect');

    var tmp = $('masterCheckbox');
    tmp.onclick = function(event) {
	for (var i=0; i < rowSelects.length; i++) {
	    rowSelects[i].checked = tmp.checked;
	}
	masterHandler(tmp);
    }
    var createBtn = $('createBtn');
    createBtn.onclick = function(event) {
	createEditDialogue(null);
    }

    var deleteBtn = $('deleteBtn');
    deleteBtn.onclick = function(event) {
	//confirm
	var resp = confirm("Are you sure you want to DELETE these "+mdl+"?");
	if (resp) {
	    var tmp = [];
	    for (var i = 0; i < rowSelects.length; i++) {
		if (rowSelects[i].checked) {
		    tmp.push(rowSelects[i].id);
		}
	    }
	    var m = mdl;
	    if (mdl == "Assembly") {
		m = "Assemblies";
	    }
	    
	    if (tmp.length > 0) { //CHECK for the empty list
		window.location = SUB_SITE+"generic_delete/"+m+"/?objects="+tmp+"&next="+next;
	    }
	}
    }
    
    //SET the overlay height and width:
    var overlay = $('overlay');
    overlay.style.width = document.width+"px";
    overlay.style.height = document.height+"px";
    //HIDE the overlay:
    $('overlay').style.display="none";

    //Cookie enabled drop-down:
    Cookie.init({name: 'fieldsView', expires: 0});
    //add functionality to fieldTypes select
    var fieldType = $('fieldType');
    fieldType.onchange = function(e) {
	//Set the cookie
	Cookie.setData("fieldType", this.value);
	//reload page:
	window.location = SUB_SITE+"fieldsView/";
    }

    //Search
    var searchFld = $('searchFld');
    var searchBtn = $('searchBtn');
    var cancelBtn = $('cancelBtn');
    var searchView = new SearchView(searchFld, searchBtn, cancelBtn, 
				    "Search by name");

}

//Creates the dialogue--if id is not null then tries to edit
//Only allows setting the name
function createEditDialogue(id) {
    //NOTE: in CHROME, for some reason my global vars aren't global! so models
    //is null!!
    var obj = (id == null)? new model({id:null}) : model.get(id);
    
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
    dialogue.style.left = "100px";
    overlay.appendChild(dialogue);
    
    //build header
    var p = $D('p');
    p.appendChild($D('span', {innerHTML:model.className+":", className:'label'}));
    p.appendChild($D('span', {innerHTML:id, className:'value'}));
    p.style.paddingTop="10px";
    p.style.borderBottom="3px solid #c9c9c9";
    dialogue.appendChild(p);

    //add a spacer
    p = $D('p', {innerHTML:'&nbsp;'});
    dialogue.appendChild(p);

    p = $D('p');
    p.appendChild($D('span', {innerHTML:"name:", className:'label'}));
    var inp = $D('input', {type:'text', className:'value'});
    if (obj.id != null) {
	inp.value = obj.name;
    }
    p.appendChild(inp);
    dialogue.appendChild(p);

    //add buttons
    p = $D('p');
    //a spacer to move the buttons to the right
    p.appendChild($D('span', {className:'diagBtnSpacer'}));
    var cancel = $D('input', {type:'button', value:'cancel', className:'diagBtn'});
    cancel.onclick = function(){destroyOverlay();}
    p.appendChild(cancel);

    var save = $D('input', {type:'button', value:'save', className:'diagBtn'});
    save.onclick = function(event) {
	var cb = function(req) {
	    var resp = eval("("+req.responseText+")");
	    if (resp.success) {
		window.location = SUB_SITE+"fieldsView/?page=-1"
	    }
	}
	//Load the model
	obj.name = inp.value
	obj.save(cb);
    }
    p.appendChild(save);

    dialogue.appendChild(p);
}

function destroyOverlay() {
    //show the overlay:
    var overlay = $('overlay');
    overlay.style.display="none";    
}

//DIRECTLY ripped from samples.js and home.js and modified
function SearchView(searchFld, searchBtn, cancelBtn, msg) {
    this.searchFld = searchFld;
    this.searchBtn = searchBtn;
    this.cancelBtn = cancelBtn;
    this.msg = msg;
    var outer = this;
    
    //handle the searchBtn interactions
    this.searchBtn.onclick = function(event) {
	if (outer.searchFld.value != outer.msg) {
	    window.location = SUB_SITE+"fieldsView/?search="+searchFld.value;
	}
    }

    //Enter key invokes search --NOTE: this might not work across browsers
    this.searchFld.onkeydown = function(event) {
	if (event.keyCode == 13) {
	    outer.searchBtn.onclick()
	}
    }
    this.cancelBtn.onclick = function(event) {
	window.location = SUB_SITE+"fieldsView/";
    }

}
