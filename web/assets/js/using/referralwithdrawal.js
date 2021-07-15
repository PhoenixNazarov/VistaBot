var url = window.storage.globalVar;

function bind_allow(){
    $('.allow').bind('click',
        function(){
            $.post(url+"allow_withdrawal",
            {
                "id": $(this).val()
            },
            onAjaxSuccess);
            function onAjaxSuccess(data){location.reload();}
        });
}

$(document).ready(function(){

    $.post(url+"get_withdrawals",
        {
        },
        onAjaxSuccess);
            function onAjaxSuccess(data){
            data=JSON.parse(data);

            for (let i = 0; i < data.length; i++) {
                let id = data[i][0];
                let currency = data[i][1];
                let userId = data[i][2];
                let card = data[i][3];
                let count = data[i][4];

                userId = '<a href="users.html?'+userId+'">'+userId+'</a>'

                let allow_button = '<button class="allow btn btn-success btn-sm" value="'+id+'">✔️</button>'
                // let disallow_button = '<button class="user_bal btn btn-danger btn-sm" value="'+id+'">❌</button>'


                $("table").append('<tr class="gradeA odd "><td>' + userId + '</td><td>' + card +' ' +currency + '</td><td>' + count + '</td><td>' + allow_button + '</td></tr>');
            }
            $('table').dataTable();
            bind_allow();
        }

});