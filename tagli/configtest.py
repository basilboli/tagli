# CONFIGURATION FILE
DEBUG           = True
MONGO_DBNAME    = "tagli-test"
SECRET          = "tagli"
GOOGLE_MAP_KEY  = "AIzaSyBp38HrCDKnnLzddo9VO8YhWuzUdvkcX-g"
TESTING			= True
TWITTER = dict(
    consumer_key='',
    consumer_secret=''
)
HOST=http://tagli.io/
EMAIL_FROM="opteamis@gmail.com"

MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = "opteamis@gmail.com"
MAIL_PASSWORD = "AZER1234"

DOMAIN_NAME = "localhost:5000"
#EMAIL CONFIGURATION OPTIONS
EMAIL_CONF_SUBJ_FR	= "Bienvenue chez Tagli"
EMAIL_PWD_FR = "Pour changer votre mot de passe "

SITE_URL = "http://" + DOMAIN_NAME

class UserStatus:
    Default, Blocked, Active, Inactive = {"UNCONFIRMED", "BLOCKED", "ACTIVE", "INACTIVE"}