var rowSelects;
var model = null;
var next = null;

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
    createBtn.disabled = "true";
    /*
    //CHANGE THIS BELOW!
    createBtn.onclick = function(event) {
	//model = Factors
	//we want to redirect to new_factor_form
	var tmp = mdl.toLowerCase();
	if (tmp != "species" && tmp != "assembly") {
	    tmp = tmp.substring(0, tmp.length-1);
	}
	//alert(SUB_SITE+"new_"+tmp+"_form/?next="+this_pg);
	window.location = SUB_SITE+"new_"+tmp+"_form/?next="+this_pg;
    }
    */

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
}

function showInfo(id) {
    //NOTE: in CHROME, for some reason my global vars aren't global! so models
    //is null!!
    var obj = model.get(id);
    
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
    
    //build the info:
    for (var i=0; i < obj.fields.length; i++) {
	p = $D('p');
	if (obj.fields[i] != "id") {
	    p.appendChild($D('span', {innerHTML:obj.fields[i]+":", className:'label'}));
	    p.appendChild($D('span', {innerHTML:obj[obj.fields[i]], className:'value'}));
	} 
	dialogue.appendChild(p);
	
    }
    
    //add buttons
    p = $D('p');
    //a spacer to move the buttons to the right
    p.appendChild($D('span', {className:'diagBtnSpacer'}));
    var edit = $D('input', {type:'button', value:'edit', className:'diagBtn'});
    p.appendChild(edit);
    var close = $D('input', {type:'button', value:'close', className:'diagBtn'});
    close.onclick = function(){destroyOverlay();}
    p.appendChild(close);
    dialogue.appendChild(p);

}

function destroyOverlay() {
    //show the overlay:
    var overlay = $('overlay');
    overlay.style.display="none";    
}
