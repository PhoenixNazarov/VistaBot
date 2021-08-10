var url = window.storage.globalVar;

function unixToDate(timestamp){
    var date = new Date(timestamp * 1000);
    var hours = date.getHours();
    var minutes = "0" + date.getMinutes();
    var seconds = "0" + date.getSeconds();
    var year = date.getFullYear();
    var month = date.getMonth();
    var day = date.getDay();
    var formattedTime = hours + ':' + minutes.substr(-2) + ':' + seconds.substr(-2);
    return day + '.' + month + '.' + year + ' ' + formattedTime ;
}

function update_base(){
    $('.showed').remove();
    $.post(url+"get_old_deals",
        {
            'id': id,
            'date1': $('#datetimepicker1_inp').val(),
            'date2': $('#datetimepicker2_inp').val(),
        },
        onAjaxSuccess);
            function onAjaxSuccess(data){
                data=JSON.parse(data);

                final_count = 0;
                final_profit = 0;
                final_referral = 0

                list = [];

                for (let i = 0; i < data.length; i++) {
                    let userA = data[i][0];
                    let userB = data[i][1];
                    let text = data[i][2];
                    let referralACount = data[i][3];
                    let referralBCount = data[i][4];
                    let commission = data[i][5]
                    let date = data[i][7];
                    final_count += data[i][6];
                    final_profit += commission;
                    final_referral += referralACount+ referralBCount;

                    userA = '<a href="users.html?'+userA+'">'+userA+'</a>';
                    userB = '<a href="users.html?'+userB+'">'+userB+'</a>';

                    list.push('<tr class="gradeA odd showed"><td>' + userA + '</td><td>' + userB + '</td><td>' + text + '</td><td>' + referralACount +'+'+ referralBCount +'</td><td>' + commission + '</td><td>' + unixToDate(date) + '</td></tr>');
                }
                $("#dataTables-olddeals").append('<tr class="gradeA odd showed"><td></td><td><b>Итого</b></td><td><b>' + final_count + '</b></td><td><b>' + final_referral + '</b></td><td><b>' + final_profit + '</b></td><td></td></tr>');

                for (let i = 0; i < list.length; i++){
                    $("#dataTables-olddeals").append(list[i]);
                }
                $('#dataTables-olddeals').dataTable();
        }
}

$(document).ready(function(){
    let list = location.href.split('/');

    if (list[list.length - 1] === 'olddeals.html'){
        id = -1;
    }
    else{
        id = list[list.length - 1];
        id = id.replace('olddeals.html?','');
        update_base();
    }


    $('#update').bind('click', update_base);

    $('#datetimepicker6').datetimepicker({
        useCurrent: false,
        locale: 'ru'});
    $('#datetimepicker7').datetimepicker({
        useCurrent: false,
        locale: 'ru'
    });

    $("#datetimepicker6").on("dp.change", function (e) {
       $('#datetimepicker7').data("DateTimePicker").minDate(e.date);
    });
    $("#datetimepicker7").on("dp.change", function (e) {
       $('#datetimepicker6').data("DateTimePicker").maxDate(e.date);
    });

});