# CONFIGURATION FILE
DEBUG           = True
DATABASE        = "tagli"
SECRET          = "tagli"
GOOGLE_MAP_KEY  = "BLABLA"
TWITTER = dict(
    consumer_key='',
    consumer_secret=''
)

EMAIL_FROM="BLABLA"

MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = "BLABLA"
MAIL_PASSWORD = "BLABLA"

DOMAIN_NAME = "localhost:5000"
#EMAIL CONFIGURATION OPTIONS
EMAIL_CONF_SUBJ_FR	= "Bienvenue chez Tagli"
EMAIL_PWD_FR = "Pour changer votre mot de passe "

SITE_URL = "http://" + DOMAIN_NAME

class UserStatus:
    Default, Blocked, Active, Inactive = {"UNCONFIRMED", "BLOCKED", "ACTIVE", "INACTIVE"}