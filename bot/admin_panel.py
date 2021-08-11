import datetime
from flask import Flask, request, Response
import json

import screens

from classes import Asks, Users, Data, Deals, ReferralWithdrawal
Asks = Asks()
Users = Users()
Data = Data()
Deals = Deals()
ReferralWithdrawal = ReferralWithdrawal()


class Admin_panel:
    def __init__(self, config):
        self.username = 'admin'
        self.password = 'hk~|mpe?'

        self.app = Flask(__name__)

        self.auth = ['127.0.0.1']

        self.Bot = config.Bot

    def initiate(self):
        self.set()
        import config
        self.app.run(host = config.addr)

    def set(self):
        @self.app.before_request
        def before_request():
            ip = request.remote_addr
            # auth
            if 'url' in request.form:
                if request.form['url'] == 'auth':
                    name = request.form['name']
                    pas = request.form['password']

                    if name == self.username and pas == self.password:
                        self.auth.append(request.remote_addr)
                        return Response('ok')
                    else:
                        return Response('{"kod":"1"}')
                else:
                    return Response('NOT_AUTH')

            # check auth
            else:
                if ip in self.auth:
                    pass
                else:
                    return Response('NOT_AUTH')

        @self.app.route("/index", methods = ['POST'])
        def index():
            return Response(json.dumps({
                'users': Users.amount(),
                'asks': Asks.amount(),
                'deals': Deals.amount(),
            }))

        # USERS
        @self.app.route("/get_users", methods = ['POST'])
        def get_users():
            return Response(json.dumps(Users.getUsers(output = 'web')))

        @self.app.route("/get_user", methods = ['POST'])
        def get_user():
            trade_id = request.form['id']
            user = Users.identification(tradeId = trade_id)
            return Response(json.dumps(user.to_json()))

        @self.app.route("/change_user", methods = ['POST'])
        def change_user():
            tg_id = request.form['tg_id']
            type = request.form['type']
            user = Users.identification(telegramId = tg_id)
            if not user:
                return Response('false')

            if type == 'ban':
                if user.ban:
                    user.ban = 0
                else:
                    user.ban = 1

            elif type == 'rating':
                count = request.form['count']
                if not count.isdigit():
                    return Response('false')
                user.rating = int(count)

            return Response('true')

        # ASKS
        @self.app.route("/get_asks", methods = ['POST'])
        def get_asks():
            return Response(json.dumps(Asks.getAsks(preview='web')))

        @self.app.route("/get_ask", methods = ['POST'])
        def get_ask():
            ask_id = int(request.form['id'])
            return Response(json.dumps(Asks.getAsk(ask_id).to_json()))

        @self.app.route("/allow_ask", methods = ['POST'])
        def allow_ask():
            ask_id = int(request.form['ask_id'])
            ask = Asks.getAsk(ask_id)
            ask.setStatus('ok')

            user = Users.identification(tradeId = ask.trade_id_owner)
            self.Bot.send_screen(user, screens.create_asks('admin_public', user, Ask = ask))

            ret = '{ok}'

            return Response(json.dumps(ret))

        @self.app.route("/delete_ask", methods = ['POST'])
        def delete_ask():
            ask_id = int(request.form['ask_id'])

            ask = Asks.getAsk(ask_id)
            user = Users.identification(tradeId = ask.trade_id_owner)
            self.Bot.send_screen(user, screens.create_asks('admin_unpublic', user, Ask = ask))

            ask.setStatus('removed')
            ret = '{ok}'

            return Response(json.dumps(ret))

        # DEALS
        @self.app.route("/get_deals", methods = ['POST'])
        def get_deals():
            return Response(json.dumps(Deals.getDeals('web', active = 'work')))

        @self.app.route("/get_deal", methods = ['POST'])
        def get_deal():
            id = request.form['id']
            Deal = Deals.getDeal(id)
            return Response(json.dumps(Deal.to_json()))

        @self.app.route("/remove_deal", methods = ['POST'])
        def remove_deal():
            id = request.form['id']
            Deals.getDeal(id).updateStatus('remove')
            return Response(json.dumps('ok'))

        @self.app.route("/accept_garant_deal", methods = ['POST'])
        def accept_garant_deal():
            id = request.form['id']
            Deal = Deals.getDeal(id)
            Deal.logic_control('garant_accept', 'admin')

            self.Bot.notification_deal_users(Deal)

            return Response(json.dumps('ok'))

        @self.app.route("/send_garant_deal", methods = ['POST'])
        def send_garant_deal():
            id = request.form['id']
            Deal = Deals.getDeal(id)
            Deal.logic_control('garant_send', 'admin')

            self.Bot.notification_deal_users(Deal)
            referralMessage, newAsk = Deal.end()
            if referralMessage['referral_A']:
                self.Bot.send_screen(referralMessage['referral_A'], screens.referral('bonus', referralMessage['commission'], referralMessage['commissionCurrency']))
            if referralMessage['referral_B']:
                self.Bot.send_screen(referralMessage['referral_B'], screens.referral('bonus', referralMessage['commission'], referralMessage['commissionCurrency']))

            if newAsk:
                Asks.addAsk(oldAsk = newAsk)

            return Response(json.dumps('ok'))

        @self.app.route("/notification_deal", methods = ['POST'])
        def notification_deal():
            id = request.form['id']
            pos = request.form['position']
            Deal = Deals.getDeal(id)
            if pos == 'A':
                user_A = Users.identification(telegramId = Deal.vista_people)
                screen_A = Deal.logic_message(user_A)
                if screen_A:
                    self.Bot.send_screen(user_A, screen_A)
            else:
                user_B = Users.identification(telegramId = Deal.fiat_people)
                screen_B = Deal.logic_message(user_B)
                if screen_B:
                    self.Bot.send_screen(user_B, screen_B)

            return Response(json.dumps('ok'))

        @self.app.route("/continue_deal", methods = ['POST'])
        def continue_deal():
            id = request.form['id']
            Deal = Deals.getDeal(id)
            Deal.cancel = 0
            Deal.moderate = 0
            self.Bot.notification_deal_users(Deal)

            return Response(json.dumps('ok'))

        # SETTINGS
        @self.app.route("/get_settings", methods = ['POST'])
        def get_settings():
            return Response(json.dumps(Data.to_json()))

        @self.app.route("/set_settings", methods = ['POST'])
        def set_settings():
            Data.perc_vst = float(request.form['perc_vst'])
            Data.perc_fiat = float(request.form['perc_fiat'])
            Data.faq = json.loads(request.form['faq'])
            Data.card_usd = request.form['card_usd']
            Data.card_eur = request.form['card_eur']

            return Response(json.dumps({'ok': 1}))

        # REFERRAL WITHDRAWAL
        @self.app.route("/get_withdrawals", methods = ['POST'])
        def get_withdrawals():
            return Response(json.dumps(ReferralWithdrawal.getWait()))

        @self.app.route("/allow_withdrawal", methods = ['POST'])
        def allow_withdrawal():
            id = int(request.form['id'])
            ReferralWithdrawal.done(id)
            return Response('ok')

        # OLD DEALS
        @self.app.route("/get_old_deals", methods = ['POST'])
        def get_old_deals():
            idOwner = int(request.form['id'])
            if idOwner == -1:
                idOwner = None

            date1 = request.form['date1']
            date2 = request.form['date2']

            if date1 != '':
                date1 = datetime.datetime.strptime(date1, '%d.%m.%Y %H:%M').timestamp()
            if date2 != '':
                date2 = datetime.datetime.strptime(date2, '%d.%m.%Y %H:%M').timestamp()
            print(date1, date2)
            return Response(json.dumps(Deals.getDeals(preview = 'end', idOwner = idOwner, active = 'end', date = (date1, date2))))

        @self.app.after_request
        def after_request(response):
            header = response.headers
            header['Access-Control-Allow-Origin'] = '*'
            return response
