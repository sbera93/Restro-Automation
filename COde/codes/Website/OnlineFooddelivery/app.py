from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, SelectField
from passlib.hash import sha256_crypt
from functools import wraps
from flask_uploads import UploadSet, configure_uploads, IMAGES
import timeit
import datetime
from flask_mail import Mail, Message
import os
from wtforms.fields.html5 import EmailField
import qrcode
import csv
from gettingrecommendations import *
from locationFromUser import *
app = Flask(__name__)
app.secret_key = os.urandom(24)
#app.config['UPLOADED_PHOTOS_DEST'] = 'static/image/product'
app.config['UPLOADED_PHOTOS_DEST'] = 'static/foodimages'
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

# app.config['UPLOADED_QR_DEST'] = 'static/qrimages'
# qrphotos = UploadSet('photos', IMAGES)
# configure_uploads(app, qrphotos)

# Config MySQL
mysql = MySQL()
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'onlinefooddelivery'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# Initialize the app for use with this MySQL class
mysql.init_app(app)


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, *kwargs)
        else:
            return redirect(url_for('login'))
    return wrap


def not_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return redirect(url_for('index'))
        else:
            return f(*args, *kwargs)
    return wrap


def is_admin_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'admin_logged_in' in session:
            return f(*args, *kwargs)
        else:
            return redirect(url_for('admin_login'))
    return wrap


def not_admin_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'admin_logged_in' in session:
            return redirect(url_for('admin'))
        else:
            return f(*args, *kwargs)
    return wrap


def is_ruser_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'ruser_logged_in' in session:
            return f(*args, *kwargs)
        else:
            return redirect(url_for('ruser_login'))
    return wrap


def not_ruser_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'ruser_logged_in' in session:
            return redirect(url_for('ruser'))
        else:
            return f(*args, *kwargs)
    return wrap


def wrappers(func, *args, **kwargs):
    def wrapped():
        return func(*args, **kwargs)
    return wrapped

@app.route('/')
@app.route('/index')
def index():

    form = OrderForm(request.form)
    # Create cursor
    cur = mysql.connection.cursor()
    values = 'fastfood'
    cur.execute("SELECT * FROM groceryname WHERE category=%s and imagename != ''", (values,))
    fruit = cur.fetchall()
    values = 'chinesse'
    cur.execute("SELECT * FROM groceryname WHERE category=%s and imagename != ''", (values,))
    bakery = cur.fetchall()
    values = 'rice'
    cur.execute("SELECT * FROM groceryname WHERE category=%s and imagename != ''", (values,))
    home = cur.fetchall()
    #recommendation={}
    userid=3#int(session['uid'])
    cur.execute("SELECT * FROM groceryname")
    allitem = cur.fetchall()
    allitemreplica=allitem
    idsofall=[]
    for allid in allitemreplica:
        idofprod=allid['id']
        if idofprod<5:
            opof=dataofuseroutput(userid,idofprod) 
            if opof>3.5:
                idsofall.append(idofprod)
    t = tuple(idsofall)
    query = "select * from groceryname where id IN {}".format(t)
    cur.execute(query)
    recommendation = cur.fetchall()
    print(recommendation)
    cur.close()
    return render_template('home.html', fruit=fruit, bakery=bakery, home=home,recommendation=recommendation, form=form)


class LoginForm(Form):  # Create Login Form
    username = StringField('', [validators.length(min=1)],
                           render_kw={'autofocus': True, 'placeholder': 'Username'})
    password = PasswordField('', [validators.length(min=3)],
                             render_kw={'placeholder': 'Password'})


# User Login
@app.route('/login', methods=['GET', 'POST'])
@not_logged_in
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        # GEt user form
        username = form.username.data
        # password_candidate = request.form['password']
        password_candidate = form.password.data

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM users WHERE username=%s", [username])

        if result > 0:
            # Get stored value
            data = cur.fetchone()
            password = data['password']
            uid = data['id']
            name = data['name']

            # Compare password
            if sha256_crypt.verify(password_candidate, password):
                # passed
                session['logged_in'] = True
                session['uid'] = uid
                session['s_name'] = name
                x = '1'
                cur.execute("UPDATE users SET online=%s WHERE id=%s", (x, uid))

                return redirect(url_for('index'))

            else:
                flash('Incorrect password', 'danger')
                return render_template('login.html', form=form)

        else:
            flash('Username not found', 'danger')
            # Close connection
            cur.close()
            return render_template('login.html', form=form)
    return render_template('login.html', form=form)


