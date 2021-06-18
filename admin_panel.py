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

        @self.app.after_request
        def after_request(response):
            header = response.headers
            header['Access-Control-Allow-Origin'] = '*'
            return response