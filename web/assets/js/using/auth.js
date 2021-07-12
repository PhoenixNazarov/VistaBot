
jQuery(document).ready(function(){
    var url = window.storage.globalVar;

        jQuery('button.aut').bind('click',
            function(){
                    nm=$("#name").val();
                    pas=$("#password").val();
                    jQuery.post(url+"auth",
                    {   
                        'url':'auth',
                        'name':nm,
                        'password':pas
                    },
                    onAjaxSuccess);
                function onAjaxSuccess(data){

                    if (data === 'ok'){
                        $(location).attr('href','index.html');}
                    }
                    data = JSON.parse(data);

                    kode=data.kod;
                    if (kode===1){
                        alert('Неправильный логин или пароль');
                    }
                });

});