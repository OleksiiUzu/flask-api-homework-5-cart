from flask import render_template, request, redirect, flash, session
from db_methods import SQLiteDB
import datetime


# /////////////////////////////DataBase Methods/////////////////////////////////////////////////
def db_get_data(data_base, table_name, *args, params=None, get_all=True):
    """
    :param data_base: name of database
    :param table_name: name of table
    :param args: columns {dict}
    :param params: {dict} , adding WHERE to sql query
    :param get_all: fetchall(True) or fetchone(False)
    :return: dict
    """
    with data_base as db:
        result = db.select_from(table_name, *args, param=params, all_data=get_all)
    return result


def db_post_data(data_base, table_name, params=None):
    """
    :param data_base:  name of database
    :param table_name: str
    :param params: dict
    :return:
    """
    with data_base as db:
        result = db.insert_into(table_name, params)
        print(result)
    return result


def db_del_data(data_base, table_name, columns, param=False):
    """
    :param columns: dict
    :param data_base:  name of database
    :param table_name: str
    :param param: dict
    :return:
    """
    with data_base as db:
        result = db.delete_dish(table_name, columns, param=param)
    return result


def db_update_data(data_base, table_name, columns, params):
    with data_base as db:
        result = db.update(table_name, columns, params)
    return result


def ordered(data_base, table_name, params, asc_desc):
    with data_base as db:
        result = db.ordered_by(table_name, ['*'], params, asc_desc=asc_desc)
    return result


def db_raw_query(data_base, query: str, get_all=True):
    with data_base as db:
        result = db.sql_query(query, all_data=get_all)
    return result

# ///////////////////////////////The END///////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////Main Page, About Page Methods/////////////////////////


def start_page():
    """
    :return: Main Page.
    """
    if not session.get("Email") and not session.get("Password") and not session.get("ID"):
        return redirect("user/sign_in")
    return render_template('index.html')


def about():
    """
    :return: About Page.
    """
    return render_template('about.html')


# ///////////////////////////////The END///////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////Cart Methods//////////////////////////////////////////
def cart_add_order(post_data: dict, order_data: dict):
    post_data['order_id'] = str(order_data['ID'])
    db_post_data(SQLiteDB('Dishes.db'), 'Ordered_dishes', params=post_data)


def cart():
    """
    Shows all dishes in cart.
    :return: data of all dishes in cart.
    """
    user_id = session['ID']
    order_status = 0
    order = db_get_data(SQLiteDB('Dishes.db'), 'Orders', ["*"], params={'User': user_id, 'Status': order_status}, get_all=False)
    ordered_dishes = False
    try:
        ordered_dishes = db_raw_query(SQLiteDB('Dishes.db'),
                                      f'SELECT * FROM Ordered_dishes join Dishes on Ordered_dishes.dish = Dishes.ID where Ordered_dishes.order_id = {order["ID"]}')
    except Exception as e:
        print("Помилка:", e)
    if request.method == 'POST':
        del_order = request.form.to_dict()
        if del_order:
            try:
                db_del_data(SQLiteDB('Dishes.db'), 'Ordered_dishes', columns={'order_id': order['ID'], 'dish': del_order['ID']}, param=True)
            except Exception as e:
                print("Помилка:", e)
        return redirect('/cart')

    return render_template('cart.html',
                           result=ordered_dishes
                           )


def cart_order():
    """
    :return: order_data for paying.
    """
    if request.method == 'POST':
        try:
            db_update_data(SQLiteDB('Dishes.db'), 'Orders', {'Status': 1}, params={'User': session['ID'], 'Status': 0})
        except Exception as e:
            print("Помилка:", e)
        return redirect('/cart')
    if request.method == 'GET':
        try:
            result = db_get_data(SQLiteDB('Dishes.db'), 'Orders', ['*'], params={'User': session['ID']})
            result = result[0]
            dish_data = db_raw_query(SQLiteDB('Dishes.db'),
                                  f'SELECT * FROM Ordered_dishes join Dishes on Ordered_dishes.dish = Dishes.ID where Ordered_dishes.order_id = {result["ID"]}')
            return render_template('cart_order.html', result=result, dish_data=dish_data)
        except Exception as e:
            print("Помилка:", e)
        return render_template('cart_order.html')


