//function that redirects to the manage file page
function manageFiles(model, obj_id) {
    //alert(model + " " + obj_id);
    window.location = SUB_SITE+"manage_files/"+model+"/"+obj_id+"/";
}

var Model;
var Obj_id;

function deleteCb(resp) {
    //reload the page
    window.location.reload();
}

function manage_files_init(model, obj_id) {
    Model = model;
    Obj_id = obj_id;

    //hook up the delete functionality--hack: use "fakeLink" css
    var deleteLinks = $$('.fakeLink');
    for (var i = 0; i < deleteLinks.length; i++) {
	deleteLinks[i].onclick = function() {
	    //make ajax delete call and then reload pg
	    var resp = confirm("Are you sure you want to DELETE this file?");
	    if (resp) {
		var ignored = new Ajax.Request(SUB_SITE+"delete_file/"+Model+"/"+Obj_id+"/"+this.id+"/", {method:"get", onComplete: deleteCb})
	    }
	}
	    
    }
}
