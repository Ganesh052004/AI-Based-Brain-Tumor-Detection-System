import os
from flask import Flask, jsonify, render_template, request, send_file, redirect, session, url_for, flash
from database import execute_select, execute_insert, execute_insert_return_id, execute_update, execute_delete, check_login
import bcrypt

from datetime import datetime
server_timestamp = datetime.now().strftime("%Y%m%d")


app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['SECRET_KEY'] = '462288428'
s=app.config['SECRET_KEY']


from functools import wraps
from flask import session, redirect, url_for, make_response

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or 'email' not in session:
            return redirect(url_for('login'))

        response = make_response(f(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    return decorated_function


# Routes
@app.route('/')
def index():
    return render_template('Home.html')


# Routes
@app.route('/about')
def about():
    return render_template('About.html')


# Routes
@app.route('/contact')
def contact():
    return render_template('Contact.html')


@app.route('/login')
def login():
    return render_template('Login.html', active_tab="admin")


@app.route('/admin-login', methods=['POST'])
def admin_login():
    email = request.form['admin_username']
    password = request.form['admin_password']

    query = "SELECT * FROM tbladmin WHERE email = %s"
    success, msg, msg_type = check_login(query, email, password)

    if success:
        return redirect(url_for('admin_home'))
    else:
        return render_template('Login.html', msg=msg, msg_type=msg_type, active_tab="admin")


@app.route('/admin-home')
@login_required
def admin_home():
    msg = "Welcome back, Admin!"
    msg_type = "success"
    return render_template('Admin/AdminHome.html', msg=msg, msg_type=msg_type)


# --- Display Users with Optional Message ---
@app.route('/admin/users')
def admin_users():
    msg = request.args.get('msg')
    msg_type = request.args.get('msg_type', 'info')
    users = execute_select("SELECT * FROM tblusers")
    return render_template("Admin/AdminUsersList.html", users=users, msg=msg, msg_type=msg_type)

# --- Edit User ---
@app.route('/admin/edit-user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        mobile = request.form['mobile']
        query = "UPDATE tblusers SET username=%s, email=%s, mobile=%s WHERE id=%s"
        result = execute_update(query, (username, email, mobile, user_id))
        if result:
            return redirect(url_for('admin_users', msg="User updated successfully!", msg_type="success"))
        else:
            return redirect(url_for('admin_users', msg="Failed to update user.", msg_type="danger"))

    user = execute_select("SELECT * FROM tblusers WHERE id = %s", (user_id,))
    if user:
        return render_template("Admin/AdminUsersEdit.html", user=user[0])
    return redirect(url_for('admin_users', msg="User not found.", msg_type="warning"))

# --- Delete User ---
@app.route('/admin/delete-user/<int:user_id>')
def delete_user(user_id):
    success = execute_delete("DELETE FROM tblusers WHERE id = %s", (user_id,))
    if success:
        return redirect(url_for('admin_users', msg="User deleted successfully!", msg_type="success"))
    else:
        return redirect(url_for('admin_users', msg="Failed to delete user.", msg_type="danger"))

# --- Display FAQs ---
@app.route('/admin/faq')
def admin_faq():
    msg = request.args.get('msg')
    msg_type = request.args.get('msg_type', 'info')
    faqs = execute_select("SELECT * FROM tblfaq")
    return render_template("Admin/AdminFAQList.html", faqs=faqs, msg=msg, msg_type=msg_type)

# --- Add FAQ ---
@app.route('/admin/add-faq', methods=['GET', 'POST'])
def add_faq():
    if request.method == 'POST':
        question = request.form['question']
        answer = request.form['answer']
        result = execute_insert("INSERT INTO tblfaq (question, answer) VALUES (%s, %s)", (question, answer))
        if result == True:
            return redirect(url_for('admin_faq', msg="FAQ added successfully!", msg_type="success"))
        else:
            return redirect(url_for('admin_faq', msg="Failed to add FAQ.", msg_type="danger"))
    return render_template("Admin/AdminAddFAQ.html")

# --- Edit FAQ ---
@app.route('/admin/edit-faq/<int:faq_id>', methods=['GET', 'POST'])
def edit_faq(faq_id):
    if request.method == 'POST':
        question = request.form['question']
        answer = request.form['answer']
        result = execute_update("UPDATE tblfaq SET question=%s, answer=%s WHERE id=%s", (question, answer, faq_id))
        if result:
            return redirect(url_for('admin_faq', msg="FAQ updated successfully!", msg_type="success"))
        else:
            return redirect(url_for('admin_faq', msg="Failed to update FAQ.", msg_type="danger"))
    faq = execute_select("SELECT * FROM tblfaq WHERE id = %s", (faq_id,))
    if faq:
        return render_template("Admin/AdminEditFAQ.html", faq=faq[0])
    return redirect(url_for('admin_faq', msg="FAQ not found.", msg_type="warning"))

# --- Delete FAQ ---
@app.route('/admin/delete-faq/<int:faq_id>')
def delete_faq(faq_id):
    success = execute_delete("DELETE FROM tblfaq WHERE id = %s", (faq_id,))
    if success:
        return redirect(url_for('admin_faq', msg="FAQ deleted successfully!", msg_type="success"))
    else:
        return redirect(url_for('admin_faq', msg="Failed to delete FAQ.", msg_type="danger"))


# --- Display Health Tips with Optional Message ---
@app.route('/admin/health-tips')
def admin_health_tips():
    msg = request.args.get('msg')
    msg_type = request.args.get('msg_type', 'info')
    health_tips = execute_select("SELECT * FROM tblhealthtips ORDER BY id DESC")
    return render_template("Admin/AdminHealthTipsList.html", health_tips=health_tips, msg=msg, msg_type=msg_type)


# --- Add Health Tip ---
@app.route('/admin/add-health-tip', methods=['GET', 'POST'])
def add_health_tip():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        query = "INSERT INTO tblhealthtips (title, description) VALUES (%s, %s)"
        result = execute_insert(query, (title, description))
        if result == True:
            return redirect(url_for('admin_health_tips', msg="Health tip added successfully!", msg_type="success"))
        else:
            return redirect(url_for('admin_health_tips', msg="Failed to add health tip.", msg_type="danger"))
    return render_template("Admin/AdminHealthTipForm.html", action="Add", health_tip=None)


# --- Edit Health Tip ---
@app.route('/admin/edit-health-tip/<int:tip_id>', methods=['GET', 'POST'])
def edit_health_tip(tip_id):
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        query = "UPDATE tblhealthtips SET title=%s, description=%s WHERE id=%s"
        result = execute_update(query, (title, description, tip_id))
        if result:
            return redirect(url_for('admin_health_tips', msg="Health tip updated successfully!", msg_type="success"))
        else:
            return redirect(url_for('admin_health_tips', msg="Failed to update health tip.", msg_type="danger"))

    tip = execute_select("SELECT * FROM tblhealthtips WHERE id = %s", (tip_id,))
    if tip:
        return render_template("Admin/AdminHealthTipForm.html", action="Edit", health_tip=tip[0])
    return redirect(url_for('admin_health_tips', msg="Health tip not found.", msg_type="warning"))


# --- Delete Health Tip ---
@app.route('/admin/delete-health-tip/<int:tip_id>')
def delete_health_tip(tip_id):
    success = execute_delete("DELETE FROM tblhealthtips WHERE id = %s", (tip_id,))
    if success:
        return redirect(url_for('admin_health_tips', msg="Health tip deleted successfully!", msg_type="success"))
    else:
        return redirect(url_for('admin_health_tips', msg="Failed to delete health tip.", msg_type="danger"))


@app.route('/adminlogout')
def adminlogout():
    # Clear the entire session to log out the user
    session.clear()
    # Redirect to login page (or wherever you want)
    return redirect(url_for('login'))




@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = None
    msg_type = None

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        mobile = request.form['mobile']
        password = request.form['password']

        # Check if user exists
        user_check = execute_select("SELECT * FROM tblusers WHERE email = %s", (email,))
        if user_check and isinstance(user_check, list) and len(user_check) > 0:
            msg = "Email already registered. Please login or use another email."
            msg_type = "danger"
            return render_template('register.html', msg=msg, msg_type=msg_type)

        # Hash and insert
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        insert_query = """
            INSERT INTO tblusers (username, email, mobile, password)
            VALUES (%s, %s, %s, %s)
        """
        result = execute_insert(insert_query, (username, email, mobile, hashed_pw))

        if result is True:
            # Redirect to login with user tab active
            return render_template('Login.html', msg="Registration successful! Please login.", msg_type="success", active_tab="user")
        else:
            msg = f"Error during registration: {result}"
            msg_type = "danger"
            return render_template('register.html', msg=msg, msg_type=msg_type)

    return render_template('register.html')



@app.route('/user-login', methods=['POST'])
def user_login():
    email = request.form['user_username']
    password = request.form['user_password']

    query = "SELECT * FROM tblusers WHERE email = %s"
    success, msg, msg_type = check_login(query, email, password)

    if success:
        return redirect(url_for('user_dashboard'))
    else:
        return render_template('Login.html', msg=msg, msg_type=msg_type, active_tab="user")


@app.route('/user_dashboard')
@login_required
def user_dashboard():
    msg = "Welcome back, User!"
    msg_type = "success"
    return render_template('User/UserHome.html', msg=msg, msg_type=msg_type)

@app.route('/user/health-tips')
def user_health_tips():
    try:
        health_tips = execute_select("SELECT * FROM tblhealthtips ORDER BY id DESC")
        return render_template('User/UserHealthTipsList.html', health_tips=health_tips)
    except Exception as e:
        print("Error fetching health tips:", e)
        return render_template('User/UserHealthTipsList.html', health_tips=[], msg="Unable to fetch health tips.", msg_type="danger")
    
@app.route('/user/faq')
def user_faq():
    try:
        faqs = execute_select("SELECT * FROM tblFAQ ORDER BY id DESC")
        return render_template('User/UserFAQList.html', faqs=faqs)
    except Exception as e:
        print("Error fetching FAQs:", e)
        return render_template('User/UserFAQList.html', faqs=[], msg="Unable to fetch FAQs.", msg_type="danger")



@app.route('/userlogout')
def userlogout():
    # Clear the entire session to log out the user
    session.clear()
    # Redirect to login page (or wherever you want)
    return redirect(url_for('login'))









from flask import Flask, render_template, request
from keras.models import load_model
from PIL import Image
import numpy as np
import os



# Load model once at app startup
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model = load_model(os.path.join(BASE_DIR, 'model', 'brain_tumor_classifier_model.keras'))

# Upload folder
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/user/prediction', methods=['GET', 'POST'])
def user_prediction():
    if request.method == 'POST':
        try:
            file = request.files['image']
            if file.filename == '':
                return render_template('User/UserPrediction.html', msg='No file selected.', msg_type='warning')

            # Save uploaded image
            filename = file.filename
            image_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(image_path)

            # Preprocess image
            img = Image.open(image_path).convert('RGB').resize((128, 128))
            img_array = np.array(img) / 255.0
            img_array = img_array.reshape(1, 128, 128, 3)

            # Make prediction
            prediction = model.predict(img_array)
            predicted_class = int(prediction[0][0] > 0.5)

            result = "No Tumor Detected" if predicted_class == 1 else "Tumor Detected"

            return render_template('User/UserPrediction.html', 
                                   filename=filename,
                                   result=result,
                                   msg="Prediction complete.",
                                   msg_type="success")
        except Exception as e:
            print("Prediction error:", e)
            return render_template('User/UserPrediction.html', msg='Error during prediction.', msg_type='danger')

    # GET method
    return render_template('User/UserPrediction.html')




if __name__ == '__main__':
    app.run(debug=True)
