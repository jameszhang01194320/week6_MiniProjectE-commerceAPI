# Lesson 3: MiniProjectE-commerceAPI
# ________________________________________


"""
1. Create a new directory for the project:
    
    mkdir MiniProjectE-commerceAPI

2.  Set up a virtual environment:
    python -m venv venv

3. Activate the virtual environment:
    # On Windows:
    venv/Scripts/activate

    Activate the virtual environment:
    # On Windows:
    venv/Scripts/activate

    Install Necessary Packages:
    pip install flask
    pip install flask_sqlalchemy
    pip install marshmallow
    pip install flask_marshmallow
    pip install marshmallow-sqlalchemy
    pip install mysql-connector-python


4. Create a Python file app.py for Flask application and set up the database connection.
The reasons for importing each module:
import logging：
Used to record the running log of the application, helping you track and diagnose problems, understand the execution process of the program, and monitor the status of the system.
from flask import Flask, request, jsonify：
Flask: It is the core class of the Flask framework and is used to create a Flask application instance.
request: Used to obtain data in the HTTP request sent by the client.
jsonify: Used to convert data into JSON format and generate the corresponding HTTP response.
from flask_sqlalchemy import SQLAlchemy：
Provides SQLAlchemy support integrated with Flask applications to facilitate database operations and management.
from sqlalchemy import exc：
Import SQLAlchemy's exception classes to catch and handle specific exceptions when processing database operations.
from datetime import datetime：
Used to handle date and time related operations, such as recording the timestamp of an operation or processing time-related data.
from flask_marshmallow import Marshmallow：
Used to serialize and deserialize data, usually converting data formats when interacting with databases and generating API responses.
from sqlalchemy.exc import SQLAlchemyError：
Imports specifically SQLAlchemy-related error types to allow for more precise handling of errors that may occur in database operations.

"""

import logging
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
from datetime import datetime
from flask_marshmallow import Marshmallow
from sqlalchemy.exc import SQLAlchemyError 
from marshmallow import fields#, Schema
from marshmallow import fields#, post_load
from datetime import datetime
from marshmallow import fields#, post_dump

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:8832@localhost/ecom'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# init SQLAlchemy
db = SQLAlchemy(app)

# init Marshmallow
ma = Marshmallow(app)


class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    phone_number = db.Column(db.String(20), nullable=False)
    # Relationship fields can be added if they need to be associated with an order
    orders1234 = db.relationship('Order', backref='customer', lazy=True)

    def __repr__(self):
        return f"<Customer {self.name}>"

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), nullable=False, unique=True)  # order_date = db.Column(db.DateTime, default=datetime.now)
    order_date = db.Column(db.DateTime, default=datetime.now(), nullable=False)  
    expected_delivery_date = db.Column(db.DateTime)
    total_amount = db.Column(db.Float, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # status of
    order_items = db.relationship('OrderItem', back_populates='order')

    def __repr__(self):
        return f"<Order {self.order_number}>"
    
class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer, nullable=False)
    order = db.relationship('Order', back_populates='order_items')
    product = db.relationship('Product', back_populates='order_items')

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False)
    threshold = db.Column(db.Integer, nullable=False)
    restock_level = db.Column(db.Integer, nullable=False)
    
    orders987 = db.relationship('Order', backref='product', lazy=True)
    order_items = db.relationship('OrderItem', back_populates='product')

    def __repr__(self):
        return f"<Product {self.name}>"

class CustomerAccount(db.Model):
    __tablename__ = 'customer_accounts'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    customer = db.relationship('Customer', backref=db.backref('account', uselist=False))

# Customer schema
class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer

 # init schema
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)


# Order schema
class OrderSchema(ma.SQLAlchemyAutoSchema):
    order_date = fields.DateTime(missing=lambda: datetime.now())
    expected_delivery_date = fields.DateTime()
    customer_name = fields.Method("get_customer_name")
    product_name = fields.Method("get_product_name")

    class Meta:
        model = Order
        include_fk = True  # Include foreign key fields

    def get_customer_name(self, obj):
        return obj.customer.name if obj.customer else None

    def get_product_name(self, obj):
        return obj.product.name if obj.product else None

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)


