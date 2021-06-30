var url = window.storage.globalVar;


function bind_save(button){
    button.bind('click',
        function(){
            $.post(url+"set_settings",
            {
                "perc_vst": $('#perc_vst').val(),
                "perc_fiat": $('#perc_fiat').val()
            },
            onAjaxSuccess);
            function onAjaxSuccess(data){
                if (data === 'false'){alert('error')}
                else{location.reload()}
                }
        });
}

function get_faqs(data){
    let table = $('#ask_table')
    for (let i = 0; i < data.length; i++){
        let format = `<td><td></td></td>`
    }
}

$(document).ready(function(){

    function get_settings(){
        $.post(url+"get_settings",
            {
            },
            onAjaxSuccess);
                function onAjaxSuccess(data){
                data=JSON.parse(data);

                $('#perc_vst').val(data.perc_vst);
                $('#perc_fiat').val(data.perc_fiat);
            }
    }

    get_settings();
    bind_save($('#save'));


});