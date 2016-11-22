# from flask_mail import Mail
# from flask_mail import Message
import config
import logging
import requests

# Mailer class provides mailing service using mailgun api
class Mailer:
	logger = logging.getLogger('app')
	url   = "https://api.mailgun.net/v2/tagli.io/messages"
	token = "key-4ut65uvelj2cjucyl3x4o-lrvazmpe-9"
	_from = "Tagli Team <welcome@tagli.io>"

	def load_template(self, filename):
		f = open("./emails/" + filename)
		file_content = f.read()
		f.close()
		return file_content	

	def welcome(self, to):
		return self.send("Welcome to Tagli Club!", "welcome.html", to)

	def newmessage(self, to):
		return self.send("You have new message!", "newmessage.html", to)	

	def newtag(self, to):
		return self.send("Bravo!", "newtag.html", to)		

	def checkout(self, to):
		return self.send("Great!", "checkout.html", to)			

	def send(self, subject, template, to):
		file_content = self.load_template(template)
		message = requests.post(
	        self.url,
	        auth=("api", self.token),
	        data={"from": self._from,
	              "to": [to],
	              "bcc": "basilboli+tagli@gmail.com",
	              "subject": subject,
	              "html": file_content})
		print message.text	
		return	