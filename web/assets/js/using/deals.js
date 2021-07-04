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
function bind_notification_A(button){
        button.bind('click',
        function(){
            $.post(url+"notification_deal",
            {
                "id": id,
                'position': 'A'
            },
            onAjaxSuccess);
            function onAjaxSuccess(data){location.reload()}
        });
}
function bind_notification_B(button){
        button.bind('click',
        function(){
            $.post(url+"notification_deal",
            {
                "id": id,
                'position': 'B'
            },
            onAjaxSuccess);
            function onAjaxSuccess(data){location.reload()}
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
            else{setTimeout(bind_update, 5000);}
        }
    }

    function bind_update_time_A(){
        $('#vista_time_over').remove();

        var minutes = ~~(cur_time/60);
        var seconds = cur_time%60;
        if (cur_time < 0){
            seconds = seconds / -1;
        }
        if (seconds < 10){seconds = '0'+seconds;}

        var formattedTime = minutes + ':' + seconds;
        if (cur_time > 0) {
            $('#vista_count').append('<div id="vista_time_over" class = "text-info">' + formattedTime + '</div>');
        }
        else{
            $('#vista_count').append('<div id="vista_time_over" class = "text-danger">' + formattedTime + '</div>');
        }
        cur_time--;
        setTimeout(bind_update_time_A, 1000);
    }
    function bind_update_time_B(){
        $('#fiat_time_over').remove();

        var minutes = ~~(cur_time/60);
        var seconds = cur_time%60;
        if (cur_time < 0){
            seconds = seconds / -1;
        }
        if (seconds < 10){seconds = '0'+seconds;}

        var formattedTime = minutes + ':' + seconds;
        if (cur_time > 0) {
            $('#fiat_count').append('<div id="fiat_time_over" class = "text-info">' + formattedTime + '</div>');
        }
        else{
            $('#fiat_count').append('<div id="fiat_time_over" class = "text-danger">' + formattedTime + '</div>');
        }
        cur_time--;
        setTimeout(bind_update_time_B, 1000);
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
            $('#garant_vst_card1').append(data.g_vst_card);
            $('#garant_vst_card2').append(data.g_vst_card);

            $('#vista_count').append(data.vista_count+' '+ data.vista_currency);
            $('#fiat_count').append(data.fiat_count+' '+ data.fiat_currency);
            $('#vista_count_w').append(data.vista_count_without_com+' '+ data.vista_currency);

            $('#notificate_A_time').append(data.vista_last_notification);
            $('#notificate_B_time').append(data.fiat_last_notification);

            $('#Trade_id_A').append('<a href="users.html?'+data.a_trade_id+'">'+data.a_trade_id+'</a>');
            $('#Trade_id_B').append('<a href="users.html?'+data.b_trade_id+'">'+data.b_trade_id+'</a>');

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
                if (data.vista_send_over !== 0){
                    cur_time = ~~(data.vista_send_over - new Date().getTime() /1000);
                    bind_update_time_A(cur_time);
                }
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
                if (data.fiat_send_over !== 0) {
                    cur_time = ~~(data.fiat_send_over - new Date().getTime() / 1000);
                    bind_update_time_B(cur_time);
                }
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

            bind_notification_A($('#notificate_A'));
            bind_notification_B($('#notificate_B'));
            bind_remove_deal($('#remove'), id);
            setTimeout(bind_update, 5000);
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