@app.route('/out')
def logout():
    if 'uid' in session:
        # Create cursor
        cur = mysql.connection.cursor()
        uid = session['uid']
        x = '0'
        cur.execute("UPDATE users SET online=%s WHERE id=%s", (x, uid))
        session.clear()
        flash('You are logged out', 'success')
        return redirect(url_for('index'))
    return redirect(url_for('login'))


class RegisterForm(Form):
    name = StringField('', [validators.length(min=3, max=50)],
                       render_kw={'autofocus': True, 'placeholder': 'Full Name'})
    username = StringField('', [validators.length(min=3, max=25)], render_kw={'placeholder': 'Username'})
    email = EmailField('', [validators.DataRequired(), validators.Email(), validators.length(min=4, max=25)],
                       render_kw={'placeholder': 'Email'})
    password = PasswordField('', [validators.length(min=3)],
                             render_kw={'placeholder': 'Password'})
    mobile = StringField('', [validators.length(min=11, max=15)], render_kw={'placeholder': 'Mobile'})


@app.route('/register', methods=['GET', 'POST'])
@not_logged_in
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        mobile = form.mobile.data
        # Create Cursor
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(name, email, username, password, mobile) VALUES(%s, %s, %s, %s, %s)",
                    (name, email, username, password, mobile))
        # Commit cursor
        mysql.connection.commit()
        # Close Connection
        cur.close()
        flash('You are now registered and can login', 'success')
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


class MessageForm(Form):  # Create Message Form
    body = StringField('', [validators.length(min=1)], render_kw={'autofocus': True})

#
# @app.route('/chatting/<string:id>', methods=['GET', 'POST'])
# def chatting(id):
#     if 'uid' in session:
#         form = MessageForm(request.form)
#         # Create cursor
#         cur = mysql.connection.cursor()
#         # lid name
#         get_result = cur.execute("SELECT * FROM users WHERE id=%s", [id])
#         l_data = cur.fetchone()
#         if get_result > 0:
#             session['name'] = l_data['name']
#             uid = session['uid']
#             session['lid'] = id
#             if request.method == 'POST' and form.validate():
#                 txt_body = form.body.data
#                 # Create cursor
#                 cur = mysql.connection.cursor()
#                 cur.execute("INSERT INTO messages(body, msg_by, msg_to) VALUES(%s, %s, %s)",
#                             (txt_body, id, uid))
#                 # Commit cursor
#                 mysql.connection.commit()
#             # Get users
#             cur.execute("SELECT * FROM users")
#             users = cur.fetchall()
#             # Close Connection
#             cur.close()
#             return render_template('chat_room.html', users=users, form=form)
#         else:
#             flash('No permission!', 'danger')
#             return redirect(url_for('index'))
#     else:
#         return redirect(url_for('login'))
#
#
# @app.route('/chats', methods=['GET', 'POST'])
# def chats():
#     if 'lid' in session:
#         id = session['lid']
#         uid = session['uid']
#         # Create cursor
#         cur = mysql.connection.cursor()
#         # Get message
#         cur.execute("SELECT * FROM messages WHERE (msg_by=%s AND msg_to=%s) OR (msg_by=%s AND msg_to=%s) "
#                     "ORDER BY id ASC", (id, uid, uid, id))
#         chats = cur.fetchall()
#         # Close Connection
#         cur.close()
#         return render_template('chats.html', chats=chats, )
#     return redirect(url_for('login'))
#

