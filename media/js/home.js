var TabsModel = ModelFactory(["currTab"],[]);
var tabsModel = new TabsModel({"currTab":null});

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
