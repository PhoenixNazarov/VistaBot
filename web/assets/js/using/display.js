var url = window.storage.globalVar;

function div(val, by){
    return (val - val % by) / by;
}
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
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

var audio = new Audio('assets/notif.mp3');
async function notif(){
    notifActive = 1;
    audio.play();
    $('body').bind('mouseover',
        function(){
        notifActive = 0;
        $('body').unbind();
    });

    while (notifActive === 1){
        $('title').html('Новое уведомление')
        await sleep(1000);
        $('title').html('Дисплей')
        await sleep(1000);

    }
}

first = 1;
time_end = -1;
ctime = 0;

function getControlNotifications(){
    $.post(url+"display",
        {
            'time': ctime,
            'acceptAsks': acceptAsks,
            'dealGetVista': dealGetVista,
            'dealSendVista': dealSendVista,
            'referralWithdrawals': referralWithdrawals,
        },
        onAjaxSuccess);
        function onAjaxSuccess(data){
            data = JSON.parse(data);
            if (data.notifications !== 'notFound'){
                pasteControlNotifications(data.notifications)
                if (first === 1){first = 0}
                else{
                    notif();
                }
            }
            ctime = data.time;
            getControlNotifications();
        }
}

function pasteControlNotifications(data){
    for (let i=0; i < data.length; i++){
        if (data[i][0] === 'ask_allow'){
            pasteAcceptAsk(data[i])
        }
        if (data[i][0] === 'deal_getVista') {
            pasteDealGetVista(data[i])
        }
        if (data[i][0] === 'deal_sendVista') {
            pasteDealSendVista(data[i])
        }
        if (data[i][0] === 'referralWithdrawal') {
            pasteReferralWithdrawal(data[i])
        }
    }
}

function pasteAcceptAsk(data){
    src = `<div class="panel panel-warning">
                <div class="panel-heading">
                    Принятие заявки №<a href="asks.html?${data[1]}">${data[1]}</a>
                </div>
                <div class="panel-body">
                    <p>${data[2]}</p>
                </div>
                <div class="panel-footer">
                    <button value="${data[1]}" type="button" class="btn btn-warning acceptAsk">Принять</button>
                </div>
            </div>`

    $('#control-wrapper').append(src);

    buttons = $('#control-wrapper').find('.acceptAsk');

    $(buttons[buttons.length - 1]).bind('click',
    function(){
        AcceptAsk(this);
    });

}
function AcceptAsk(button){
    $.post(url+"allow_ask",
    {
        'ask_id': $(button).val()
    },
    onAjaxSuccess);
    function onAjaxSuccess(data){
        button.parentElement.parentElement.remove();
    }
}

function pasteDealGetVista(data){
    src = `<div class="panel panel-warning">
                <div class="panel-heading">
                    Принятие Vista от заявки №<a href="deals.html?${data[1]}">${data[2]}</a>
                </div>
                <div class="panel-body">
                    <p>${data[4]} ${data[5]}</p>
                    <p>${data[3]}</p>
                </div>
                <div class="panel-footer">
                    <button value="${data[1]}" type="button" class="btn btn-warning DealGetVista">Подтвердить</button>
                </div>
            </div>`

    $('#control-wrapper').append(src);

    buttons = $('#control-wrapper').find('.DealGetVista');

    $(buttons[buttons.length - 1]).bind('click',
    function(){
        DealGetVista(this);
    });

}
function DealGetVista(button){
    $.post(url+"accept_garant_deal",
    {
        'id': $(button).val()
    },
    onAjaxSuccess);
    function onAjaxSuccess(data){
        button.parentElement.parentElement.remove();
    }
}

function pasteDealSendVista(data){
    src = `<div class="panel panel-warning">
                <div class="panel-heading">
                    Отправление Vista по заявке №<a href="deals.html?${data[1]}">${data[2]}</a>
                </div>
                <div class="panel-body">
                    <p>${data[4]} ${data[5]}</p>
                    <p>${data[3]}</p>
                </div>
                <div class="panel-footer">
                    <button value="${data[1]}" type="button" class="btn btn-warning DealSendVista">Перевёл</button>
                </div>
            </div>`

    $('#control-wrapper').append(src);

    buttons = $('#control-wrapper').find('.DealSendVista');

    $(buttons[buttons.length - 1]).bind('click',
    function(){
        DealSendVista(this);
    });

}
function DealSendVista(button){
    $.post(url+"send_garant_deal",
    {
        'id': $(button).val()
    },
    onAjaxSuccess);
    function onAjaxSuccess(data){
        button.parentElement.parentElement.remove();
    }
}

