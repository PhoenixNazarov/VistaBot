var url = window.storage.globalVar;

function bind_remove_deal(button, id){
    button.bind('click',
        function(){
            $.post(url+"remove_deal",
            {
                "id": id,
            },
            onAjaxSuccess);
            function onAjaxSuccess(data){location.href = 'deals.html';}
        });
}
function bind_garant_accept(button, id){
    button.bind('click',
        function(){
            $.post(url+"accept_garant_deal",
            {
                "id": id,
            },
            onAjaxSuccess);
            function onAjaxSuccess(data){location.reload()}
        });
}
function bind_garant_send(button, id){
    button.bind('click',
        function(){
            $.post(url+"send_garant_deal",
            {
                "id": id,
            },
            onAjaxSuccess);
            function onAjaxSuccess(data){location.href = 'deals.html';}
        });
}


$(document).ready(function(){

    function bind_update(){
    $.post(url+"get_deal",
            {
                "id": id
            },
            onAjaxSuccess);
        function onAjaxSuccess(data){
            if (data !== data_str){location.reload()}
            else{setTimeout(bind_update, 3000);}
        }
    }

    function get_deals(){
        $.post(url+"get_deals",
            {
            },
            onAjaxSuccess);
                function onAjaxSuccess(data){
                data=JSON.parse(data);

                for (let i = 0; i < data.length; i++) {
                    let id = data[i][0];
                    let desr = data[i][1];
                    let status = data[i][2];

                    let a_url = '<a href="deals.html?'+id+'">'+id+'</a>'

                    $("#dataTables-deals").append('<tr class="gradeA odd "><td class="center">' + a_url + '</td><td>' + desr + '</td><td>' + status + '</td></tr>');
                }

                $('#dataTables-deals').dataTable();
            }
    }

    function get_deal(id) {
        $.post(url+"get_deal",
            {
                "id": id
            },
            onAjaxSuccess);
        function onAjaxSuccess(data){
            data_str = data;
            data = JSON.parse(data);

            $('#a_vst_card').append(data.a_vst_card);
            $('#b_vst_card').append(data.b_vst_card);

            $('#vista_count').append(data.vista_count+' '+ data.vista_currency);
            $('#fiat_count').append(data.fiat_count+' '+ data.fiat_currency);
            $('#vista_count_w').append(data.vista_count_without_com+' '+ data.vista_currency);

            let f_panel = $('#first_panel');
            let s_panel = $('#second_panel');
            let t_panel = $('#third_panel');
            let b_garant_accept = $('#garant_accept');
            let b_garant_send = $('#garant_vst_send');

            function first_block_end(){
                $('#fp_status_2').css({'display': 'inline'});
                f_panel.removeClass('panel-default');
                f_panel.addClass('panel-success');
            }
            function second_block_end(){
                s_panel.removeClass('panel-default');
                s_panel.addClass('panel-success');
                $('#sc_footer').css({'display': 'block'});
                $('#sc_status_3').css({'display': 'inline'});
            }

            if (data.status === 'wait_vst'){
                f_panel.removeClass('panel-default');
                f_panel.addClass('panel-info');

                $('#fp_status_1').css({'display': 'inline'});
                $('#notificate_A').css({'display': 'inline'});
            }
            if (data.status === 'wait_vst_proof'){
                f_panel.removeClass('panel-default');
                f_panel.addClass('panel-info');

                b_garant_accept.css({'display': 'inline'});
                bind_garant_accept(b_garant_accept, id)
            }
            if (data.status === 'wait_fiat'){
                first_block_end();

                s_panel.removeClass('panel-default');
                s_panel.addClass('panel-info');
                $('#sc_footer').css({'display': 'block'});

                $('#sc_status_1').css({'display': 'inline'});
            }
            if (data.status === 'wait_fiat_proof'){
                first_block_end();

                s_panel.removeClass('panel-default');
                s_panel.addClass('panel-info');
                $('#sc_footer').css({'display': 'block'});

                $('#sc_status_2').css({'display': 'inline'});
            }
            if (data.status === 'wait_garant_vst'){
                first_block_end();
                second_block_end();

                t_panel.removeClass('panel-default');
                t_panel.addClass('panel-info');
                $('#th_footer').css({'display': 'block'});
                b_garant_send.css({'display': 'inline'});
                bind_garant_send(b_garant_send, id);
            }

            bind_remove_deal($('#remove'), id);
            setTimeout(bind_update, 3000);
        }
    }

    let list = location.href.split('/');

    // deals
    if (list[list.length - 1] === 'deals.html'){
        $('#deals').css({'display': 'block'});
        get_deals();
    }
    // deal
    else{
        // set nav deal
        let users_nav = $('#deals_nav');
        users_nav.removeClass('active-menu');
        users_nav.attr('href', 'deals.html');
        $('#deal').css({'display': 'block'});
        id = list[list.length - 1];
        id = id.replace('deals.html?','');
        get_deal(id);
    }
});