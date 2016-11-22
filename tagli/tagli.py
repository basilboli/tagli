#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Tagli
    ~~~~~~~~
    online tags app
    :copyright: (c) 2012 by basilboli
    prohibited by real patsan's law.
"""

from flask import Flask, request, redirect, render_template, url_for, flash, abort, session, g, flash,_app_ctx_stack
from bson.objectid import ObjectId
from flask.ext.pymongo import PyMongo
from werkzeug import check_password_hash, generate_password_hash
from jinja2 import TemplateNotFound
import datetime
import uuid
from Mailer import Mailer
from urlparse import urlparse, urljoin
import stripe
import os

from wtforms import Form, BooleanField, StringField, SelectField, validators

stripe_keys = {
    'secret_key': os.environ['LIVE_SECRET_KEY'],
    'publishable_key': os.environ['LIVE_PUBLISHABLE_KEY']
}

stripe.api_key = stripe_keys['secret_key']

# configuration
DATABASE = 'tagli'

app = Flask(__name__)
app.secret_key = 'tagli'
mongo  = PyMongo(app)
mail = Mailer() 

def check_code(form, field):
    code = mongo.db.codes.find_one({"code_hash": field.data})
    tag = mongo.db.tags.find_one({"code_hash": field.data})
    if code is None:
        raise validators.ValidationError('Seems to be not existing code. Please take look at the sticker code')    
    elif tag is not None:
        raise validators.ValidationError('Already used by someone. Try another one.')   

class TagForm(Form):
    type         = SelectField('Your object category', choices=[('laptop', 'Laptop'), ('mobile-phone', 'Mobile'), ('key', 'Keys'), ('briefcase', 'Document'), ('heart', 'Other')])
    name         = StringField('Name', [validators.Length(min=1, max=50, message=(u'Seems to be too long or empty'))])
    price        = StringField('Reward', [validators.Length(min=1, max=1000, message=(u'Seems to be too long or empty'))])
    code         = StringField('Code', [validators.Length(min=4, max=5, message=(u'Seems to be too long or empty')), check_code])

def is_empty(value):
    return value is None or len(value) == 0 


#REQUESTS HANDLING
@app.before_request
def before_request():
    g.user = None #request user
    if session and 'user_id' in session:
        g.user = mongo.db.users.find_one({"user_id": session['user_id']})  

@app.route('/<code>')
def show(code):
    print ("yo")
    print("Checking tag code %s" % code)
    if code.startswith('x'):
        tag = mongo.db.tags.find_one({'code_hash':code, 'is_active': True})
        print("Found tag %s" % tag)
        if tag:
            return render_template('tag.html',tag = tag)
        else:
            return render_template('404.html')
    else:
        try:
            return render_template('%s.html' % code)
        except TemplateNotFound:
            return render_template('404.html')

@app.route('/')
def _home():
    if g.user:
        return redirect("/tags")
    return render_template('index.html')

@app.route('/signin')
def _signin():
    if g.user:
        return redirect("/tags")
    return render_template('signin.html', next=request.values.get('next'))

@app.route('/signup')
def _signup():
    if g.user:
        return redirect("/tags")
    return render_template('signup.html', next=request.values.get('next'))


@app.route('/shop')
def shop():
    return render_template('shop.html', key=stripe_keys['publishable_key'])

@app.route('/charge', methods=['POST'])
def charge():
    # Amount in cents
    amount = 399

    customer = stripe.Customer.create(
        email=request.form['stripeEmail'],
        card=request.form['stripeToken']
    )

    charge = stripe.Charge.create(
        customer=customer.id,
        amount=amount,
        currency='eur',
        description='Tagli 4 stickers'
    )
    mail.checkout(request.form['stripeEmail'])
    return render_template('charge.html', amount=amount)    


@app.route('/dosignin',methods=['POST'])
def dosignin():
    error = None
    print("Signin in")
    next = request.form['next']
    print("Next url is : %s" % next)
    print("email is : %s" % request.form['email'])
    print("password is : %s" % request.form['password'])
    if g.user:
        return redirect("/tags")
    if request.method == 'POST':
        if not request.form['email'] or '@' not in request.form['email']:
            error = 'You have to enter a valid email address'
        elif not request.form['password']:
            error = 'You have to enter a password'
        else:
            user = mongo.db.users.find_one({"email": request.form['email']})
            if user is None:
                error = 'Invalid username'
            elif not check_password_hash(user['password'],request.form['password']):
                error = 'Invalid password'
            else:
                flash('Hey pal! Hope you are having a great day! ')
                session['user_id'] = user['email']
                return redirect(next or ('/tags'))
    return render_template('signin.html', error=error)

@app.route('/dosignup',methods=['POST'])
def dosignup():
    error = None
    print("Signing up ...")
    next = request.form['next']
    print("Next url is : %s" % next)

    print(request.form['email'])
    if g.user:
        return redirect(url_for('tags'))
    if request.method == 'POST':
        if not request.form['name']:
            error = 'Please provider provide your name'
        elif not request.form['email'] or '@' not in request.form['email']:
            error = 'Please provider provide your valid email address'
        elif not request.form['password']:
            error = 'Please provider provide your password'
        elif mongo.db.users.find_one({"email": request.form['email']}) is not None:
            error = 'User with a given email already exists'    
        else:
            #create a new user
            # hashcode = str(uuid.uuid4())
            mongo.db.users.insert({"user_id": request.form['email'],
                                     "name": request.form['name'],
                                     "email": request.form['email'],
                                     "password": generate_password_hash(request.form['password'])})

            #open user session
            session['user_id'] = request.form['email'] 
            mail.welcome(request.form['email'] )
            flash('You were successfully registered!')
            return redirect(next or '/tags')
    return render_template('signup.html', error=error)


@app.route('/tags')
def showtags():
    if g.user:
        print("Checking tags ...")
        tags_count = mongo.db.tags.find({'user_id':g.user['user_id']}).count()
        tags = mongo.db.tags.find({'user_id':g.user['user_id']})
        print("Found {0} tags for user {1} ".format(tags_count, g.user))
        return render_template('tags.html',tags = tags, tags_count=tags_count)
    else:
        return redirect('/')    


@app.route('/tag')
def newtag():
    print("Adding new tag ...")
    form = TagForm()
    return render_template('newtag.html',form = form)

@app.route('/newtag', methods=['POST'])
def newtag():

    print("creating new tag with data :")
    form = TagForm(request.form)
    
    print("type %s" % form.type.data.encode('utf-8'))
    print("name %s" % form.name.data.encode('utf-8'))    
    print("price %s" % form.price.data.encode('utf-8'))    
    print("code %s" % form.code.data.encode('utf-8'))    
    
    if request.method == 'POST' and form.validate():
        new_tag = dict(
            type         = form.type.data,
            name         = form.name.data,
            code_hash    = form.code.data,
            price        = form.price.data,
            create_dt    = datetime.datetime.now(),
            is_active    = True,
            user_id      = g.user['user_id']
        )
        print("REGISTERING new tag %s" % new_tag)
        mongo.db.tags.insert(new_tag)
        print("New tag is ADDED!")
        flash('Woohoo, new tag has been added!')
        mail.newtag(g.user['user_id'])
        return redirect('tags')
    return render_template('newtag.html',form=form)

@app.route('/tag/delete', methods=['POST'])
def tag_id_delete():
    # delete the tag
    print('Deleting tag by id %s' % request.form['tagId'])
    mongo.db.tags.remove({'_id': ObjectId(request.form['tagId'])})
    flash('Your tag is deleted!')
    return redirect('/tags')

@app.route('/tag/<id>/activate', methods=['GET','POST'])
def tag_id_activate(id):
    # delete the tag
    print('Activating tag by id %s' % id)
    tag = mongo.db.tags.find_one_or_404({'_id': ObjectId(id)})
    tag['is_active'] = True
    print('Tag status is  %s' % tag['is_active'])
    mongo.db.tags.update({'_id': ObjectId(id)}, tag)
    flash('Your tag "%s" is ON again! Other people can contact you using tag address.' % tag['name'])
    return redirect('/tags')

@app.route('/tag/<id>/deactivate', methods=['GET','POST'])
def tag_id_deactivate(id):
    # delete the tag
    print('Deactivating tag by id %s' % id)
    tag = mongo.db.tags.find_one_or_404({'_id': ObjectId(id)})
    tag['is_active'] = False
    print('Tag status is  %s' % tag['is_active'])
    mongo.db.tags.update({'_id': ObjectId(id)}, tag)
    flash('Your tag "%s" is muted! You will not receive any notifications for this object.' % tag['name'])
    return redirect('/tags')

@app.route('/tag/<id>/edit', methods=['GET'])
def tag_edit_get(id):
    # edit the tag
    print('Editing tag by id %s' % id)
    form = TagForm()
    tag = mongo.db.tags.find_one_or_404({'_id': ObjectId(id)})
    return render_template('edittag.html',form = form, tag = tag)

@app.route('/tag/<id>/edit', methods=['POST'])
def tag_edit_post(id):
    # edit the tag
    print('Editing tag by id %s' % id)
    tag = mongo.db.tags.find_one_or_404({'_id': ObjectId(id)})
    form = TagForm(request.form)
    
    print("type %s" % form.type.data.encode('utf-8'))
    print("name %s" % form.name.data.encode('utf-8'))    
    print("price %s" % form.price.data.encode('utf-8'))    
    print("code %s" % form.code.data.encode('utf-8'))    
    
    if request.method == 'POST' and form.validate():
        tag['type'] = form.type.data
        tag['name'] = form.name.data
        tag['price'] = form.price.data
        tag['code_hash'] = form.code.data

        print("Updating tag %s" % tag)
        mongo.db.tags.update(tag)
        flash('Done!')
        return redirect('tags')
    return render_template('edittag.html', form=form)    

@app.route('/search',methods=['POST'])
def searchtag():
    print("Checking tags ...")
    tags = mongo.db.tags.find()
    return render_template('tags.html',tags = tags)


@app.route('/domessage/<conversation_id>', methods=['POST'])
def domessage(conversation_id):
    print "yo domessage"   
    tag_id = request.form['tag_id']
    print("posting new message for tag %s" % tag_id)
    tag = mongo.db.tags.find_one({'_id': ObjectId(tag_id)})
    new_message = dict(
            from_user_id         = g.user['email'],
            to_user_id           = tag['user_id'],
            post_dt              = datetime.datetime.now(),
            text                 = request.form['text']
        )

    # start new conversation
    if conversation_id == 'new' :
        print("creating new conversation ...")
        new_conversation    = dict(
            from_user_id         = g.user['email'],
            to_user_id           = tag['user_id'],
            post_dt              = datetime.datetime.now(),
            messages             = [new_message],
            count                = 1,
            tag                  = tag,
            )
        print("Registering new conversation %s" % new_conversation)
        conversation_id = str(mongo.db.conversations.insert(new_conversation))
        print("New conversation is registered: %s" % conversation_id)
    else :
        print("Posting new message ...")
        mongo.db.conversations.update({'_id': ObjectId(conversation_id)},{'$push':{'messages':new_message},'$inc': {'count': 1 }})
        print("New message is ADDED!")
    if (tag['user_id'] == g.user['email']):
        flash('You message has been sent! We will let you know as soon as the person read it')    
    else :
        flash('You message has been sent to the owner! We will let you know as soon as the owner read it')            
    mail.newmessage(tag['user_id'])    
    return redirect('conversation/' + conversation_id)

@app.route('/conversations')
def show_conversations():
    print("Loading conversations ...")
    conversations = mongo.db.conversations.find({ "$or" :
            [ { "from_user_id" : g.user['user_id'] } ,{ "to_user_id": g.user['user_id'] } ] }).sort('messages.post_dt', -1)
    return render_template('conversations.html',conversations = conversations)


@app.route('/conversation/<conversation_id>')
def show_conversation(conversation_id):
    print("Loading messages by conversation_id ... %s" % conversation_id)
    conversation = mongo.db.conversations.find_one_or_404({'_id': ObjectId(conversation_id)})
    print('conversation found %s' % conversation)
    return render_template('messages.html', conversation = conversation)

@app.route('/logout')
def logout():
    if 'user_id' in session:
        del session['user_id']
    print('Session details : %s' % session)
    return redirect("/")             

if __name__ == '__main__':
    app.run('0.0.0.0',debug=True)    