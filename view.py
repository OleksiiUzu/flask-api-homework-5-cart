from flask import render_template, request, redirect, flash, session
from db_methods import SQLiteDB


# //////////////////////////////////////////////////////////////////////////////
#  З цим я потім придумаю як краще написати

# get_all може бути True/False (fetchall() / fetchone()) , за замовчуванням повертає fetchall()
def db_get_data(data_base, tables, *args, params=None, get_all=True):
    with data_base as db:
        result = db.select_from(tables, *args, param=params, all_data=get_all)
    return result


def db_post_data(data_base, tables, params=None):
    with data_base as db:
        result = db.insert_into(tables, params)
    return result


def db_update_data(data_base, table_name, columns, params):
    with data_base as db:
        result = db.update(table_name, columns, params)
    return result


def ordered(data_base, tables, params, asc_desc):
    with data_base as db:
        result = db.ordered_by(tables, ['*'], params, asc_desc=asc_desc)
    return result

# //////////////////////////////////////////////////////////////////////////////


def start_page():
    """
    :return: Main Page.
    """
    if not session.get("Email") and not session.get("Password") and not session.get("ID"):
        # if not there in the session then redirect to the login page
        return redirect("user/sign_in")
    return render_template('index.html')


def about():
    """
    :return: About Page.
    """
    return render_template('about.html')


def cart():
    """
    Shows all dishes in cart.
    :return: data of all dishes in cart.
    """
    if request.method == 'GET':
        return render_template('cart.html',
                               result=db_get_data(SQLiteDB('Dishes.db'), 'Orders', ['*'])
                               )


def cart_order():
    """
    :return: order_data for paying.
    """
    if request.method == 'POST':
        pass


def cart_add():
    """
    Adding dish to cart.
    POST / PUT methods
    :return:  dish_data (I guess).
    """
    return


def user():
    """
    Different actions with user.
    methods=['GET', 'POST', 'PUT', 'DELETE']
    :return: user_data.
    """
    if session.get('ID') is None:
        return redirect('/user/sign_in')

    if request.method == 'GET' and session['ID'] is not None:
        return render_template('user.html',
                               result=db_get_data(SQLiteDB('Dishes.db'), 'User', ['*'], params={'ID': session['ID']})
                               )


def user_update():
    if session.get('ID') is None:
        return redirect('/user/sign_in')

    if request.method == 'POST' and session['ID'] is not None:
        data = request.form.to_dict()
        db_update_data(SQLiteDB('Dishes.db'), 'User', data, params={'ID': session['ID']})
        return redirect('/')
    return render_template('user_update.html')


def user_register():
    if request.method == 'POST':
        data = request.form.to_dict()
        result = db_post_data(SQLiteDB('Dishes.db'), 'User', data)
        if result:
            return redirect('/user/sign_in')
    return render_template('register.html')


def user_sign_in():
    """
    methods = [POST]
    :return:
    """

    if request.method == 'POST':
        data = request.form.to_dict()
        result = db_get_data(SQLiteDB('Dishes.db'), 'User', ['*'], params=data, get_all=False)
        if result:
            flash('You logged in')
            session['ID'] = result['ID']
            session['Telephone'] = result['Telephone']
            session['Email'] = result['Email']
            session['Password'] = result['Password']
            session['Tg'] = result['Tg']
            session['Type'] = result['Type']
            return redirect('/')
        else:
            return '<p>Invalid data</p>'
    return render_template('sign_in.html')


def user_logout():
    """
    methods=['POST', 'GET']
    :return:
    """
    if session.get('ID') is None:
        return redirect('/user/sign_in')
    session['ID'] = None
    session['Email'] = None
    session['Password'] = None
    session['Type'] = None
    return redirect("/")


def user_restore():
    """
    methods=['POST']
    :return:
    """
    if request.method == 'POST':
        data = request.form.to_dict()
        if db_update_data(SQLiteDB('Dishes.db'), 'User', {'Password': data['Password']}, params={'Email': data['Email']}):
            return redirect('/user/sign_in')
    return render_template('password_restore.html')


