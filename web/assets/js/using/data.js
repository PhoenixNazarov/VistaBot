var url='http://127.0.0.1:5000/';
window.storage = {}; // для пространства имен, что бы много мусора в window не пихать
window.storage.globalVar = url;

jQuery(document).ready(function(){
	function au(){
    	jQuery.post(url,
	        {
	        },
	        onAjaxSuccess);
	            function onAjaxSuccess(data){
	            if (data==='NOT_AUTH'){$(location).attr('href','auth.html');}
		}}
	a=location.pathname.split('/').pop();

	if (a!=='auth.html'){
		au();
		
	}
	
});