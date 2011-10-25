function validPmid(pmid) {
    //returns true if it is an positive integer >= 10000000
    pattern = /^\d{8}$/;
    return pattern.test(pmid);
}

function validGSEID(gseid) {
    pattern = /^GSE\d{5}$/;
    return pattern.test(gseid);
}

var currPMID = "";
//Function that tries to grab the paper info from ENTREZ dbs
function fetch(pmid) {
    //var URL = "/entrez/eutils/esummary";
    var URL = SUB_SITE+"entrez/GetPubmedArticle/";

    var cbFn = function(req) {
	//alert(req.responseText);
	
	var tmp = eval("("+req.responseText+")");

	var authorList = tmp.authors;
	var authors = authorList.length > 0 ? authorList[0] : "";
	for (var i = 1; i < authorList.length; i++) {
	    authors += ", " + authorList[i];
	}

	$('authors').innerHTML = authors;

	var rest = ['gseid', 'title','abstract','published'];
	rest.each(function(attr) { $(attr).innerHTML = tmp[attr]; });
	//currPMID = tmp['pmid'];
    }

    var EntrezCall = 
	new Ajax.Request(URL, {method:"get", onSuccess: cbFn,
				 parameters:{"id":pmid}});

}

function init() {
    $('fetchBtn').onclick = function(event) {
	var val = $('pmid').value;
	if (validPmid(val)) {
	    fetch(val);
	    currPMID = val;
	} else {
	    alert("invalid pmid");
	}
    }
    
    $('importBtn').onclick = function(event) {
	if(validPMID(currPMID)) {
	    //Just before submission add a hidden input field
	    var pmid = document.createElement('input');
	    pmid.type = "hidden";
	    pmid.name = "pmid";
	    pmid.value = currPMID;
	    $('autoimport_form').appendChild(gseid);
	} else {
	    alert("you must fetch a valid pubmed entry first\n"+val);
	    //break the submission
	    return false;
	}
    }
}
