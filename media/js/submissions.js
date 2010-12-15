
function changeStatus(id, currStatus) {
    var status = [["pending", "Pending"], ["closed", "Imported/Closed"],
		  ["n/a", "Not Appropriate"]]
    tmp = document.getElementById('status_'+id);    
    
    //create a new form
    form = document.createElement("form");
    form.action = SUB_SITE + "change_status/"+id+"/";
    form.method = "post";
    //make selection
    sel = document.createElement("select");
    sel.name = "status";
    sel.id = "id_status";
    for (var i = 0; i < status.length; i++) {
	opt = document.createElement("option");
	opt.value = status[i][0];
	opt.innerHTML = status[i][1];
	if (status[i][1] == currStatus) {
	    opt.selected = "selected";
	}
	sel.appendChild(opt);
    }
    form.appendChild(sel);
    //add submit
    submitBtn = document.createElement("input");
    submitBtn.type = "submit";
    submitBtn.value = "submit";    
    form.appendChild(submitBtn);

    //add cancel btn
    cancelBtn = document.createElement("span");
    cancelBtn.innerHTML = "cancel";
    cancelBtn.onclick = function(event) { cancel(tmp, id, currStatus);}
    cancelBtn.className = "clickable";
    form.appendChild(cancelBtn);

    //replace childnodes w/ form
    replaceChildren(tmp, [form]);
}

function cancel(container, id, currStatus) {
    container.innerHTML = currStatus;
    changeBtn = document.createElement("span");
    changeBtn.innerHTML = "change";
    changeBtn.onclick = function(event) { changeStatus(id, currStatus);}
    changeBtn.className = "clickable";
    container.appendChild(changeBtn);
}

function replaceChildren(container, new_children) {
    //remove current children
    while (container.childNodes.length > 0) {
	container.removeChild(tmp.firstChild);
    }
    for (var i = 0; i < new_children.length; i++) {
	container.appendChild(new_children[i]);
    }
}

