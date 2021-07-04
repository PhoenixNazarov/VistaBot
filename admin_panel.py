import flask
from flask import Flask, request, Response
import json

import services


class Admin_panel:
    def __init__(self, config):
        self.username = 'admin'
        self.password = ''

        self.app = Flask(__name__)

        self.auth = ['127.0.0.1']

        self.Users = config.Users
        self.Bot = config.Bot
        self.Asks = config.Asks
        self.Data = config.Data
        self.Deals = config.Deals

    def initiate(self):
        self.set()
        self.app.run()

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

        # USERS
        @self.app.route("/get_users", methods = ['POST'])
        def get_users():
            return Response(self.Users.get_users())

        @self.app.route("/get_user", methods = ['POST'])
        def get_user():
            trade_id = request.form['id']
            user = self.Users.get_user(trade_id)
            if not user:
                return Response('false')

            js = user.to_json()
            # referrals
            referrals = []
            for i in user.referal_list:
                ref_user = self.Users.tg_id_identification(i)
                referrals.append([ref_user.trade_id, ref_user.fio])

            js.update({'referrals': referrals})
            if user.referal_to:
                js.update({'main_referral': self.Users.tg_id_identification(user.referal_to).trade_id})

            # cards
            cards = []
            for i in user.cards:
                cards.append(i.collect_full('web'))
            js.pop('cards')
            js.update({'cards': cards})

            return Response(json.dumps(js))

        @self.app.route("/change_user", methods = ['POST'])
        def change_user():
            tg_id = request.form['tg_id']
            type = request.form['type']
            user = self.Users.tg_id_identification(int(tg_id))
            if not user:
                return Response('false')

            if type == 'ban':
                if user.ban:
                    user.ban = False
                else:
                    user.ban = True

            elif type == 'rating':
                count = request.form['count']
                if not count.isdigit():
                    return Response('false')
                user.rating = int(count)

            return Response('true')

        # ASKS
        @self.app.route("/get_asks", methods = ['POST'])
        def get_asks():
            return Response(json.dumps(self.Asks.get_asks_web()))

        @self.app.route("/get_ask", methods = ['POST'])
        def get_ask():
            ask_id = int(request.form['id'])
            ask = self.Asks.get_ask_from_id(ask_id)
            ret = ask.to_json()
            ret.update({'web': ask.web()})
            ret.update({'vst_card': ask.vst_card.collect_full('web')})
            ret.update({'fiat_cards': [i.collect_full('web') for i in ask.fiat_cards]})
            ret.update({'fiat_banks': '<br>'.join(ask.fiat_banks)})

            return Response(json.dumps(ret))

        @self.app.route("/allow_ask", methods = ['POST'])
        def allow_ask():
            ask_id = int(request.form['ask_id'])
            ask = self.Asks.get_ask_from_id(ask_id)
            ask.status = 'ok'
            ret = '{ok}'

            return Response(json.dumps(ret))

        @self.app.route("/delete_ask", methods = ['POST'])
        def delete_ask():
            ask_id = int(request.form['ask_id'])
            self.Asks.remove_ask(ask_id)
            ret = '{ok}'

            return Response(json.dumps(ret))

        # DEALS
        @self.app.route("/get_deals", methods = ['POST'])
        def get_deals():
            return Response(json.dumps(self.Deals.get_deals_for_web()))

        @self.app.route("/get_deal", methods = ['POST'])
        def get_deal():
            id = request.form['id']
            Deal = self.Deals.get_deal(id)
            acp = Deal.to_json()
            acp['a_vst_card'] = Deal.vista_people_vst_card.collect_full('web')
            acp['b_vst_card'] = Deal.fiat_people_vst_card.collect_full('web')
            acp['g_vst_card'] = Deal.garant_card().replace('\n','<br>')
            acp['a_trade_id'] = self.Users.tg_id_identification(Deal.vista_people).trade_id
            acp['b_trade_id'] = self.Users.tg_id_identification(Deal.fiat_people).trade_id
            return Response(json.dumps(acp))

        @self.app.route("/remove_deal", methods = ['POST'])
        def remove_deal():
            id = request.form['id']
            Deal = self.Deals.remove_deal(id)
            return Response(json.dumps('ok'))

        @self.app.route("/accept_garant_deal", methods = ['POST'])
        def accept_garant_deal():
            id = request.form['id']
            Deal = self.Deals.get_deal(id)
            Deal.logic_control('garant_accept', 'admin')

            self.Bot.notification_deal_users(Deal)

            return Response(json.dumps('ok'))

        @self.app.route("/send_garant_deal", methods = ['POST'])
        def send_garant_deal():
            id = request.form['id']
            Deal = self.Deals.get_deal(id)
            Deal.logic_control('garant_send', 'admin')

            self.Bot.notification_deal_users(Deal)

            self.Deals.remove_deal(Deal.id)

            return Response(json.dumps('ok'))

        @self.app.route("/notification_deal", methods = ['POST'])
        def notification_deal():
            id = request.form['id']
            pos = request.form['position']
            Deal = self.Deals.get_deal(id)
            if pos == 'A':
                user_A = self.Users.tg_id_identification(Deal.vista_people)
                screen_A = Deal.logic_message(user_A)
                if screen_A:
                    self.Bot.send_screen(user_A, screen_A)
            else:
                user_B = self.Users.tg_id_identification(Deal.fiat_people)
                screen_B = Deal.logic_message(user_B)
                if screen_B:
                    self.Bot.send_screen(user_B, screen_B)

            return Response(json.dumps('ok'))

        # SETTINGS
        @self.app.route("/get_settings", methods = ['POST'])
        def get_settings():
            return Response(json.dumps(self.Data.to_json()))

        @self.app.route("/set_settings", methods = ['POST'])
        def set_settings():
            self.Data.perc_vst = float(request.form['perc_vst'])
            self.Data.perc_fiat = float(request.form['perc_fiat'])
            self.Data.faq = json.loads(request.form['faq'])
            self.Data.card_usd = request.form['card_usd']
            self.Data.card_eur = request.form['card_eur']

            return Response(json.dumps({'ok': 1}))

        @self.app.after_request
        def after_request(response):
            header = response.headers
            header['Access-Control-Allow-Origin'] = '*'
            return response