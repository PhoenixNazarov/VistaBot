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

function save_faqs(){
    let names = $('.faq_name');
    let text = $('.faq_text');

    let faqs = []

    for (let i = 0; i < names.length; i++){
        faqs.push([$(names[i]).val(), $(text[i]).val()]);
    }
    return faqs;
}

function bind_faq_remove(){
    $('.faq_remove').bind('click',
        function(){
            $(this).closest("tr").remove();
        });
}

function bind_faq_add(button){
    button.bind('click',
        function(){
            str ='<tr><td><button type="button" class="btn btn-danger faq_remove">-</button></td>\n' +
                 '<td><input class="form-control faq_name"></td>\n' +
                 '<td><textarea class="form-control faq_text" rows="3"></textarea></td></tr>';
            $('#faq_table').append(str);
            bind_faq_remove();
    });
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

    // get_settings();
    bind_save($('#save'));
    bind_faq_add($('#faq_add'))

});