class OrderForm(Form):  # Create Order Form
    name = StringField('', [validators.length(min=1), validators.DataRequired()],
                       render_kw={'autofocus': True, 'placeholder': 'Full Name'})
    mobile_num = StringField('', [validators.length(min=1), validators.DataRequired()],
                             render_kw={'autofocus': True, 'placeholder': 'Mobile'})
    quantity = SelectField('', [validators.DataRequired()],
                           choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')])
    order_place = StringField('', [validators.length(min=1), validators.DataRequired()],
                              render_kw={'placeholder': 'Order Place'})


@app.route('/fastfood', methods=['GET', 'POST'])
def fruit():
    print("fastfood")
    form = OrderForm(request.form)
    # Create cursor
    cur = mysql.connection.cursor()
    # Get message
    values = 'fastfood'
    cur.execute("SELECT * FROM groceryname WHERE category=%s", (values,))

    products = cur.fetchall()
    # Close Connection
    cur.close()
    if request.method == 'POST' and form.validate():
        name = form.name.data
        mobile = form.mobile_num.data
        order_place = form.order_place.data
        quantity = form.quantity.data
        pid = request.args['order']
        now = datetime.datetime.now()
        week = datetime.timedelta(days=7)
        delivery_date = now + week
        now_time = delivery_date.strftime("%y-%m-%d %H:%M:%S")
        curs1 = mysql.connection.cursor()
        values1= '1'
        curs1.execute("SELECT * FROM groceryname WHERE id=%s", (values1,))

        productsdata = curs1.fetchall()
        productname=""
        #print(productsdata)
        for product in productsdata:
            productname=product['name']
        # Create Cursor
        curs = mysql.connection.cursor()
        if 'uid' in session:
            uid = session['uid']
            curs.execute("INSERT INTO orders(uid, pid, ofname, mobile, oplace, quantity, ddate) "
                         "VALUES(%s, %s, %s, %s, %s, %s, %s)",
                         (uid, pid, name, mobile, order_place+" "+productname, quantity, now_time))
        else:
            curs.execute("INSERT INTO orders(pid, ofname, mobile, oplace, quantity, ddate) "
                         "VALUES(%s, %s, %s, %s, %s, %s)",
                         (pid, name, mobile, order_place+" "+productname, quantity, now_time))
        # Commit cursor
        mysql.connection.commit()

        # Close Connection
        cur.close()

        flash('Order successful', 'success')
        return render_template('fastfood.html', products=products, form=form)
    if 'view' in request.args:
        print()
        product_id = request.args['view']
        curso = mysql.connection.cursor()
        curso.execute("SELECT * FROM groceryname WHERE id=%s", (product_id,))
        product = curso.fetchall()

        return render_template('view_product.html', products=product)
    elif 'order' in request.args:
        product_id = request.args['order']
        curso = mysql.connection.cursor()
        curso.execute("SELECT * FROM groceryname WHERE id=%s", (product_id,))
        product = curso.fetchall()
        #x = content_based_filtering(product_id)
        return render_template('order_product.html', products=product, form=form)
    return render_template('fastfood.html', products=products, form=form)


@app.route('/chinesse', methods=['GET', 'POST'])
def bakery():
    print("chinesse")
    form = OrderForm(request.form)
    # Create cursor
    cur = mysql.connection.cursor()
    # Get message
    values = 'chinesse'
    cur.execute("SELECT * FROM groceryname WHERE category=%s", (values,))

    products = cur.fetchall()
    # Close Connection
    cur.close()
    if request.method == 'POST' and form.validate():
        name = form.name.data
        mobile = form.mobile_num.data
        order_place = form.order_place.data
        quantity = form.quantity.data
        pid = request.args['order']
        now = datetime.datetime.now()
        week = datetime.timedelta(days=7)
        delivery_date = now + week
        now_time = delivery_date.strftime("%y-%m-%d %H:%M:%S")
        # Create Cursor
        curs = mysql.connection.cursor()
        if 'uid' in session:
            uid = session['uid']
            curs.execute("INSERT INTO orders(uid, pid, ofname, mobile, oplace, quantity, ddate) "
                         "VALUES(%s, %s, %s, %s, %s, %s, %s)",
                         (uid, pid, name, mobile, order_place, quantity, now_time))
        else:
            curs.execute("INSERT INTO orders(pid, ofname, mobile, oplace, quantity, ddate) "
                         "VALUES(%s, %s, %s, %s, %s, %s)",
                         (pid, name, mobile, order_place, quantity, now_time))
        # Commit cursor
        mysql.connection.commit()

        # Close Connection
        cur.close()

        flash('Order successful', 'success')
        return render_template('chinesse.html', products=products, form=form)
    if 'view' in request.args:
        print()
        product_id = request.args['view']
        curso = mysql.connection.cursor()
        curso.execute("SELECT * FROM groceryname WHERE id=%s", (product_id,))
        product = curso.fetchall()

        return render_template('view_product.html', products=product)
    elif 'order' in request.args:
        product_id = request.args['order']
        curso = mysql.connection.cursor()
        curso.execute("SELECT * FROM groceryname WHERE id=%s", (product_id,))
        product = curso.fetchall()
        # x = content_based_filtering(product_id)
        return render_template('order_product.html', products=product, form=form)
    return render_template('chinesse.html', products=products, form=form)


@app.route('/rice', methods=['GET', 'POST'])
def drink():
    print("rice")
    form = OrderForm(request.form)
    # Create cursor
    cur = mysql.connection.cursor()
    # Get message
    values = 'rice'
    cur.execute("SELECT * FROM groceryname WHERE category=%s", (values,))

    products = cur.fetchall()
    # Close Connection
    cur.close()
    if request.method == 'POST' and form.validate():
        name = form.name.data
        mobile = form.mobile_num.data
        order_place = form.order_place.data
        quantity = form.quantity.data
        pid = request.args['order']
        now = datetime.datetime.now()
        week = datetime.timedelta(days=7)
        delivery_date = now + week
        now_time = delivery_date.strftime("%y-%m-%d %H:%M:%S")
        # Create Cursor
        curs = mysql.connection.cursor()
        if 'uid' in session:
            uid = session['uid']
            curs.execute("INSERT INTO orders(uid, pid, ofname, mobile, oplace, quantity, ddate) "
                         "VALUES(%s, %s, %s, %s, %s, %s, %s)",
                         (uid, pid, name, mobile, order_place, quantity, now_time))
        else:
            curs.execute("INSERT INTO orders(pid, ofname, mobile, oplace, quantity, ddate) "
                         "VALUES(%s, %s, %s, %s, %s, %s)",
                         (pid, name, mobile, order_place, quantity, now_time))
        # Commit cursor
        mysql.connection.commit()

        # Close Connection
        cur.close()

        flash('Order successful', 'success')
        return render_template('rice.html', products=products, form=form)
    if 'view' in request.args:
        print()
        product_id = request.args['view']
        curso = mysql.connection.cursor()
        curso.execute("SELECT * FROM groceryname WHERE id=%s", (product_id,))
        product = curso.fetchall()

        return render_template('view_product.html', products=product)
    elif 'order' in request.args:
        product_id = request.args['order']
        curso = mysql.connection.cursor()
        curso.execute("SELECT * FROM groceryname WHERE id=%s", (product_id,))
        product = curso.fetchall()
        # x = content_based_filtering(product_id)
        return render_template('order_product.html', products=product, form=form)
    return render_template('rice.html', products=products, form=form)


@app.route('/admin_login', methods=['GET', 'POST'])
@not_admin_logged_in
def admin_login():
    if request.method == 'POST':
        # GEt user form
        username = request.form['email']
        password_candidate = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM admin WHERE email=%s", [username])

        if result > 0:
            # Get stored value
            data = cur.fetchone()
            password = data['password']
            uid = data['id']
            name = data['firstName']

            # Compare password
            if sha256_crypt.verify(password_candidate, password):
                # passed
                session['admin_logged_in'] = True
                session['admin_uid'] = uid
                session['admin_name'] = name

                return redirect(url_for('admin'))

            else:
                flash('Incorrect password', 'danger')
                return render_template('pages/login.html')

        else:
            flash('Username not found', 'danger')
            # Close connection
            cur.close()
            return render_template('pages/login.html')
    return render_template('pages/login.html')


@app.route('/admin_out')
def admin_logout():
    if 'admin_logged_in' in session:
        session.clear()
        return redirect(url_for('admin_login'))
    return redirect(url_for('admin'))


@app.route('/admin')
@is_admin_logged_in
def admin():
    curso = mysql.connection.cursor()
    #num_rows = curso.execute("SELECT * FROM products")
    num_rows = curso.execute("SELECT * FROM groceryname")
    result = curso.fetchall()
    order_rows = curso.execute("SELECT * FROM orders")
    users_rows = curso.execute("SELECT * FROM users")
    return render_template('pages/index.html', result=result, row=num_rows, order_rows=order_rows,
                           users_rows=users_rows)


@app.route('/orders')
@is_admin_logged_in
def orders():
    curso = mysql.connection.cursor()
    num_rows = curso.execute("SELECT * FROM products")
    order_rows = curso.execute("SELECT * FROM orders")
    result = curso.fetchall()
    users_rows = curso.execute("SELECT * FROM users")
    return render_template('pages/all_orders.html', result=result, row=num_rows, order_rows=order_rows,
                           users_rows=users_rows)


@app.route('/users')
@is_admin_logged_in
def users():
    curso = mysql.connection.cursor()
    num_rows = curso.execute("SELECT * FROM groceryname")
    order_rows = curso.execute("SELECT * FROM orders")
    users_rows = curso.execute("SELECT * FROM users")
    result = curso.fetchall()
    return render_template('pages/all_users.html', result=result, row=num_rows, order_rows=order_rows,users_rows=users_rows)


@app.route('/admin_add_product', methods=['POST', 'GET'])
@is_admin_logged_in
def admin_add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form['price']
        category = request.form['category']
        file = request.files['picture']
        if name and price and category and file:
            pic = file.filename
            photo = pic.replace("'", "")
            picture = photo.replace(" ", "_")
            if picture.lower().endswith(('.png', '.jpg', '.jpeg')):
                save_photo = photos.save(file)
                if save_photo:
                    # Create Cursor
                    curs = mysql.connection.cursor()
                    curs.execute("INSERT INTO groceryname(name,imagename,price,category)"
                                 "VALUES(%s, %s, %s, %s)",
                                 (name, picture, price, category))
                    mysql.connection.commit()
                    curs.close()
                    flash('Product added successful', 'success')
                    return redirect(url_for('admin_add_product'))
                else:
                    flash('Picture not save', 'danger')
                    return redirect(url_for('admin_add_product'))
            else:
                flash('File not supported', 'danger')
                return redirect(url_for('admin_add_product'))
        else:
            flash('Please fill up all form', 'danger')
            return redirect(url_for('admin_add_product'))
    else:
        return render_template('pages/add_product.html')


@app.route('/edit_product', methods=['POST', 'GET'])
@is_admin_logged_in
def edit_product():
    if 'id' in request.args:
        product_id = request.args['id']
        curso = mysql.connection.cursor()
        res = curso.execute("SELECT * FROM groceryname WHERE id=%s", (product_id,))
        product = curso.fetchall()
        if res:
            if request.method == 'POST':
                name = request.form.get('name')
                price = request.form['price']
                category = request.form['category']
                file = request.files['picture']
                # Create Cursor
                if name and price and category and file:
                    pic = file.filename
                    photo = pic.replace("'", "")
                    picture = photo.replace(" ", "")
                    if picture.lower().endswith(('.png', '.jpg', '.jpeg')):
                        file.filename = picture
                        save_photo = photos.save(file)
                        if save_photo:
                            # Create Cursor
                            cur = mysql.connection.cursor()
                            exe = curso.execute("UPDATE groceryname SET name=%s, price=%s, category=%s, imagename=%s WHERE id=%s",(name, price, category, picture, product_id))
                            mysql.connection.commit()
                            flash('Product updated successful', 'success')
                            return redirect(url_for('admin_add_product'))
                        else:
                            flash('Pic not upload', 'danger')
                            return render_template('pages/edit_product.html', product=product)
                    else:
                        flash('File not support', 'danger')
                        return render_template('pages/edit_product.html', product=product)
                else:
                    flash('Fill all field', 'danger')
                    return render_template('pages/edit_product.html', product=product)
            else:
                return render_template('pages/edit_product.html', product=product)
        else:
            return redirect(url_for('admin_login'))
    else:
        return redirect(url_for('admin_login'))


@app.route('/search', methods=['POST', 'GET'])
def search():
    form = OrderForm(request.form)
    if 'q' in request.args:
        q = request.args['q']
        # Create cursor
        cur = mysql.connection.cursor()
        # Get message
        query_string = "SELECT * FROM groceryname WHERE name LIKE %s ORDER BY id ASC"
        cur.execute(query_string, ('%' + q + '%',))
        products = cur.fetchall()
        # Close Connection
        cur.close()
        flash('Showing result for: ' + q, 'success')
        return render_template('search.html', products=products, form=form)
    else:
        flash('Search again', 'danger')
        return render_template('search.html')


@app.route('/profile')
@is_logged_in
def profile():
    if 'user' in request.args:
        q = request.args['user']
        curso = mysql.connection.cursor()
        curso.execute("SELECT * FROM users WHERE id=%s", (q,))
        result = curso.fetchone()
        if result:
            if result['id'] == session['uid']:
                curso.execute("SELECT * FROM orders WHERE uid=%s ORDER BY id ASC", (session['uid'],))
                res = curso.fetchall()
                return render_template('profile.html', result=res)
            else:
                flash('Unauthorised', 'danger')
                return redirect(url_for('login'))
        else:
            flash('Unauthorised! Please login', 'danger')
            return redirect(url_for('login'))
    else:
        flash('Unauthorised', 'danger')
        return redirect(url_for('login'))


class UpdateRegisterForm(Form):
    name = StringField('Full Name', [validators.length(min=3, max=50)],
                       render_kw={'autofocus': True, 'placeholder': 'Full Name'})
    email = EmailField('Email', [validators.DataRequired(), validators.Email(), validators.length(min=4, max=25)],
                       render_kw={'placeholder': 'Email'})
    password = PasswordField('Password', [validators.length(min=3)],
                             render_kw={'placeholder': 'Password'})
    mobile = StringField('Mobile', [validators.length(min=11, max=15)], render_kw={'placeholder': 'Mobile'})


@app.route('/settings', methods=['POST', 'GET'])
@is_logged_in
def settings():
    form = UpdateRegisterForm(request.form)
    if 'user' in request.args:
        q = request.args['user']
        curso = mysql.connection.cursor()
        curso.execute("SELECT * FROM users WHERE id=%s", (q,))
        result = curso.fetchone()
        if result:
            if result['id'] == session['uid']:
                if request.method == 'POST' and form.validate():
                    name = form.name.data
                    email = form.email.data
                    password = sha256_crypt.encrypt(str(form.password.data))
                    mobile = form.mobile.data

                    # Create Cursor
                    cur = mysql.connection.cursor()
                    exe = cur.execute("UPDATE users SET name=%s, email=%s, password=%s, mobile=%s WHERE id=%s",
                                      (name, email, password, mobile, q))
                    if exe:
                        flash('Profile updated', 'success')
                        return render_template('user_settings.html', result=result, form=form)
                    else:
                        flash('Profile not updated', 'danger')
                return render_template('user_settings.html', result=result, form=form)
            else:
                flash('Unauthorised', 'danger')
                return redirect(url_for('login'))
        else:
            flash('Unauthorised! Please login', 'danger')
            return redirect(url_for('login'))
    else:
        flash('Unauthorised', 'danger')
        return redirect(url_for('login'))


class DeveloperForm(Form):  #
    id = StringField('', [validators.length(min=1)],
                     render_kw={'placeholder': 'Input a product id...'})


def a():
    DataCaptured = csv.reader('groceries.csv', delimiter=',')
    product = []
    cur = mysql.connection.cursor()
    for a in DataCaptured:
        if a not in product:
            product.append(a)

            sql = "INSERT INTO groceryname (name) VALUES (%s)"
            val = (a)
            cur.execute(sql, val)
            mysql.connection.commit()
#=============================


@app.route('/ruser_login', methods=['GET', 'POST'])
@not_ruser_logged_in
def ruser_login():
    if request.method == 'POST':
        username = request.form["rusername"]
        password_candidate = request.form["rpassword"]
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM resto_user WHERE username=%s", [username])
        if result > 0:
            data = cur.fetchone()
            password = data['password']
            uid = data['id']
            name = data['name']
            if sha256_crypt.verify(password_candidate, password):
                session['ruser_logged_in'] = True
                session['ruid'] = uid
                session['s_name'] = name
                x = '1'
                cur.execute("UPDATE resto_user SET online=%s WHERE id=%s", (x, uid))
                return redirect(url_for('rhome'))
            else:
                flash('Incorrect password', 'danger')
                return render_template('RestoUser/login.html')
        else:
            flash('Username not found', 'danger')
            # Close connection
            cur.close()
            return render_template('RestoUser/login.html')
    return render_template('RestoUser/login.html')


@app.route('/ruser_register', methods=['GET', 'POST'])
@not_ruser_logged_in
def ruser_register():
    if request.method == 'POST':
        name = request.form["rname"]
        email = request.form["remail"]
        username = request.form["rusername"]
        password = sha256_crypt.encrypt(str(request.form["rpassword"]))
        mobile = request.form["rmobile"]
        # Create Cursor
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO resto_user(name, email, username, password, mobile) VALUES(%s, %s, %s, %s, %s)",
                    (name, email, username, password, mobile))
        # Commit cursor
        mysql.connection.commit()
        # Close Connection
        cur.close()
        flash('You are now registered and can login', 'success')
        return redirect(url_for('ruser_login'))
    return render_template('RestoUser/register.html')


