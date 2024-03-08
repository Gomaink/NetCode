from flask import Flask, render_template, session, redirect, request, url_for
from config.database import init_db, db, User, Post, PostStars
from flask_bcrypt import Bcrypt
from sqlalchemy import func 

# Instanciando a aplicação
app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'  
bcrypt = Bcrypt(app)
init_db(app)

# Rotas da aplicação
@app.route('/')
def index():
    try:
        subquery = db.session.query(func.count(PostStars.post_id).label('star_count'), PostStars.post_id) \
            .group_by(PostStars.post_id).subquery()

        posts = db.session.query(User.username, Post.id, Post.title, Post.created_at, subquery.c.star_count) \
            .join(Post, Post.user_id == User.id) \
            .outerjoin(subquery, Post.id == subquery.c.post_id) \
            .order_by(subquery.c.star_count.desc()) \
            .all()

        posts = [(username, post_id, title, created_at, star_count or 0) for username, post_id, title, created_at, star_count in posts]

        return render_template('index.html', posts=posts)
    except Exception as e:
        error_message = "Erro ao recuperar os posts: " + str(e)
        return render_template('index.html', error_message=error_message)
    

@app.route('/recent')
def recent():
    try:
        subquery = db.session.query(func.count(PostStars.post_id).label('star_count'), PostStars.post_id) \
            .group_by(PostStars.post_id).subquery()
        
        posts = db.session.query(User.username, Post.id, Post.title, Post.created_at, subquery.c.star_count) \
            .join(Post, Post.user_id == User.id) \
            .outerjoin(subquery, Post.id == subquery.c.post_id) \
            .order_by(Post.created_at.desc()) \
            .all()
        
        posts = [(username, post_id, title, created_at, star_count or 0) for username, post_id, title, created_at, star_count in posts]
        
        return render_template('index.html', posts=posts)
    except Exception as e:
        error_message = "Erro ao recuperar os posts: " + str(e)
        return render_template('recent.html', error_message=error_message)
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if not username or not password:
            error_message = "Por favor, preencha todos os campos."
            return render_template('login.html', error_message=error_message)
        
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            # Se a senha estiver correta, criar uma sessão para o usuário
            session['user_id'] = user.id
            return redirect(url_for('index'))
        else:
            error_message = "Usuário ou senha incorretos."
            return render_template('login.html', error_message=error_message)
    else:
        return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        print("post")
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if not username or not email or not password:
            error_message = "Por favor, preencha todos os campos."
            return render_template('register.html', error_message=error_message)

        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            error_message = "O nome de usuário já está em uso."
            return render_template('register.html', error_message=error_message)
        
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            error_message = "O e-mail já está em uso."
            return render_template('register.html', error_message=error_message)
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        if new_user and bcrypt.check_password_hash(new_user.password, password):
            session['user_id'] = new_user.id
            return redirect(url_for('index'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/thread/<int:postid>')
def thread(postid):
    post = Post.query.filter_by(id=postid).first()
    if post:
        return render_template('post.html', post=post)
    else:
        return render_template('error.html', error_message="Postagem não encontrada. 404")
    