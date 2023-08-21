from sqlite3 import DatabaseError

from flask import Flask
from view import *
import secrets

"""
ПРАЦЮЄ:
    'DELETE' (Видалення страви є, видалення з кошика є)
    Session додано до користувача і адмінки
    Також є тамплейти
    Реєстрація, логін, зміна пароля, редагування даних користувача працюють
    Додавання , редагування страви працюють
    Додавання категоріі працює
    Кошик працює (додавання, кількість, видалення з кошика, зміна статусу(Замовити))


НЕ ПРАЦЮЄ:
    Історія замовленнь в процессі розробки
    'DELETE' (Видалення користувача)
    Сортування категорії в процессі розробки
    КБЖВ поки не рахує (потім зроблю)
    Перевірок на правильність введених користувачем даних поки нема
    Сортування в процессі розробки
"""

app = Flask(__name__)
app.secret_key = secrets.token_hex()
app.config['PERMANENT_SESSION_LIFETIME'] = 3600


app.add_url_rule('/', view_func=start_page, methods=['GET'])  # ok
app.add_url_rule('/about', view_func=about, methods=['GET'])  # ok

app.add_url_rule('/cart', view_func=cart, methods=['GET', 'POST'])  # ok
app.add_url_rule('/cart/order', view_func=cart_order, methods=['GET', 'POST'])
app.add_url_rule('/cart/add', view_func=cart_add, methods=['GET', 'POST'])

app.add_url_rule('/user', view_func=user, methods=['GET', 'POST', 'DELETE'])  # ok
app.add_url_rule('/user/update', view_func=user_update, methods=['GET', 'POST'])  # ok
app.add_url_rule('/user/register', view_func=user_register, methods=['GET', 'POST'])  # ok
app.add_url_rule('/user/sign_in', view_func=user_sign_in, methods=['GET', 'POST'])  # ok
app.add_url_rule('/user/logout', view_func=user_logout, methods=['GET', 'POST'])  # ok
app.add_url_rule('/user/restore', view_func=user_restore, methods=['GET', 'POST'])  # ok
app.add_url_rule('/user/history', view_func=user_orders_history, methods=['GET'])  # ok
app.add_url_rule('/user/history/<order_id>', view_func=user_order, methods=['GET'])  # ok
app.add_url_rule('/user/addresses', view_func=user_address_list, methods=['GET', 'POST'])  # ok
app.add_url_rule('/user/addresses/add', view_func=user_address_add, methods=['GET', 'POST'])  # ok
app.add_url_rule('/user/addresses/<address_id>', view_func=user_address, methods=['GET', 'POST', 'DELETE'])  # ok

app.add_url_rule('/menu', view_func=menu, methods=['GET'])  # ok
app.add_url_rule('/menu/categories', view_func=categories, methods=['GET'])  # ok
app.add_url_rule('/menu/categories/<cat_id>', view_func=category_dishes, methods=['GET'])  # ok
app.add_url_rule('/menu/categories/<cat_id>/<dish_id>', view_func=dish, methods=['GET'])  # ok
app.add_url_rule('/menu/categories/<cat_id>?<order_by>/<asc_desc_val>', view_func=category_sort, methods=['GET'])  # in progress
app.add_url_rule('/menu/all_dishes', view_func=dishes, methods=['GET'])  # ok

app.add_url_rule('/menu/search', view_func=search, methods=['GET', 'POST'])  # ok
app.add_url_rule('/menu/all_dishes/<order_by_var>/<asc_desc_val>', view_func=dish_sort, methods=['GET', 'POST'])  # ok

app.add_url_rule('/admin/dishes', view_func=admin_dishes, methods=['GET'])  # ok
app.add_url_rule('/admin/dishes/add', view_func=admin_dish, methods=['GET', 'POST'])  # ok
app.add_url_rule('/admin/dishes/edit/<dish_id>', view_func=admin_dish_edit, methods=['GET', 'POST'])  # ok
app.add_url_rule('/admin/dishes/edit/<dish_id>/delete', view_func=delete_dish, methods=['GET', 'POST'])  # ok
app.add_url_rule('/admin/orders', view_func=admin_orders, methods=['GET'])  # ok
app.add_url_rule('/admin/orders/<order_id>', view_func=admin_order, methods=['GET', 'POST'])  # ok
app.add_url_rule('/admin/orders?status={new/in_progress}', view_func=admin_sort_order_status, methods=['GET'])
app.add_url_rule('/admin/orders/<id>/status', view_func=admin_set_order_status, methods=['POST'])
app.add_url_rule('/admin/categories', view_func=admin_show_categories, methods=['GET'])  # ok
app.add_url_rule('/admin/categories/edit', view_func=admin_category_edit, methods=['GET', 'POST', 'DELETE'])  # [GET, POST] ok
app.add_url_rule('/admin/search', view_func=admin_search, methods=['GET'])   # ok


@app.errorhandler(404)
def page_not_found(error):
    return 'This page does not exist', 404


@app.errorhandler(DatabaseError)
def special_exception_handler(error):
    return 'Database connection failed', 500


if __name__ == '__main__':
    app.run(debug=True)
