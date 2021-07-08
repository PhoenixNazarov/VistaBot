var url = window.storage.globalVar;

$(document).ready(function(){
    $.post(url+"index",
            {
            },
            onAjaxSuccess);
    function onAjaxSuccess(data){
        data = JSON.parse(data);
        $('#asks').append(data['asks']);
        $('#deals').append(data['deals']);
        $('#users').append(data['users']);
    }
});