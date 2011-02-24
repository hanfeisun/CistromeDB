var UserProfiles = loadJSRecord('UserProfiles');

function init() {
    var container = $('main');
    var cb = function(req) {
	var users = eval("("+req.responseText+")");
	var tbl = $D('table');
	var tr = $D('tr');
	tr.appendChild($D('th', {innerHTML:'User'}));
	tr.appendChild($D('th', {innerHTML:'Team'}));
	tr.appendChild($D('th', {innerHTML:'Edit'}));
	tbl.appendChild(tr);
	for (var i = 0; i < users.length; i++) {
	    tr = $D('tr');
	    tr.appendChild($D('td', {innerHTML: users[i].user.username}));
	    var teamTd = $D('td', {innerHTML: users[i].team});
	    tr.appendChild(teamTd);
	    var editTd = $D('td');
	    var editBtn = $D('input', {'type':'button', 'value':'edit'});
	    editBtn.onclick = function(u, teamTd, editTd, editB) {
		return function(event) {
		    var select = $D('select');
		    select.appendChild($D('option', {'value':'', 
						  'innerHTML':'None'}));
		    select.appendChild($D('option', {'value':'paper',
						  'innerHTML':'Paper',
						  'selected':(u.team=='paper')?
						  "selected":""}));
		    select.appendChild($D('option', {'value':'data',
						  'innerHTML':'Data',
						  'selected':(u.team=='data')?
						  "selected":""}));
		    if (teamTd.childNodes.length > 0) {
			teamTd.replaceChild(select, teamTd.childNodes[0]);
		    } else {
			teamTd.appendChild(select);
		    }
		    
		    var cancelBtn = $D('input', {'type':'button', 
					       'value':'cancel'});
		    cancelBtn.onclick = function(event) {
			//restore the previous values
			teamTd.innerHTML = u.team;
			//remove the cancel and save
			editTd.replaceChild(editB, editTd.childNodes[0]);
			editTd.removeChild(editTd.childNodes[1]);
		    }

		    var saveBtn = $D('input', {'type':'button', 
					     'value':'save'});
		    saveBtn.onclick = function(event) {
			//UserProfiles = user, team
			u.team = teamTd.childNodes[0].value;
			var cb = function(req) {
			    //alert(req.responseText);
			}
			var tmp = UserProfiles.get(u.id);
			tmp.setTeam(u.team);
			tmp.save(cb);
			cancelBtn.onclick();
		    }

		    editTd.replaceChild(cancelBtn, editTd.childNodes[0]);
		    editTd.appendChild(saveBtn);		    
		}
	    } (users[i], teamTd, editTd, editBtn);
	    editTd.appendChild(editBtn);
	    tr.appendChild(editTd);

	    tbl.appendChild(tr);
	}
	container.appendChild(tbl);
    }
    var getUserProfiles = 
	new Ajax.Request(SUB_SITE+"jsrecord/UserProfiles/all/",
			 {method:"get", onComplete:cb});
}
