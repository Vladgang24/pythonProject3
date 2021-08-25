from main import app
from flask import render_template, redirect, url_for, flash, request
from main.models import Item, Shop, User
from main.forms import RegisterForm, LoginForm, PurchaseItemForm, SellItemForm
from main import db
from flask_login import login_user, logout_user, login_required, current_user


@app.route('/')
@app.route('/home')
def home_page():
    return render_template('Home.html')


@app.route('/advice')
def advice_page():
    return render_template('Advices.html')


@app.route('/training')
def train():
    trains = Item.query.all()
    return render_template('Train.html', trains=trains)


@app.route('/shop', methods=['GET', 'POST'])
@login_required
def shop():
    purchase_form = PurchaseItemForm()
    selling_form = SellItemForm()
    if request.method == 'POST':
        purchased_shop = request.form.get('purchased_shop')
        p_shop_obj = Shop.query.filter_by(name=purchased_shop).first()
        if p_shop_obj:
            if current_user.can_purchase(p_shop_obj):
                p_shop_obj.buy(current_user)
                flash(f"Congratulations! You purchased {p_shop_obj.name} for {p_shop_obj.price}$", category='success')
            else:
                flash(f'Go get a job and open your eyes {current_user.username} ', category='danger')

        sold_item = request.form.get('sold_item')
        s_shop_obj = Shop.query.filter_by(name=sold_item).first()
        if s_shop_obj:
            if current_user.can_sell(s_shop_obj):
                s_shop_obj.sell(current_user)
                flash(f"Congratulations! You sold {s_shop_obj.name} back to market!", category='success')
            else:
                flash(f"Something went wrong with selling {s_shop_obj.name}", category='danger')
        return redirect(url_for('shop'))

    if request.method == 'GET':
        shops = Shop.query.filter_by(owner=None)
        owned_shops = Shop.query.filter_by(owner=current_user.id)
        return render_template('shop.html', shops=shops, purchase_form=purchase_form, owned_shops=owned_shops,
                               selling_form=selling_form)


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email_address=form.email_address.data,
                              password=form.password1.data,
                              )
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Account created successfully! You are now logged in as {user_to_create.username}", category='success')
        return redirect(url_for('shop'))
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('shop'))
        else:
            flash('Username and password are not match! Please try again', category='danger')
    return render_template('login.html', form=form)


@app.route('/logout')
def logout_page():
    logout_user()
    flash('You have been logout.', category='info')
    return redirect(url_for("home_page"))

