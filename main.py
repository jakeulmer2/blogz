from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:Cheese!!123321@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(6000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.before_request
def require_login():
    allowed_routes = ['login', 'list_blogs', 'index', 'signup', 'static']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/blog', methods=['POST', 'GET'])
def list_blogs():
    if request.method == "GET" and "id" in request.args:
        id = request.args.get("id")
        blog_id = Blog.query.filter_by(id=id).first()
        owner_id = blog_id.owner
        return render_template("single_blog.html", title="Blog Post", blog_id=blog_id, owner_id=owner_id)

    if request.method == "GET" and "username" in request.args:
        username = request.args.get("username")
        
        user_id = User.query.filter_by(username=username).first()
        user_posts = Blog.query.filter_by(owner=user_id).all()
        return render_template("singleUser.html", title=username + "'s" + " Posts", user_posts=user_posts, username=username, user_id=user_id)

    blogs = Blog.query.all()
    return render_template('main_blog.html',title="All Blogs", 
        blogs=blogs)


@app.route('/newpost', methods=['POST'])
def add_newpost():

    blog_title = request.form['blog_title']
    entry_body = request.form['entry_body']
    owner = User.query.filter_by(username=session['username']).first()

    blog_title_error = ''
    entry_body_error = ''

    if len(blog_title) == 0:
        blog_title_error = 'No title entered'
        blog_title = ''

    if len(entry_body) == 0:
        entry_body_error = 'No entry'
        entry_body = ''

    if not blog_title_error and not entry_body_error:
        new_blog = Blog(blog_title, entry_body, owner)
        db.session.add(new_blog)
        db.session.commit()
        id = str(new_blog.id)
        return redirect('/blog?id=' + id)
        
    else:
        return render_template('newpost.html', 
            blog_title_error=blog_title_error, 
            entry_body_error=entry_body_error, 
            blog_title=blog_title, 
            entry_body=entry_body)

@app.route('/newpost', methods=['GET'])
def add_newpost_get():
    if request.method == 'GET':
        return render_template('newpost.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        username_error = ''
        password_error = ''
        verify_error = ''

        if len(username) == 0:
            username_error = 'No username entered'
            username = ''
        elif len(username) < 3 or len(username) > 20:
            username_error = 'Username out of 3-20 char range'
            username = ''
        elif " " in username:
            username_error = 'Username cannot contain spaces'
            username = ''


        if len(password) == 0:
            password_error = 'No password entered'
            password = ''
        elif len(password) < 3 or len(password) > 20:
            password_error = 'Password out of 3-20 char range'
            password = ''
        elif " " in password:
            password_error = 'Password cannot contain spaces'
            password = ''


        if len(verify) == 0:
            verify_error = 'No verification password entered'
            verify = ''
        elif len(verify) < 3 or len(verify) > 20:
            verify_error = 'Verification password out of 3-20 char range'
            verify = ''
        elif " " in verify:
            verify_error = 'Verification password cannot contain spaces'
            verify = ''
        elif verify != password:
            verify_error = 'Verification password entered does not match password'
            verify = ''

  

        if not username_error and not password_error and not verify_error:
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')
            else:
                # TODO - user better response messaging
                return "<h1>User Already Exists</h1>"
            
        
        else:
            return render_template('signup.html', 
                username_error=username_error, 
                password_error=password_error, 
                verify_error=verify_error,  
                username=username, password=password, 
                verify=verify)

    return render_template('signup.html', title="Signup")

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html', title="Login")

@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template('index.html',title="Blogz Home", 
        users=users)

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')
    



if __name__ == '__main__':
    app.run()