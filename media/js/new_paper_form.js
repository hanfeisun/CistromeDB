/*
function init() {
    //create the journal choices
    var cb = function(req) {
	var journals = eval("("+req.responseText+")");

	var container = $('journal');
	container.appendChild($D('label', {'for':'journal', 
					 'innerHTML':'Journal'}));
	
	var select = $D('select', {'name':'journal', 'id':'journal'})
	select.appendChild($D('option',{'value':'','innerHTML':'----------'}));
	for (var i = 0; i < journals.length; i++) {
	    select.appendChild($D('option',{'value':journals[i].id,
					  'innerHTML':journals[i].name}));
	}
	container.appendChild(select);

	var a = $D('a', {'href':SUB_SITE+"new_journal_form/",
			   'innerHTML':"add new journal"});
	container.appendChild(a);
    }
    var getJournals = 
	new Ajax.Request(SUB_SITE+"jsrecord/Journals/all/", 
			 {method:"get", onSuccess: cb});
}
*/

function init() {
    var container = $('id_journal').parentNode;
    var thisPage = SUB_SITE+"new_paper_form/";
    var a = $D('a', {'href':SUB_SITE+"new_journal_form/?next="+thisPage,
		       'innerHTML':"add new journal"});
    container.appendChild(a);
}
