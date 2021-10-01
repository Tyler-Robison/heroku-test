from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Tweet
from forms import UserForm, TweetForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///auth_demo"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)

toolbar = DebugToolbarExtension(app)


@app.route('/')
def home_page():
    return render_template('index.html')

@app.route('/register', methods=["GET", "POST"])    
def register():
    """Registers a user"""

    form = UserForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        try:
            new_user = User.register(username, password)
            db.session.add(new_user)
            db.session.commit()
        except:
            db.session.rollback()
            flash('Registration failed, need unique username')
            return redirect('/register') 

        session["user_id"] = new_user.id      
        flash('Account Created!')

        return redirect('/tweets')

    else:     
        return render_template('register.html', form=form)
     
    
@app.route('/login', methods=["GET", "POST"])
def login():
    """Logs in a user"""    

    form = UserForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        logged_user = User.authenticate(username, password)
        if logged_user:
            session['user_id'] = logged_user.id
            flash(f'Welcome back {logged_user.username}')
            return redirect('/tweets')
        else:
            form.username.errors = ['Invalid username/password']   

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    """Logs out a user"""

    # Better to have logout be a form that submits a POST request to this route.

    # Will get error if try this route while not logged in
    session.pop('user_id')
    flash('Goodbye')
    return redirect('/')


@app.route('/tweets', methods=["GET", "POST"])
def show_tweets():
    """Displays tweets"""
    
    if "user_id" not in session:
        flash('Not logged in')
        return redirect('/') 
 
    form = TweetForm()

    tweets = Tweet.query.all()

    if form.validate_on_submit():
        text = form.text.data
        user = session.get('user_id')

        new_tweet = Tweet(text=text, user_id=user)
        db.session.add(new_tweet)
        db.session.commit()
        flash('Tweet Created!')
        return redirect('/tweets')


    return render_template('tweets.html', form=form, tweets=tweets) 

@app.route('/tweets/<int:tweet_id>', methods=["POST"])    
def delete_tweet(tweet_id):
    """Deletes a tweet"""
    
    tweet = Tweet.query.get_or_404(tweet_id)
    
    if tweet.user_id == session['user_id']:
        db.session.delete(tweet)
        db.session.commit()
        flash('tweet deleted')
        return redirect('/tweets')

    else:
        flash('Must be logged in and can only delete own tweets')
        return redirect('/tweets')    

    
   













# @app.route('/tweets', methods=['GET', 'POST'])
# def show_tweets():
#     if "user_id" not in session:
#         flash("Please login first!", "danger")
#         return redirect('/')
#     form = TweetForm()
#     all_tweets = Tweet.query.all()
#     if form.validate_on_submit():
#         text = form.text.data
#         new_tweet = Tweet(text=text, user_id=session['user_id'])
#         db.session.add(new_tweet)
#         db.session.commit()
#         flash('Tweet Created!', 'success')
#         return redirect('/tweets')

#     return render_template("tweets.html", form=form, tweets=all_tweets)


# @app.route('/tweets/<int:id>', methods=["POST"])
# def delete_tweet(id):
#     """Delete tweet"""
#     if 'user_id' not in session:
#         flash("Please login first!", "danger")
#         return redirect('/login')
#     tweet = Tweet.query.get_or_404(id)
#     if tweet.user_id == session['user_id']:
#         db.session.delete(tweet)
#         db.session.commit()
#         flash("Tweet deleted!", "info")
#         return redirect('/tweets')
#     flash("You don't have permission to do that!", "danger")
#     return redirect('/tweets')


# @app.route('/register', methods=['GET', 'POST'])
# def register_user():
#     form = UserForm()
#     if form.validate_on_submit():
#         username = form.username.data
#         password = form.password.data
#         new_user = User.register(username, password)

#         db.session.add(new_user)
#         try:
#             db.session.commit()
#         except IntegrityError:
#             form.username.errors.append('Username taken.  Please pick another')
#             return render_template('register.html', form=form)
#         session['user_id'] = new_user.id
#         flash('Welcome! Successfully Created Your Account!', "success")
#         return redirect('/tweets')

#     return render_template('register.html', form=form)


# @app.route('/login', methods=['GET', 'POST'])
# def login_user():
#     form = UserForm()
#     if form.validate_on_submit():
#         username = form.username.data
#         password = form.password.data

#         user = User.authenticate(username, password)
#         if user:
#             flash(f"Welcome Back, {user.username}!", "primary")
#             session['user_id'] = user.id
#             return redirect('/tweets')
#         else:
#             form.username.errors = ['Invalid username/password.']

#     return render_template('login.html', form=form)


# @app.route('/logout')
# def logout_user():
#     session.pop('user_id')
#     flash("Goodbye!", "info")
#     return redirect('/')