function pasteReferralWithdrawal(data){
    if (data[3] === 'vusd'){currency = 'USD'}
    else{currency = 'EUR'}
    src = `<div class="panel panel-default">
                <div class="panel-heading">
                    Реферальный вывод пользователя №<a href="deals.html?${data[2]}">${data[2]}</a>
                </div>
                <div class="panel-body">
                    <p>${data[5]} ${currency}</p>
                    <p>${data[4]}</p>
                </div>
                <div class="panel-footer">
                    <button value="${data[1]}" type="button" class="btn btn-info ReferralWithdrawal">Перевёл</button>
                </div>
            </div>`

    $('#control-wrapper').append(src);

    buttons = $('#control-wrapper').find('.ReferralWithdrawal');

    $(buttons[buttons.length - 1]).bind('click',
    function(){
        ReferralWithdrawal(this);
    });

}
function ReferralWithdrawal(button){
    $.post(url+"allow_withdrawal",
    {
        'id': $(button).val()
    },
    onAjaxSuccess);
    function onAjaxSuccess(data){
        button.parentElement.parentElement.remove();
    }
}


function analyzeNotifications(){
    $.post(url+"display_analyze",
        {
            'dealCancel': dealCancel,
            'dealModerate': dealModerate,
            'askTimeOver': askTimeOver,
            'dealUserTimeOver': dealUserTimeOver,
            'dealTimeOver': dealTimeOver,
        },
        onAjaxSuccess);
        function onAjaxSuccess(data){
            pasteAnalyzeNotifications(JSON.parse(data));
            setTimeout(analyzeNotifications, 5000);
        }
}

function pasteAnalyzeNotifications(data){
    src = ''
    for (let i=0; i < data.length; i++){
        if (data[i][0] === 'dealCancel'){
            src += pasteAnalyzeDealCancel(data[i])
        }
        if (data[i][0] === 'dealModerate') {
            src += pasteAnalyzeDealModerate(data[i])
        }
        if (data[i][0] === 'dealUserTimeOver') {
            src += pasteAnalyzeUserTimeOver(data[i])
        }
        if (data[i][0] === 'dealOver') {
            src += pasteAnalyzeDealTimeOver(data[i])
        }
        if (data[i][0] === 'askOver') {
            src += pasteAnalyzeAskTimeOver(data[i])
        }
    }
    html_now = $('#analyze-wrapper').html();
    if (src !== html_now){
        $('#analyze-wrapper').html(src);
        if (html_now.length < src.length){
            notif();
        }
    }
}

function pasteAnalyzeDealCancel(data){
    return `<div class="panel panel-danger">
                <div class="panel-heading">
                    Сделка отменена №<a href="deals.html?${data[1]}">${data[2]}</a>
                </div>
            </div>`
}
function pasteAnalyzeDealModerate(data){
    return `<div class="panel panel-default">
                <div class="panel-heading">
                    Сделка требует модерирования №<a href="deals.html?${data[1]}">${data[2]}</a>
                </div>
            </div>`
}
function pasteAnalyzeUserTimeOver(data){
    return `<div class="panel panel-default">
                <div class="panel-heading">
                    Пользователь превысил время ожидания №<a href="deals.html?${data[1]}">${data[2]}</a>
                </div>
            </div>`
}
function pasteAnalyzeDealTimeOver(data){
    return `<div class="panel panel-default">
                <div class="panel-heading">
                    Слишком долгая сделка №<a href="deals.html?${data[1]}">${data[2]}</a>
                </div>
            </div>`
}
function pasteAnalyzeAskTimeOver(data){
    return `<div class="panel panel-default">
                <div class="panel-heading">
                    Слишком долгая заявка №<a href="asks.html?${data[1]}">${data[1]}</a>
                </div>
            </div>`
}


$(document).ready(function(){
    $('#controlFind').bind('click',
        function(){
            acceptAsks = $('#acceptAsks').is(':checked');
            dealGetVista = $('#dealGetVista').is(':checked');
            dealSendVista = $('#dealSendVista').is(':checked');
            referralWithdrawals = $('#referralWithdrawals').is(':checked');

            $('#controlCheckBox').remove();
            getControlNotifications();
        });

    $('#analyze').bind('click',
        function(){
            dealCancel = $('#dealCancel').is(':checked');
            dealModerate = $('#dealModerate').is(':checked');
            askTimeOver = $('#askTimeOver').is(':checked');
            dealUserTimeOver = $('#dealUserTimeOver').is(':checked');
            dealTimeOver = $('#dealTimeOver').is(':checked');

            $('#analyzeCheckBox').remove();
            analyzeNotifications();
        });

});