def user_orders_history():
    """
    methods=['GET']
    :return:
    """
    if session.get('ID') is None:
        return redirect('/user/sign_in')
    if request.method == 'GET':
        return render_template('user.html',
                               result=db_get_data(SQLiteDB('Dishes.db'),
                                                  'Orders',
                                                  ['*'],
                                                  params={'User': session['ID']}))


def user_order(order_id: int):
    """
    Shows user order
    methods=['GET']
    :return:
    """
    if session.get('ID') is None:
        return redirect('/user/sign_in')
    if request.method == 'GET':
        return render_template('user.html',
                               result=db_get_data(SQLiteDB('Dishes.db'), 'Orders', ['*'], params={'id': order_id})
                               )


def user_address_list():
    """
    methods=['GET', 'POST']
    :return:
    """
    if session.get('ID') is None:
        return redirect('/user/sign_in')
    if request.method == 'GET':
        result = db_get_data(SQLiteDB('Dishes.db'), 'Address', ['*'], params={'User': session['ID']})
        print(result)
        return render_template('user_addresses.html', result=result)


def user_address_add():
    if session.get('ID') is None:
        return redirect('/user/sign_in')
    result = db_get_data(SQLiteDB('Dishes.db'), 'Address', ['*'], params={'User': session['ID']}, get_all=False)
    if request.method == 'POST':
        data = request.form.to_dict()
        print('this is data: ', data)
        if db_post_data(SQLiteDB('Dishes.db'), 'Address', params=data):
            return redirect('/user/addresses')
        print(result)
    return render_template('address_add.html', result=result)


def user_address(address_id: int):
    """
    methods=['GET', 'POST', 'DELETE']
    :return:
    """
    if session.get('ID') is None:
        return redirect('/user/sign_in')
    if request.method == 'GET':
        data = db_get_data(SQLiteDB('Dishes.db'), 'Address', ['*'], params={'id': address_id})
        return render_template('user_address_edit.html', result=data)
    elif request.method == 'POST':
        data = request.form.to_dict()
        db_update_data(SQLiteDB('Dishes.db'), 'Address', data,
                       params={'ID': address_id})
        return redirect('/user/addresses')
    return render_template('user_addresses.html')


def menu():
    if request.method == 'GET':
        return render_template('menu.html',
                               result=db_get_data(SQLiteDB('Dishes.db'), 'Dishes', ['*'])
                               )


def categories():
    """
    methods=['GET']
    :return:
    """
    if request.method == "GET":
        return render_template('categories.html',
                               result=db_get_data(SQLiteDB('Dishes.db'), 'Category', ['*'])
                               )


def category_dishes(cat_id):
    """
    methods=['GET']
    :return:
    """
    if request.method == "GET":
        return render_template('category_dishes.html',
                               result=db_get_data(SQLiteDB('Dishes.db'), 'Dishes', ['*'], params={'Category': cat_id})
                               )


def category_sort(cat_id, order_by, asc_desc_val):
    """
    methods=['GET']
    :return:
    """
    if request.method == "GET":
        result = ordered(SQLiteDB('Dishes.db'), 'Dishes', params=order_by, asc_desc=asc_desc_val)
        print(result)
        return result


def dishes():
    """
    methods=['GET']
    :return:
    """
    if request.method == 'GET':
        return render_template('category_dishes.html', result=db_get_data(SQLiteDB('Dishes.db'), 'Dishes', ['*'])
                               )


def dish(cat_id: int, dish_id: int):
    """
    methods=['GET']
    :return:
    """
    admin_dish_edit(dish_id)
    if request.method == 'GET':
        return render_template('dish.html',
                               result=db_get_data(SQLiteDB('Dishes.db'), 'Dishes', ['*'], params={'ID': dish_id})
                               )