def cart_add():
    """
    Adding dish to cart.
    POST methods
                                    WARNING!!!!!
    This function is **under development** and **does NOT comply with PEP8**!!!  
    
    The code may contain:  
    - Forbidden magic
    - Dirty hacks
    - Unholy, non-canonical code (code != PEP8)
    
    **Sensitive programmers are advised to look away!**  
    
    If while reading this code you experience:  
    - Migraine
    - Dizziness
    - Nausea
    - Depression
    - Rage
    
    Then the author **takes NO responsibility for this!**  
    Just close it and know that **it (kind of) works**.
    
    Enjoy the ride!
    """
    if session.get('ID') is None:
        return redirect('/user/sign_in')
    if request.method == 'POST':
        data = request.form.to_dict()
        res = db_get_data(SQLiteDB('Dishes.db'), 'Orders', ['*'], params={'User': session['ID'], 'Status': 0}, get_all=True)
        current_datetime = datetime.datetime.now()
        if res:
            for i in res:
                if i['User'] == session['ID'] and i['Status'] == 0:
                    cart_add_order(data, i)
                    return redirect('/menu')
                elif i['User'] != session['ID']:
                    data_result = db_get_data(SQLiteDB('Dishes.db'),
                                              'Address',
                                              ['ID'],
                                              params={'User': session['ID']},
                                              get_all=False)
                    order_data = {'User': session['ID'],
                                  'Address': data_result['ID'],
                                  'price': '0',
                                  'Ccal': '0',
                                  'Fat': '0',
                                  'Protein': '0',
                                  'Carbon': '0',
                                  'Order_date': current_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                                  'Status': '0'}
                    try:
                        db_post_data(SQLiteDB('Dishes.db'), 'Orders', params=order_data)
                        result_order = db_get_data(SQLiteDB('Dishes.db'), 'Orders', ['*'], params={'User': session['ID']}, get_all=False)
                        cart_add_order(data, result_order)
                    except Exception as e:
                        print("Помилка:", e)
        else:
            data_result = db_get_data(SQLiteDB('Dishes.db'), 'Address',
                                                             ['ID'],
                                                             params={'User': session['ID']},
                                                             get_all=False)
            order_data = {'User': session['ID'],
                          'Address': data_result['ID'],
                          'price': '0',
                          'Ccal': '0',
                          'Fat': '0',
                          'Protein': '0',
                          'Carbon': '0',
                          'Order_date': current_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                          'Status': '0'}
            try:
                db_post_data(SQLiteDB('Dishes.db'), 'Orders', params=order_data)
                res = db_get_data(SQLiteDB('Dishes.db'), 'Orders', ['*'], get_all=True)
                for i in res:
                    if i['User'] == session['ID'] and i['Status'] == 0:
                        cart_add_order(data, i)
            except Exception as e:
                print("Помилка:", e)
            return redirect('/')
    return render_template('index.html')
# ///////////////////////////////The END///////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////User Methods//////////////////////////////////////////


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
        try:
            result = db_post_data(SQLiteDB('Dishes.db'), 'User', data)
            if result:
                return redirect('/user/sign_in')
        except Exception as e:
            print("Помилка:", e)
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
        return render_template('orders.html',
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


# ///////////////////////////////The END///////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////Menu ,Category , Dish Methods/////////////////////////
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
    par = request.args
    print(par)
    if request.method == "GET":
        try:
            result = ordered(SQLiteDB('Dishes.db'), 'Dishes', params=order_by, asc_desc=asc_desc_val)
            print(result)
            return result
        except Exception as e:
            print("Помилка:", e)



def dishes():
    """
    methods=['GET']
    :return:
    """
    result = db_get_data(SQLiteDB('Dishes.db'), 'Dishes', ['*'])
    if request.method == 'GET':
        return render_template('category_dishes.html', result=result
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


# ///////////////////////////////The END///////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////Admin Methods/////////////////////////////////////////
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
    print(request.method)
    if session.get('ID') is None:
        return redirect('/user/sign_in')
    dish_data = db_get_data(SQLiteDB('Dishes.db'), 'Dishes', ['*'], params={'ID': dish_id})
    dish_data_dict = dish_data[0]
    print(dish_data_dict)
    if request.method == 'POST':
        data = request.form.to_dict()
        print('data: : ', data)
        try:
            result = render_template('add_dish.html',
                                     result=db_update_data(SQLiteDB('Dishes.db'),
                                                           'Dishes',
                                                           data,
                                                           params={'ID': dish_data_dict['ID']}))
            if result:
                return redirect('/admin/dishes')
        except Exception as e:
            print("Помилка:", e)
    return render_template('dish_edit.html', result=dish_data_dict)


def delete_dish(dish_id):
    if request.method == 'POST':
        print('DELETE')
        data = request.form.to_dict()
        print('Delete method: ', data)
        db_del_data(SQLiteDB('Dishes.db'), 'Dishes', data)
    return redirect('/admin/dishes')


def admin_orders():
    """
    methods=['GET']
    :return:
    """
    if session.get('ID') is None:
        return redirect('/user/sign_in')
    if request.method == 'GET':
        in_progress_orders = db_get_data(SQLiteDB('Dishes.db'), 'Orders', ['*'], params={'Status': 1})
        done_orders = db_get_data(SQLiteDB('Dishes.db'), 'Orders', ['*'], params={'Status': 2})
        print(in_progress_orders)
        print(done_orders)
        return render_template('orders.html',
                               progress=in_progress_orders,
                               done=done_orders
                               )


def admin_order(order_id: int):
    """
    methods=['GET', 'POST']
    :return:
    """
    print(request.method)
    print(order_id)
    if session.get('ID') is None:
        return redirect('/user/sign_in')
    ordered_dishes = db_raw_query(SQLiteDB('Dishes.db'),
                                  f'SELECT * FROM Ordered_dishes join Dishes on Ordered_dishes.dish = Dishes.ID where Ordered_dishes.order_id = {order_id}')
    print(ordered_dishes)
    if request.method == "POST":
        try:
            db_update_data(SQLiteDB('Dishes.db'), 'Orders', {'Status': 2}, params={'ID': order_id})
        except Exception as e:
            print("Помилка:", e)
        return redirect('/admin/orders')

    return render_template('order.html',
                           result=db_get_data(SQLiteDB('Dishes.db'), 'Orders', ['*'], params={'id': order_id}),
                           dish_data=ordered_dishes
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

# ///////////////////////////////The END///////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////////////
