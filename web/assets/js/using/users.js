var url = window.storage.globalVar;

function bind_ban_button(button){
    button.bind('click',
        function(){
            $.post(url+"change_user",
            {
                "tg_id": tg_id,
                "type": 'ban'
            },
            onAjaxSuccess);
            function onAjaxSuccess(data){location.reload();}
        });
}

function bind_rating(input){
    input.bind('change',
        function(){
            $.post(url+"change_user",
            {
                "tg_id": tg_id,
                "type": 'rating',
                "count": input.val()
            },
            onAjaxSuccess);
            function onAjaxSuccess(data){
                if (data === 'false'){alert('error')}
                else{location.reload()}
                }
        });
}

$(document).ready(function(){

    function get_users(){
        $.post(url+"get_users",
            {
            },
            onAjaxSuccess);
                function onAjaxSuccess(data){
                data=JSON.parse(data);

                for (let i = 0; i < data.length; i++) {
                    let id = data[i][0];
                    let username = data[i][1];
                    let fio = data[i][2];

                    let a_url = '<a href="users.html?'+id+'">'+id+'</a>'

                    $("table").append('<tr class="gradeA odd "><td class="center">' + a_url + '</td><td>' + username + '</td><td>' + fio + '</td></tr>');
                }

                $('#dataTables-users').dataTable();
            }
    }

    function get_user(id) {
        $.post(url+"get_user",
            {
                "id": id
            },
            onAjaxSuccess);
        function onAjaxSuccess(data){
            data = JSON.parse(data);

            // tg
            tg_id = data.tg_id;
            $("#tg_id").append(tg_id);
            $("#first_name").append(data.first_name);
            $("#last_name").append(data.last_name);
            $("#tg_username").append(data.tg_username);
            $("#last_active").append(data.last_active);

            // trade
            let trade_id = data.trade_id;
            $("#trade_id").append(trade_id);
            $("#fio").append(data.fio);
            $("#mail").append(data.mail);
            $("#phone").append(data.phone);
            $("#time_zone").append(data.time_zone);

            // card
            let table = $('#cards');
            // alert(data.cards.length);
            if (data.cards.length === 0){
                table.append('<tr><td class="text-center"> - </td></tr>');
            }
            else{
                for (let i = 0; i < data.cards.length; i++) {
                    let current_card = data.cards[i];
                    table.append('<tr><td><p>'+current_card+'</p></td></tr>');
                }
            }

            // referals
            $('#vista_usd').append(data.vusd);
            $('#vista_eur').append(data.veur);
            let ref_table = $('#referrals');
            if (data.referal_to === false){
                $('#referral').text(data.referal_to);
            }
            else{
                $('#referral').append('<a href="users.html?'+data.main_referral+'">'+data.main_referral+'</a>');
            }

            for (let i = 0; i < data.referrals.length; i++) {
                let ref_user = data.referrals[i];
                let td1 = '<td> <a href="users.html?'+ref_user[0]+'">'+ref_user[0]+'</a></td>';
                let td2 = '<td> '+ref_user[1]+'</td>';
                ref_table.append('<tr>'+td2+td1+'</tr>');
            }



            // control
            let ban_button = $('#ban');
            ban_button.removeClass('btn-secondary')
            if (data.ban === true) {
                ban_button.addClass('btn-danger')
                ban_button.text('Разбанить')
            }
            else{
                ban_button.addClass('btn-primary')
                ban_button.text('Забанить')
            }
            bind_ban_button(ban_button);

            let rating_input = $('#rating');
            rating_input.val(data.rating);
            bind_rating(rating_input);

            // olddeals
            let old_a = '<a href="olddeals.html?'+trade_id+'">История сделок</a>';
            $('#olddeals').append(old_a);
        }
    }

    let list = location.href.split('/');

    // users
    if (list[list.length - 1] === 'users.html'){
        $('#users').css({'display': 'block'});
        get_users();
    }
    // user
    else{
        // set nav user
        let users_nav = $('#users_nav');
        users_nav.removeClass('active-menu');
        users_nav.attr('href', 'users.html');
        $('#user').css({'display': 'block'});
        let id = list[list.length - 1];
        id = id.replace('users.html?','');
        get_user(id);
    }
});