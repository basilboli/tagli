# -*- coding: utf-8 -*-
"""
    tagli Tests
    ~~~~~~~~~~~~
    Tests the tagli application.
    :copyright: (c) 2012 by basilboli
"""
import os
import unittest
from flask.ext.pymongo import PyMongo
from flask import Flask, request
from tagli import app, mongo
import configtest
from Mailer import Mailer 
from mock import MagicMock, call

class ApplicationTestCase(unittest.TestCase):
    nickname = "tagli"
    password = "tagli"
    email    = "support@tagli.io"

    def setUp(self):
        #configure application
        app.config.from_object("configtest")
        app.secret_key = configtest.SECRET

        self.app = app.test_client()

        mailer = Mailer(app)
        mailer.send_confirmation = MagicMock()
        
    def tearDown(self):
        #drop the database
        with app.app_context():
            db = container[constants.IOC_DATABASE]
            db.cx.drop_database(configtest.MONGO_DBNAME)

    def register(self, nickname, password, email, agerange):
        """Helper function to register a user"""
        rd = self.app.post('/doregister', data={'nickname' : nickname, 'agerange' : agerange, 'password': password, 'email': email }, follow_redirects=True)
        mailer = container[constants.IOC_MAILER] 

        with app.app_context():
            user = container[constants.IOC_DATABASE].db.users.find_one({'user_id': self.email})            
            #assert registration email has been sent
            mailer.send_confirmation.assert_called_once_with(self.email, self.nickname, user['hashcode'])

        return rd

    # def confirm(self, email):
    #     with app.app_context():
    #         user = container[constants.IOC_DATABASE].db.users.find_one({'user_id': self.email})
    #         return self.app.get('/doconfirm/' + user['hashcode'], data={}, follow_redirects = True)

    # def logout(self):
    #     return self.app.post('/dologout', data={}, follow_redirects = True)

    # def login(self, email, password):
    #     return self.app.post('/dologin', data={'email' : email, 'password' : password}, follow_redirects = True)

    # def register_confirm(self, nickname, password, email, agerange):
    #     self.register(nickname, password, email, agerange)
    #     return self.confirm(email)

    # def test_register_confirm(self):
    #     #test registration failed with the parameters
    #     rv = self.register(self.nickname, self.password, self.email, self.agerange)

    #     #check the user is created
    #     with app.app_context():
    #         user = container[constants.IOC_DATABASE].db.users.find_one({'user_id' : self.email})
    #         assert constants.UserStatus.Default == user['status']
    #         assert "feed" in rv.data

    #     #check the mailer has sent an invitation letter
    #     #check the user is redirected to the "/feed" page
    #     #test registration failed with the parameters

    #     reply = self.confirm(self.email)
    #     with app.app_context():
    #         user = container[constants.IOC_DATABASE].db.users.find_one({'user_id': self.email})
    #         assert user['status'] == constants.UserStatus.Active
    #         assert "feed" in reply.data

    # def test_login(self):
    #     self.register(self.nickname, self.password, self.email, self.agerange)
    #     self.logout()

    #     #confirmation required
    #     rv = self.login(self.email, self.password)
    #     mailer = container[constants.IOC_MAILER]

    #     #there should have been two email sent. One during the registration, and another one when 
    #     #the user entered the data incorrectly
    #     with app.app_context():
    #         user = container[constants.IOC_DATABASE].db.users.find_one({'user_id': self.email})
    #         expected = [call(self.email, self.nickname, user['hashcode']), call(self.email, self.nickname, user['hashcode'])]
    #         mailer.send_confirmation.call_args_list = expected

    #     assert "votre email" in rv.data

    #     #confirm email
    #     self.confirm(self.email)
    #     self.logout()

    #     #test email incorrect
    #     rv = self.login(self.email + "error", self.password)
    #     assert "Re-essayer login" in rv.data

    #     #test password incorrect
    #     rv = self.login(self.email, self.password + "error")
    #     assert "Re-essayer login" in rv.data

    #     #test login successful
    #     rv = self.login(self.email, self.password)
    #     assert "feed" in rv.data
    #     self.logout()

    # def test_registration_details_incorrect():
    #     pass

    # def test_retry_login(self):
    #     pass

    # def test_reset_password(self):
    #     pass

if __name__ == '__main__':    
    unittest.main()