@app.route('/rhome', methods=['GET', 'POST'])
def rhome():
    if 'ruid' in session:
        if request.method == 'POST':
            ruid = request.form["ruid"]
            tno = request.form["tno"]
            qrimgname = ruid+'_'+tno+'.png'
            if ruid and tno:
                img = qrcode.make('Order from table no'+tno)
                #static/qrimages
                img.save('static/qrimages/'+qrimgname)

                cur = mysql.connection.cursor()
                cur.execute(
                    "INSERT INTO tableinfo(tableno, rid, tqrcode) VALUES(%s, %s, %s)",
                    (tno,ruid,qrimgname))
                # Commit cursor
                mysql.connection.commit()
                # Close Connection
                cur.close()
        return render_template('RestoUser/rhome.html', ruid=session['ruid'])
    return redirect(url_for('ruser_login'))


@app.route('/tableDetails', methods=['GET', 'POST'])
def tableDetails():
    if 'ruid' in session:
        ruid = str(session['ruid'])
        print(ruid)
        cur = mysql.connection.cursor()
        # Get message
        query = "SELECT * FROM tableinfo WHERE rid="+ruid
        print(query)
        #val=(ruid)
        #cur.execute("SELECT * FROM tableinfo WHERE rid=%s", (ruid))
        cur.execute(query )
        allqr = cur.fetchall()
        print(allqr)
        # Close Connection
        cur.close()
        return render_template('RestoUser/tableDetails.html', allqr=allqr)
    return redirect(url_for('ruser_login'))

@app.route('/restarauntlocation', methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        latti=request.args['latti']
        longi=request.args['longi']
        print('in get')
        print(latti+' '+longi)
        python2json=lattilongilocation(latti,longi)
        return python2json
    if request.method == 'POST':
        print('inside')
        latti=request.args.get('latti')
        longi=request.args.get('longi')
        print('in post')
        print(latti)
        print(longi)
        python2json=lattilongilocation(float(latti),float(longi))
        print(python2json)
        return python2json
@app.route('/ruserout')
def ruserout():
    if 'ruid' in session:
        session.clear()
        return redirect(url_for('rhome'))
    return redirect(url_for('rhome'))
#=============================


if __name__ == '__main__':
    app.run('0.0.0.0')
    #app.run()