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
                for (let i = 0; i < data.length; i++) {
                    let userA = data[i][0];
                    let userB = data[i][1];
                    let text = data[i][2];
                    let cancel = data[i][3];
                    let moderate = data[i][4]
                    let date = data[i][5];

                    userA = '<a href="users.html?'+userA+'">'+userA+'</a>'
                    userB = '<a href="users.html?'+userB+'">'+userB+'</a>'

                    $("table").append('<tr class="gradeA odd "><td>' + userA + '</td><td>' + userB + '</td><td>' + text + '</td><td>' + cancel +'/'+moderate +'</td><td>' + date + '</td></tr>');
                }
                $('table').dataTable();
        }
});