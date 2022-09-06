#!/usr/bin/env python

"""
Columbia's COMS W4111.003 Introduction to Databases
Example Webserver

To run locally:

    python server.py

Go to http://localhost:8111 in your browser.

A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@104.196.152.219/proj1part2
#
# For example, if you had username biliris and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://biliris:foobar@104.196.152.219/proj1part2"
#
DATABASEURI = "postgresql://jl5801:jl5801@35.196.73.133/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
# engine.execute("""CREATE TABLE IF NOT EXISTS test (
#  id serial,
#  name text
# );""")
# engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print ("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """




  #
  # example of a database query
  #
  cursor = g.conn.execute("SELECT DISTINCT name FROM test")
  names = []
  for result in cursor:
    names.append(result['name'])  # can also be accessed using result[0]
  cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  context = dict(data = names)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#

@app.route('/employee_delete',methods=['GET'])
def employee_delete():
  ssn = request.args["ssn"]
  g.conn.execute("delete FROM employee where ssn="+ssn)
  return redirect('/employee')

@app.route('/employee_add',methods=['POST'])
def employee_add():
  form = request.form
  if form['employee_authority'] == "TRUE":
    employee_authority = 1
  else:
    employee_authority = 0
  sql = "insert into employee(ssn,first_name,last_name,e_id,d_id,employee_time_zone,employee_authority) \
    values({form['ssn']},'{form['first_name']}','{form['last_name']}',{form['e_id']},'{form['d_id']}',{form['employee_time_zone']},{employee_authority})"
  g.conn.execute(sql)
  return redirect('/employee')

@app.route('/employee_update',methods=['POST'])
def employee_update():
  form = request.form
  if form['employee_authority'] == "TRUE":
    employee_authority = 1
  else:
    employee_authority = 0
  sql = f"update employee set \
        first_name ='{form['first_name']}', \
       last_name='{form['last_name']}',e_id={form['e_id']},d_id={form['d_id']},employee_time_zone={form['employee_time_zone']},employee_authority={employee_authority} \
        where ssn={form['ssn']}"
  g.conn.execute(sql)
  return redirect('/employee')


# page of employee
@app.route('/employee')
def employee():
  datas = []
  cursor = g.conn.execute("SELECT E.ssn, E.first_name, E.last_name, E.e_id, \
    E.employee_time_zone, E.employee_authority, D.department_name, E.d_id \
    FROM employee E, department D \
    WHERE E.d_id = D.d_id")
  for result in cursor:
    var_auth = result['employee_authority']
    if var_auth == 1:
      var_auth = "TRUE"
    else:
      var_auth = 'FALSE'

    var_timezone = abs(result['employee_time_zone'])
    data = {
      'ssn': result['ssn'],
      'first_name': result['first_name'],
      'last_name': result['last_name'],
      "e_id": result['e_id'],
      "d_id": result['d_id'],
      'employee_time_zone': var_timezone,
      'employee_authority': var_auth,
      'department_name': result['department_name'],
    }
    datas.append(data)

  cursor.close()

  return render_template("employee.html", datas = datas)

# page of department
@app.route('/department')
def department():
  datas = []
  cursor = g.conn.execute("SELECT d_id, department_name, department_country, \
    department_city, department_authority FROM department")
  for result in cursor:
    var_dep = result['department_authority']
    if var_dep == 1:
      var_dep = 'TRUE'
    else:
      var_dep = 'FALSE'
    data = {
      'd_id': result['d_id'],
      'department_name': result['department_name'],
      'department_country': result['department_country'],
      "department_city": result['department_city'],
      'department_authority': var_dep,
    }
    datas.append(data)

  cursor.close()

  return render_template("department.html", datas = datas)

# page of deal
@app.route('/deal')
def deal():
  datas = []
  cursor = g.conn.execute("SELECT deal_id, deal_date, promotion_strategy \
    FROM deal")
  for result in cursor:
    data = {
      'deal_id': result['deal_id'],
      'deal_date': result['deal_date'],
      'promotion_strategy': result['promotion_strategy'],
    }
    datas.append(data)

  cursor.close()

  return render_template("deal.html", datas = datas)

# page of customer
@app.route('/customer')
def customer():
  datas = []
  cursor = g.conn.execute("SELECT customer_id, gender, membership, \
    phone_number, customer_city, customer_country, customer_zipcode, \
    customer_timezone FROM customer")
  for result in cursor:
    data = {
      'customer_id': result['customer_id'],
      'gender': result['gender'],
      'membership': result['membership'],
      "phone_number": result['phone_number'],
      'customer_city': result['customer_city'],
      'customer_country': result['customer_country'],
      'customer_zipcode': result['customer_zipcode'],
      'customer_timezone': result['customer_timezone'],
    }
    datas.append(data)

  cursor.close()

  return render_template("customer.html", datas = datas)

# page of cart
@app.route('/cart')
def cart():
  datas = []
  cursor = g.conn.execute("SELECT cart_id, customer_id, quantity FROM cart")
  for result in cursor:
    data = {
      'cart_id': result['cart_id'],
      'customer_id': result['customer_id'],
      'quantity': result['quantity'],
    }
    datas.append(data)

  cursor.close()

  return render_template("cart.html", datas = datas)

# page of product
@app.route('/product')
def product():
  datas = []
  cursor = g.conn.execute("SELECT p_id, inventory, price, view_date, size, \
    weight, status, product_city, product_country FROM product")
  for result in cursor:
    data = {
      'p_id': result['p_id'],
      'inventory': result['inventory'],
      'price': result['price'],
      "view_date": result['view_date'],
      'size': result['size'],
      'weight': result['weight'],
      'status': result['status'],
      'product_city': result['product_city'],
      'product_country': result['product_country'],
    }
    datas.append(data)

  cursor.close()

  return render_template("product.html", datas = datas)



# page of order
@app.route('/order_delete',methods=['GET'])
def order_delete():
  o_id= request.args["o_id"]
  g.conn.execute("delete FROM ord where o_id="+o_id)
  return redirect('/order')

@app.route('/order_add',methods=['POST'])
def order_add():
  form = request.form
  sql = f"insert into ord(o_id,total_price,created_date,order_country,order_city,order_zipcode) \
    values({form['o_id']},'{form['total_price']}','{form['created_date']}',{form['order_country']},'{form['order_city']}',{form['order_zipcode']})"
  g.conn.execute(sql)
  return redirect('/order')

@app.route('/order_update',methods=['POST'])
def order_update():
  form = request.form
  sql = f"update ord set \
        total_price='{form['total_price']}', \
       created_date ='{form['created_date']}',order_country='{form['order_country']}', order_city={form['order_city']}, order_zipcode={form['order_zipcode']}\
        where o_id={form['o_id']}"
  g.conn.execute(sql)
  return redirect('/order')


@app.route('/order')
def order():
  datas = []
  cursor = g.conn.execute("SELECT o_id, total_price, created_date, \
    order_city, order_country, order_zipcode FROM ord")
  for result in cursor:
    data = {
      'o_id': result['o_id'],
      'total_price': result['total_price'],
      'created_date': result['created_date'],
      "order_city": result['order_city'],
      'order_country': result['order_country'],
      'order_zipcode': result['order_zipcode'],
    }
    datas.append(data)

  cursor.close()

  return render_template("order.html", datas = datas)

# page of order_manage
@app.route('/order_manage')
def order_manage():
  datas = []
  cursor = g.conn.execute("SELECT E.ssn, OM.o_id, OM.operation_date, E.first_name, \
    E.last_name FROM ord_manage OM, employee E \
    WHERE E.ssn = OM.ssn")
  for result in cursor:
    data = {
      'ssn': result['ssn'],
      'o_id': result['o_id'],
      'operation_date': result['operation_date'],
    }
    datas.append(data)

  cursor.close()

  return render_template("order_manage.html", datas = datas)

# page of product_manage
@app.route('/product_manage')
def product_manage():
  datas = []
  cursor = g.conn.execute("SELECT E.ssn, E.first_name, E.last_name, PM.p_id \
    FROM product_manage PM, employee E \
    WHERE E.ssn = PM.ssn")
  for result in cursor:
    data = {
      'ssn': result['ssn'],
      'first_name': result['first_name'],
      'last_name': result['last_name'],
      "p_id": result['p_id'],
    }
    datas.append(data)

  cursor.close()

  return render_template("product_manage.html", datas = datas)


# page of create_p_o
@app.route('/create_p_o')
def create_p_o():
  datas = []
  cursor = g.conn.execute("SELECT p_id, o_id FROM create_p_o")
  for result in cursor:
    data = {
      'p_id': result['p_id'],
      'o_id': result['o_id'],
    }
    datas.append(data)

  cursor.close()

  return render_template("create_p_o.html", datas = datas)



# page of select
@app.route('/select')
def select():
  datas = []
  cursor = g.conn.execute("SELECT p_id, customer_id FROM selec")
  for result in cursor:
    data = {
      'p_id': result['p_id'],
      'customer_id': result['customer_id'],
    }
    datas.append(data)

  cursor.close()

  return render_template("select.html", datas = datas)

@app.route('/select_delete',methods=['GET'])
def select_delete():
  p_id,customer_id = request.args["p_id"],request.args["customer_id"]
  g.conn.execute("delete FROM selec where p_id="+p_id+" and customer_id="+customer_id)
  return redirect('/select')

@app.route('/select_add',methods=['POST'])
def select_add():
  p_id,customer_id = request.form["p_id"],request.form["customer_id"]
  sql = f"insert into selec(p_id,customer_id) values({p_id},{customer_id})"
  g.conn.execute(sql)
  return redirect('/select')

@app.route('/select_update',methods=['POST'])
def select_update():
  p_id,customer_id = request.form["p_id"],request.form["customer_id"]
  p_id_old,customer_id_old = request.form["p_id_old"],request.form["customer_id_old"]
  sql = f"update selec set p_id={p_id},customer_id={customer_id} where p_id={p_id_old} and customer_id={customer_id_old}"
  g.conn.execute(sql)
  return redirect('/select')

# page of create_c_o
@app.route('/create_c_o')
def create_c_o():
  datas = []
  cursor = g.conn.execute("SELECT cart_id, o_id FROM create_c_o")
  for result in cursor:
    data = {
      'cart_id': result['cart_id'],
      'o_id': result['o_id'],
    }
    datas.append(data)

  cursor.close()

  return render_template("create_c_o.html", datas = datas)

# page of show
@app.route('/show')
def show():
  datas = []
  cursor = g.conn.execute("SELECT p_id, cart_id FROM show")
  for result in cursor:
    data = {
      'p_id': result['p_id'],
      'cart_id': result['cart_id'],
    }
    datas.append(data)

  cursor.close()

  return render_template("show.html", datas = datas)

# page of deside
@app.route('/deside')
def deside():
  datas = []
  cursor = g.conn.execute("SELECT deal_id, d_id FROM deside")
  for result in cursor:
    data = {
      'deal_id': result['deal_id'],
      'd_id': result['d_id'],
    }
    datas.append(data)

  cursor.close()

  return render_template("deside.html", datas = datas)

# page of monitor
@app.route('/monitor')
def monitor():
  datas = []
  cursor = g.conn.execute("SELECT d_id, p_id FROM monitor")
  for result in cursor:
    data = {
      'p_id': result['p_id'],
      'd_id': result['d_id'],
    }
    datas.append(data)

  cursor.close()

  return render_template("monitor.html", datas = datas)

@app.route('/another')
def another():
  return render_template("another.html")

# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  g.conn.execute('INSERT INTO test VALUES (NULL, ?)', name)
  return redirect('/')


@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='localhost')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

    HOST, PORT = host, port
    print ("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=True, threaded=threaded)


  run()
