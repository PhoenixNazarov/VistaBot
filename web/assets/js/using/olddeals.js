var url = window.storage.globalVar;

$(document).ready(function(){
    let list = location.href.split('/');

    if (list[list.length - 1] === 'olddeals.html'){
        id = -1;
    }
    else{
        id = list[list.length - 1];
        id = id.replace('olddeals.html?','');
    }

    $.post(url+"get_old_deals",
        {
            'id': id
        },
        onAjaxSuccess);
            function onAjaxSuccess(data){
                data=JSON.parse(data);

                final_count = 0;
                final_profit = 0;
                final_referral = 0

                for (let i = 0; i < data.length; i++) {
                    let userA = data[i][0];
                    let userB = data[i][1];
                    let text = data[i][2];
                    let referral = data[i][3];
                    let profit = data[i][4]
                    let date = data[i][5];
                    final_count += data[i][6];
                    final_profit += profit;
                    final_referral += referral;

                    userA = '<a href="users.html?'+userA+'">'+userA+'</a>'
                    userB = '<a href="users.html?'+userB+'">'+userB+'</a>'

                    $("#dataTables-olddeals").append('<tr class="gradeA odd "><td>' + userA + '</td><td>' + userB + '</td><td>' + text + '</td><td>' + referral + '</td><td>' + profit + '</td><td>' + date + '</td></tr>');
                }
                $("#dataTables-olddeals").append('<tr class="gradeA odd "><td></td><td><b>Итого</b></td><td><b>' + final_count + '</b></td><td><b>' + final_referral + '</b></td><td><b>' + final_profit + '</b></td><td></td></tr>');
                $('#dataTables-olddeals').dataTable();
        }
});