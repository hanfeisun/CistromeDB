var TabsModel = ModelFactory(["currTab"],[]);
var tabsModel = new TabsModel({"currTab":null});
var msg = "Search Cistrome PC";

//load the sub-scripts
var head = $$('head')[0];
if (head){
    var lst = ["factors", "cells", "papers"];
    for (var i = 0; i < lst.length; i++) {
	var script = new Element('script', { type: 'text/javascript', 
					 src: SUB_SITE+'static/js/home_'+lst[i]+'.js' });
	head.appendChild(script);
    }
}

function init() {
    init_factors();
    init_cells();
    init_papers();

    //NOTE: these must be integrated at this level
    //tab views
    var fct = new TabView($('factorsTab'), $('factorsView'), tabsModel);
    var cls = new TabView($('cellsTab'), $('cellsView'), tabsModel);
    var prs = new TabView($('papersTab'), $('papersView'), tabsModel);
    tabsModel.currTabEvent.register(function() { fct.tabModelLstnr();});
    tabsModel.currTabEvent.register(function() { cls.tabModelLstnr();});
    tabsModel.currTabEvent.register(function() { prs.tabModelLstnr();});

    fct.tab.onclick();
    /* DO I want that drop down behavior when papers is first clicked??
    var papersTabLoad = true;
    //override the papers tab click
    prs.tab.onclick = function() {
	
	tabsModel.setCurrTab(prs.tab);
	if (papersTabLoad) {
	    //DEFAULT/only view for paper collection homepage is ALL papers
	    //TURNING THIS OFF FOR NOW! --REMEMBER TO TURN IT BACK ON!
	    getPapers("all", papersModel);
	    //wait 1.5 secs and then show the results pane
	    setTimeout(function() { results_tog.open();}, 1500);
	    papersTabLoad = false;
	}

    }
    */

}

function TabView(tab, section, tabsModel) {
    this.tab = tab;
    this.section = section;
    this.tabsModel = tabsModel;
    var outer=this;

    this.tabModelLstnr = function() {
	if (outer.tabsModel.getCurrTab() == outer.tab) {
	    outer.show();
	} else {
	    outer.hide();
	}
    }
    
    this.tab.onclick = function(event) {
	outer.tabsModel.setCurrTab(outer.tab);
    }

    this.show = function() {
	outer.tab.className = "activeTab";
	outer.section.style.display = "block";
    }

    this.hide = function() {
	outer.tab.className = "tabHeader";
	outer.section.style.display = "none";
    }
}

//These same functions were going to be duplicated for all three tabs,
//so instead of doing that i'm writing a formal class to handle the 
//search input and search btn interactions
//NOTE: searchCB can be initially null and set at a later time
//msg = default msg to display, can't be empty string!
function SearchView(searchFld, searchBtn, msg, searchURL, searchCb) {
    this.searchFld = searchFld;
    this.searchBtn = searchBtn;
    this.msg = msg;
    this.searchURL = searchURL;
    this.searchCb = searchCb;
    var outer = this;
    
    this.searchFld.value = this.msg;
    this.searchFld.className = "searchWait"
    this.searchFld.onclick = function(event) {
	//IF the user is clicking for the first time
	if (outer.searchFld.value == outer.msg) {
	    outer.searchFld.className = "searchIn";
	    outer.searchFld.value = "";
	}
    }

    this.searchFld.onblur = function(event) {
	if (outer.searchFld.value == "") {
	    outer.searchFld.className = "searchWait";
	    outer.searchFld.value = outer.msg;
	}
    }

    //handle the searchBtn interactions
    this.searchBtn.onclick = function(event) {
	if (outer.searchFld.value != outer.msg) {
	    var srch = new Ajax.Request(outer.searchURL, 
    {method:"get", parameters: {"q":outer.searchFld.value}, 
     onComplete: outer.searchCb});
	    outer.searchBtn.disabled = true;
	    outer.searchFld.disabled = true;
	    outer.searchFld.style.color = "#c1c1c1"; //font color to gray
	}
    }

    //Enter key invokes search --NOTE: this might not work across browsers
    this.searchFld.onkeydown = function(event) {
	if (event.keyCode == 13) {
	    outer.searchBtn.onclick()
	}
    }
}


//NOTE: i'm not sure who uses these functions!!-- I think they're obsolete!
//BUT i think they're useful!

/* getStyle- fn to get the COMPUTED css value of an element 
 * ref: http://robertnyman.com/2006/04/24/get-the-rendered-style-of-an-element/
 * NOTE: the elm must be part of the DOM (e.g. appended somewhere on the tree!)
 */
/*
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
*/
/*given a css, returns the css rule using the selector, e.g. selector="a:hover"
 */
/*
function getStyleRule(css, selector) {
    var rules = css.cssRules ? css.cssRules: css.rules;
    for (var i = 0; i < rules.length; i++){
	if(rules[i].selectorText == selector) { 
	    return rules[i];
	}
    }
    return null;
}
*/