def search():
    """
    methods=['GET', 'POST']
    :return:
    """
    if request.method == 'POST':
        data = request.form.to_dict()
        return render_template('dish.html',
                               result=db_get_data(SQLiteDB('Dishes.db'), 'Dishes', ['*'], params={'Dish_name': data['search']})
                               )
    return render_template('search.html')


def dish_sort(order_by_var, asc_desc_val):
    """
    methods=['GET', 'POST']
    :return:
    """

    if request.method == 'GET':
        print('order_by_var: ', order_by_var)
        return render_template('category_dishes.html',
                               result=ordered(SQLiteDB('Dishes.db'),
                                              'Dishes',
                                              params=order_by_var,
                                              asc_desc=asc_desc_val))


def admin_dishes():
    """
    methods=['GET']
    :return:
    """
    if session.get('ID') is None:
        return redirect('/user/sign_in')
    if request.method == 'GET':
        if session['Type'] == 'Admin':
            result = db_get_data(SQLiteDB('Dishes.db'), 'Dishes', ['*'])
            return render_template('category_dishes.html', result=result)


def admin_dish():
    """
    methods=['GET', 'POST']
    :return:
    """
    if session.get('ID') is None:
        return redirect('/user/sign_in')
    if request.method == 'POST':
        data = request.form.to_dict()

        if render_template('add_dish.html',
                           result=db_post_data(SQLiteDB('Dishes.db'), 'Dishes', data)):
            return redirect('/admin/dishes')
    category_data = db_get_data(SQLiteDB('Dishes.db'), 'Category', ['*'])
    return render_template('add_dish.html', cat_data=category_data)


def admin_dish_edit(dish_id):
    """
    methods=['GET', 'POST']
    :return:
    """
    if session.get('ID') is None:
        return redirect('/user/sign_in')
    dish_data = db_get_data(SQLiteDB('Dishes.db'), 'Dishes', ['*'], params={'ID': dish_id})
    dish_data_dict = dish_data[0]
    if request.method == 'POST':
        data = request.form.to_dict()
        result = render_template('add_dish.html',
                                 result=db_update_data(SQLiteDB('Dishes.db'),
                                                       'Dishes',
                                                       data,
                                                       params={'ID': dish_data_dict['ID']}))
        if result:
            return redirect('/admin/dishes')
    return render_template('dish_edit.html', result=dish_data_dict)


def admin_orders():
    """
    methods=['GET']
    :return:
    """
    if session.get('ID') is None:
        return redirect('/user/sign_in')
    if request.method == 'GET':
        return render_template('orders.html',
                               result=db_get_data(SQLiteDB('Dishes.db'), 'Orders', ['*'])
                               )


def admin_order(order_id: int):
    """
    methods=['GET']
    :return:
    """
    if session.get('ID') is None:
        return redirect('/user/sign_in')
    if request.method == 'GET':
        return render_template('order.html',
                               result=db_get_data(SQLiteDB('Dishes.db'), 'Orders', ['*'], params={'id': order_id})
                               )


def admin_sort_order_status():
    """
    methods=['GET']
    :return:
    """
    if session.get('ID') is None:
        return redirect('/user/sign_in')
    return


def admin_set_order_status():
    """
    methods=['POST']
    :return:
    """
    if session.get('ID') is None:
        return redirect('/user/sign_in')
    return


def admin_show_categories():
    """
    methods=['GET']
    :return:
    """
    if session.get('ID') is None:
        return redirect('/user/sign_in')
    if request.method == "GET":
        return render_template('categories.html',
                               result=db_get_data(SQLiteDB('Dishes.db'), 'Category', ['*'])
                               )


def admin_category_edit():
    """
    methods=['POST', 'DELETE']
    :return:
    """
    if session.get('ID') is None:
        return redirect('/user/sign_in')
    if request.method == 'POST':
        data = request.form.to_dict()
        if db_post_data(SQLiteDB('Dishes.db'), 'Category', data):
            return redirect('/admin/categories')
    return render_template('admin_categories.html')


def admin_search():
    """
    methods=['GET']
    :return:
    """
    if session.get('ID') is None:
        return redirect('/user/sign_in')

