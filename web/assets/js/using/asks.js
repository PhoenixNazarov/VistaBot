var url = window.storage.globalVar;

function bind_allow(button) {
    button.bind('click',
        function(){
            $.post(url+"allow_ask",
            {
                "ask_id": ask_id,
            },
            onAjaxSuccess);
            function onAjaxSuccess(data){location.reload();}
        });
}
function bind_delete(button) {
    button.bind('click',
        function(){
            $.post(url+"delete_ask",
            {
                "ask_id": ask_id,
            },
            onAjaxSuccess);
            function onAjaxSuccess(data){location.href = 'asks.html';}
        });
}

$(document).ready(function(){

    function get_asks(){
        $.post(url+"get_asks",
            {
            },
            onAjaxSuccess);
                function onAjaxSuccess(data){
                data=JSON.parse(data);

                for (let i = 0; i < data.length; i++) {
                    let id = data[i][0];
                    let id_owner = data[i][1];
                    let description = data[i][2];
                    let status = data[i][3];
                    if (status === 'ok'){
                        status = `<p2 class="bg-success">${status}</p2>`;
                    }
                    else{
                        status = `<p2 class="bg-warning">${status}</p2>`;
                    }

                    let a_url = '<a href="asks.html?'+id+'">'+id+'</a>'
                    let b_url = '<a href="users.html?'+id_owner+'">'+id_owner+'</a>'

                    $("table").append('<tr class="gradeA odd "><td class="center">' + a_url + '</td><td>' + b_url + '</td><td>' + description + '</td><td>' + status + '</td></tr>');
                }

                $('#dataTables-asks').dataTable();
            }
    }

    function get_ask(id) {
        $.post(url+"get_ask",
            {
                "id": id
            },
            onAjaxSuccess);
        function onAjaxSuccess(data){
            data = JSON.parse(data);

            // tg
            $('#ask_id').append(data.id);
            ask_id = data.id;
            $('#type').append(data.type);
            $('#status').append(data.status);
            let id_owner_a = `<a href="users.html?${data.trade_id_owner}">${data.trade_id_owner}</a>`;
            $('#id_owner').append(id_owner_a);
            $('#have_currency').append(data.web.give);
            $('#get_currency').append(data.web.get);
            $('#rate').append(data.web.rate);
            $('#rating').append(data.rating);
            $('#time_zone').append(data.time_zone);
            $('#incomplete').append(data.incomplete);

            // vst card
            $('#vst_card').append(`<tr><td> ${data.vst_card} </td></tr>`)

            // fiat cards/banks
            if (data.type === 'fiat'){
                $('#fiat_name').append('банки')
                $('#fiat').append(`<tr><td><p>${data.fiat_banks}</p></td></tr>`)
            }
            else{
                $('#fiat_name').append('карты')
                for (let i = 0; i < data.fiat_cards.length; i++) {
                    $('#fiat').append(`<tr><td><p>${data.fiat_cards[i]}</p></td></tr>`)
                }
            }

            // control
            if (data.status === 'wait_allow'){
                let button_allow = $('#allow');
                button_allow.css({'display': 'block'});
                bind_allow(button_allow);
            }
            bind_delete($('#delete'));


            // let table = $('#vst_card');
            // if (data.cards.length === 0){
            //     table.append('<tr><td class="text-center"> - </td></tr>');
            // }
            // else{
            //     for (let i = 0; i < data.cards.length; i++) {
            //         let current_card = data.cards[i];
            //         table.append('<tr><td><p>'+current_card+'</p></td>></tr>');
            //     }
            // }
            //
            // // referals
            // let ref_table = $('#referrals');
            // if (data.referal_to === false){
            //     $('#referral').text(data.referal_to);
            // }
            // else{
            //     $('#referral').append('<a href="users.html?'+data.main_referral+'">'+data.main_referral+'</a>');
            // }
            //
            // for (let i = 0; i < data.referrals.length; i++) {
            //     let ref_user = data.referrals[i];
            //     let td1 = '<td> <a href="users.html?'+ref_user[0]+'">'+ref_user[0]+'</a></td>';
            //     let td2 = '<td> '+ref_user[1]+'</td>';
            //     ref_table.append('<tr>'+td2+td1+'</tr>');
            // }
            //
            // // control
            // let ban_button = $('#ban');
            // ban_button.removeClass('btn-secondary')
            // if (data.ban === true) {
            //     ban_button.addClass('btn-danger')
            //     ban_button.text('Разбанить')
            // }
            // else{
            //     ban_button.addClass('btn-primary')
            //     ban_button.text('Забанить')
            // }
            // bind_ban_button(ban_button);
            //
            // let rating_input = $('#rating');
            // rating_input.val(data.rating);
            // bind_rating(rating_input);
        }
    }

    let list = location.href.split('/');

    // asks
    if (list[list.length - 1] === 'asks.html'){
        $('#asks').css({'display': 'block'});
        get_asks();
    }
    // ask
    else{
        let users_nav = $('#asks_nav');
        users_nav.removeClass('active-menu');
        users_nav.attr('href', 'asks.html');
        $('#ask').css({'display': 'block'});
        let id = list[list.length - 1];
        id = id.replace('asks.html?','');
        get_ask(id);
    }
});