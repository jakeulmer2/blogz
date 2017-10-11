from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:Cheese!!123321@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(6000))

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/blog', methods=['POST', 'GET'])
def index():
    if request.method == "GET" and "id" in request.args:
        id = request.args.get("id")
        blog_id = Blog.query.filter_by(id=id).first()
        return render_template("single_blog.html", title="Blog Post", blog_id=blog_id)

    blogs = Blog.query.all()
    return render_template('main_blog.html',title="Build A Blog", 
        blogs=blogs)


@app.route('/newpost', methods=['POST'])
def add_newpost():

    blog_title = request.form['blog_title']
    entry_body = request.form['entry_body']

    blog_title_error = ''
    entry_body_error = ''

    if len(blog_title) == 0:
        blog_title_error = 'No title entered'
        blog_title = ''

    if len(entry_body) == 0:
        entry_body_error = 'No entry'
        entry_body = ''

    if not blog_title_error and not entry_body_error:
        new_blog = Blog(blog_title, entry_body)
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



if __name__ == '__main__':
    app.run()