# Product schema
class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)


class CustomerAccountSchema(ma.SQLAlchemyAutoSchema):
    customer_id = fields.Int()
    
    class Meta:
        model = CustomerAccount
        include_fk = True  # Ensure foreign keys are included
        exclude = ("customer",)  # Exclude the customer field

customer_account_schema = CustomerAccountSchema()
customer_accounts_schema = CustomerAccountSchema(many=True)



# Set up logging
logging.basicConfig(level=logging.DEBUG)

# create all table

with app.app_context():
    db.create_all()

# Create new customer
@app.route('/customers', methods=['POST'])
def add_customer():
    data = request.get_json()
    try:
        logging.debug(f"Adding new customer with data {data}")
        new_customer = Customer(name=data['name'], email=data['email'], phone_number=data['phone_number'])
        db.session.add(new_customer)
        db.session.commit()
        return jsonify({'messphone_number': 'New customer added'}), 201
    except exc.SQLAlchemyError as e:
        logging.error(f"Error adding customer: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# Get all customers
@app.route('/customers', methods=['GET'])
def get_customers():
    try:
        logging.debug("Fetching all customers from the database")
        all_customers = Customer.query.all()
        result = [{'id': customer.id, 'name': customer.name, 'email': customer.email, 'phone_number': customer.phone_number} for customer in all_customers]
        return jsonify(result), 200
    except exc.SQLAlchemyError as e:
        logging.error(f"Error fetching customers: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/customers/<int:id>', methods=['GET'])
def get_customer(id):
    try:
        logging.debug(f"Fetching customer with id {id}")
        customer = db.session.get(Customer, id)
        if not customer:
            logging.warning(f"Customer with id {id} not found")
            return jsonify({'error': 'Customer not found'}), 404
        result = {'id': customer.id, 'name': customer.name, 'email': customer.email, 'phone_number': customer.phone_number}
        return jsonify(result), 200
    except exc.SQLAlchemyError as e:
        logging.error(f"Error fetching customer: {str(e)}")
        return jsonify({'error': str(e)}), 400


@app.route('/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400

    app.logger.info(f"Received data for update: {data}")

    name = data.get('name')
    email = data.get('email')
    phone_number = data.get('phone_number')

    try:
        customer = db.session.get(Customer, id)
        if not customer:
            return jsonify({"error": "Customer not found"}), 404

        app.logger.info(f"Original customer data: {customer_schema.dump(customer)}")

        if name:
            customer.name = name
        if email:
            customer.email = email
        if phone_number:
            customer.phone_number = phone_number

        app.logger.info(f"Customer data before commit: {customer_schema.dump(customer)}")

        db.session.commit()

        app.logger.info(f"Customer data after commit: {customer_schema.dump(customer)}")
        return jsonify({"message": "Customer updated successfully", "customer": customer_schema.dump(customer)}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        app.logger.error(f"Error updating customer: {e}")
        return jsonify({"error": str(e)}), 400


# Delete customer
@app.route('/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    try:
        logging.debug(f"Deleting customer with id {id}")
        customer = db.session.get(Customer, id)
        if not customer:
            logging.warning(f"Customer with id {id} not found")
            return jsonify({'error': 'Customer not found'}), 404
        db.session.delete(customer)
        db.session.commit()
        return jsonify({'message': 'Customer deleted'}), 200
    except exc.SQLAlchemyError as e:
        logging.error(f"Error deleting customer: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# Place a Order

@app.route('/orders', methods=['POST'])
def place_order():
    try:
        data = request.get_json()

        #  Manually set the default value order_date if it does not exist
        if 'order_date' not in data:
            data['order_date'] = datetime.now().isoformat()  # Ensure that dates are passed in ISO format

        # Handling of the new status field
        if'status' not in data:
            data['status'] = 'pending'  # Set the default state to 'pending'


        # Create Order object and populate it with data
        # Generate order number: ORD + current timestamp
        order_number = 'ORD' + datetime.now().strftime('%Y%m%d%H%M%S')
        order = Order(
            order_number=order_number,
            order_date=data['order_date'],
            expected_delivery_date=data['expected_delivery_date'],  
            total_amount=data['total_amount'],
            customer_id=data['customer_id'],
            product_id=data['product_id'],
            status=data['status']  # add status
        )
        
        #Add (order_items) 
        order_items_data = data.get('order_items', [])
        for item_data in order_items_data:
            product_id = item_data.get('product_id')
            quantity = item_data.get('quantity')
            
            # Check product information
            product = db.session.query(Product).filter(Product.id == product_id).first()
            if not product:
                return jsonify({"error": f"Product with ID {product_id} not found"}), 404
            
            # Create an order item object and associate it with an order
            order_item = OrderItem(
                product_id=product_id,
                quantity=quantity,
                product=product,
                order=order  # Related Orders
            )
            order.order_items.append(order_item)

         # Save orders and order items to the database   
        
        db.session.add(order)
        db.session.commit()
        return jsonify({"message": "Order created successfully", "order": {
            "order_id": order.id,
            "order_number": order.order_number,
            "order_date": order.order_date,
            "expected_delivery_date": order.expected_delivery_date,
            "total_amount": order.total_amount,
            "customer_id": order.customer_id,
            "status": order.status,
            "order_items": [{
                "product_id": item.product_id,
                "quantity": item.quantity
            } for item in order.order_items]
        }}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 400



def format_order(order):
    return {
        "id": order.id,
        "order_number": order.order_number,
        "order_date": order.order_date.isoformat(),
        "expected_delivery_date": order.expected_delivery_date.isoformat(),
        "total_amount": order.total_amount,
        "product_id": order.product_id,
        "product_name": order.product.name,
        "customer_id": order.customer_id,
        "customer_name": order.customer.name,
        "status": order.status  
    }

@app.route('/orders', methods=['GET'])
def get_all_orders():
    try:
        orders = Order.query.all()
        return jsonify([format_order(order) for order in orders]), 200
    except exc.SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 400
    


@app.route('/orders/<int:id>', methods=['GET'])
def get_order(id):
    try:
        order = Order.query.get_or_404(id)
        return jsonify(format_order(order)), 200
    except exc.SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 400
    


@app.route('/customers/<int:customer_id>/orders', methods=['GET'])
def get_order_history(customer_id):
    try:
        orders = Order.query.filter_by(customer_id=customer_id).all()
        return jsonify(orders_schema.dump(orders)), 200
    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 400
      


@app.route('/orders/<int:id>', methods=['PUT'])
def update_order(id):
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400

    try:
        order = Order.query.get(id)
        if not order:
            return jsonify({"error": "Order not found"}), 404

        # Update the order with the provided data
        if 'status' in data:
            order.status = data['status']
        # Add other fields to be updated here if needed

        db.session.commit()

        return jsonify({"message": "Order updated successfully", "order": order_schema.dump(order)}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400



@app.route('/orders/<int:id>', methods=['DELETE'])
def delete_order(id):
    try:
        order = db.session.get(Order, id)
        if not order:
            return jsonify({"error": "Order not found"}), 404

        db.session.delete(order)
        db.session.commit()
        return jsonify({"message": "Order deleted successfully"}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


# Product
@app.route('/products', methods=['POST'])
def create_product():
    try:
        data = request.get_json()
        new_product = Product(
            name=data['name'],
            description=data['description'],
            price=data['price'],
            stock_quantity=data['stock_quantity'],
            threshold=data['threshold'],
            restock_level=data['restock_level']
        )
        db.session.add(new_product)
        db.session.commit()
        return jsonify({"message": "Product created successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@app.route('/products', methods=['GET'])
def get_all_products():
    try:
        products = Product.query.all()
        return jsonify(product_schema.dump(products, many=True)), 200
    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    try:
        product = db.session.get(Product, id)
        if not product:
            return jsonify({"error": "Product not found"}), 404
        return jsonify(product_schema.dump(product)), 200
    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400

    try:
        product = db.session.get(Product, id)
        if not product:
            return jsonify({"error": "Product not found"}), 404

        product.name = data.get('name', product.name)
        product.description = data.get('description', product.description)
        product.price = data.get('price', product.price)
        product.stock_quantity = data.get('stock_quantity', product.stock_quantity)
        product.threshold = data.get('threshold', product.threshold)
        product.restock_level = data.get('restock_level', product.restock_level)

        db.session.commit()
        return jsonify({"message": "Product updated successfully", "product": product_schema.dump(product)}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    try:
        product = db.session.get(Product, id)
        if not product:
            return jsonify({"error": "Product not found"}), 404

        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": "Product deleted successfully"}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.route('/restock', methods=['POST'])
def restock_products():
    try:
        products_to_restock = Product.query.filter(Product.stock_quantity < Product.threshold).all()
        restocked_products = []
        
        for product in products_to_restock:
            product.stock_quantity += product.restock_level
            restocked_products.append(product_schema.dump(product))
        
        db.session.commit()
        
        return jsonify({
            "message": "Products restocked successfully",
            "restocked_products": restocked_products
        }), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.route('/check_stock_levels', methods=['GET'])
def check_stock_levels():
    try:
        low_stock_products = Product.query.filter(Product.stock_quantity < Product.threshold).all()
        return jsonify({
            "low_stock_products": [product_schema.dump(product) for product in low_stock_products]
        }), 200
    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 400

# Customer_Account

# @app.route('/customer_accounts', methods=['POST'])
# def create_customer_account():
#     data = request.get_json()

#     if not data:
#         return jsonify({"error": "Invalid JSON data"}), 400

#     try:
#         customer_account = CustomerAccount(
#             username=data['username'],
#             password=data['password'],
#             customer_id=data['customer_id']
#         )
#         db.session.add(customer_account)
#         db.session.commit()
#         return jsonify({"message": "Customer account created successfully", "customer_account": customer_account_schema.dump(customer_account)}), 201
#     except SQLAlchemyError as e:
#         db.session.rollback()
#         return jsonify({"error": str(e)}), 400

@app.route('/customer_accounts', methods=['POST'])
def create_customer_account():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400

    # Check for missing keys in the request data
    required_keys = ['username', 'password', 'customer_id']
    missing_keys = [key for key in required_keys if key not in data]

    if missing_keys:
        return jsonify({"error": f"Missing keys in JSON data: {', '.join(missing_keys)}"}), 400

    try:
        customer_account = CustomerAccount(
            username=data['username'],
            password=data['password'],
            customer_id=data['customer_id']
        )
        db.session.add(customer_account)
        db.session.commit()
        return jsonify({"message": "Customer account created successfully", "customer_account": customer_account_schema.dump(customer_account)}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400



@app.route('/customer_accounts', methods=['GET'])
def get_all_customer_accounts():
    try:
        customer_accounts = CustomerAccount.query.all()
        result = customer_accounts_schema.dump(customer_accounts)
        return jsonify(result), 200
    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/customer_accounts/<int:id>', methods=['GET'])
def get_customer_account(id):
    try:
        customer_account = CustomerAccount.query.get(id)
        if not customer_account:
            return jsonify({"error": "Customer account not found"}), 404
        
        result = customer_account_schema.dump(customer_account)
        return jsonify(result), 200
    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 400




@app.route('/customer_accounts/<int:id>', methods=['PUT'])
def update_customer_account(id):
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400

    try:
        customer_account = db.session.get(CustomerAccount, id)
        if not customer_account:
            return jsonify({"error": "Customer account not found"}), 404

        customer_account.username = data.get('username', customer_account.username)
        customer_account.password = data.get('password', customer_account.password)
        customer_account.customer_id = data.get('customer_id', customer_account.customer_id)

        db.session.commit()
        return jsonify({"message": "Customer account updated successfully", "customer_account": customer_account_schema.dump(customer_account)}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.route('/customer_accounts/<int:id>', methods=['DELETE'])
def delete_customer_account(id):
    try:
        customer_account = db.session.get(CustomerAccount, id)
        if not customer_account:
            return jsonify({"error": "Customer account not found"}), 404

        db.session.delete(customer_account)
        db.session.commit()
        return jsonify({"message": "Customer account deleted successfully"}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400



if __name__ == '__main__':
    app.run(debug=True)


