from flask import jsonify, render_template, request, redirect, url_for, flash
from models import User, Token, Notes, Note_History
from flask_login import login_user, logout_user, current_user, login_required
from datetime import datetime, timezone, timedelta
from helper import create_token, send_email, utc_now_naive, is_valid_email, create_security_logs, validate_token
from log_variables import SecurityAction, TokenAction, TokenError, NoteAction
from sqlalchemy import desc, or_

def register_routes(app, db, bcrypt):

    @app.after_request
    def after_request(response):
        """Ensure responses aren't cached"""
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

    @app.route('/')
    @login_required
    def index():          
        return render_template('index.html')
    

    # ======================
    # ACCOUNT OPERATIONS
    # ======================
    
    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'GET':
            return render_template('signup.html')
        elif request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm = request.form.get('password-confirm') 

            if User.query.filter(or_(User.username == username, User.email == email)).first():
                flash('This username is already exist!')
                return redirect(url_for('signup'))

            if not password == confirm:
                flash("Password Doesn't Match")
                return redirect(url_for('signup'))
            
            if not is_valid_email(email):
                flash("Invalid email format")
                return redirect(url_for('signup'))
        
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            user = User(username=username, password_hash=hashed_password, email=email)

            db.session.add(user)
            db.session.commit()

            create_security_logs(user, SecurityAction.ACCOUNT_CREATED)
            token = create_token(user, TokenAction.EMAIL_VERIFICATION)
            verify_url = url_for('verify_mail', token=token, _external=True)
            send_email(user.email, "Verify your email", f"Click here to verify: {verify_url}")
            create_security_logs(user, SecurityAction.EMAIL_VERIFICATION_SENT)


            return redirect(url_for('verify_notice'))
        

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'GET':
            if current_user.is_authenticated:
                return redirect(url_for('index'))
            return render_template('login.html')
        elif request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')

            user = User.query.filter(User.username == username).first()

            if not user:
                flash("Invalid Username or Password")
                return redirect(url_for('login'))

            if bcrypt.check_password_hash(user.password_hash, password):
                
                if not user.email_verified:         
                    record = Token.query.filter(Token.user_id == user.user_id, Token.type == TokenAction.EMAIL_VERIFICATION.value).first()
                    if record:
                        if  record.expire < utc_now_naive():
                            #Token expired!
                            flash("Verification code has been expired.")
                            token = create_token(user, TokenAction.ACCOUNT_DELETION, True)
                            return redirect(url_for('delete', token=token))  # Just for the testing, in product environment background check must be set
                        else:
                            remaining = record.expire - utc_now_naive()
                            minutes = int(remaining.total_seconds() // 60)
                            seconds = int(remaining.total_seconds() % 60)
                            flash(f"Please verify your email in {minutes} minutes and {seconds} seconds.")
                    else:
                        flash("E-mail is not verified in specified time, account deleted!")
                        token = create_token(user, TokenAction.ACCOUNT_DELETION, True)
                        return redirect(url_for('delete', token=token))  # Just for the testing, in product environment background check must be set

                create_security_logs(user, SecurityAction.LOGIN_SUCCESS)
                login_user(user)
                return redirect(url_for('index'))
            else:
                flash("Invalid Username or Password")
                create_security_logs(user, SecurityAction.LOGIN_FAILED)
                return redirect(url_for('login'))
            
    @app.route('/logout')
    @login_required
    def logout():
        create_security_logs(current_user, SecurityAction.USER_LOGOUT)
        logout_user()
        return redirect(url_for('index'))
    
    @app.route('/delete_confirm')
    @login_required
    def delete_confirm():
        return render_template('delete_confirm.html')

    @app.route('/delete')
    def redirect_delete():
        create_security_logs(current_user, SecurityAction.USER_ATTEMPT_DELETE_ACCOUNT)
        token = create_token(current_user, TokenAction.ACCOUNT_DELETION, True)
        return redirect(url_for('delete', token=token))  # Just for the testing, in product environment background check must be set

    @app.route('/delete/<token>')
    def delete(token):


        
        record, error = validate_token(token,TokenAction.ACCOUNT_DELETION)

        if error:
            flash(error)
            return redirect(url_for('login'))
        
        user = record.user

        db.session.delete(user)
        db.session.commit()
        create_security_logs(user, SecurityAction.ACCOUNT_DELETED)
        #flash("User has been deleted due to expired verification.")
        return redirect(url_for("signup"))
    
    # ======================
    # ACCOUNT RECOVERY
    # ======================

    @app.route('/recover')
    def account_recovery():
        return render_template('recovery.html')

    @app.route('/send-recovery', methods=['GET','POST'])
    def send_recovery():

        if request.method == 'POST':
            username = request.form.get('username')

            user = User.query.filter(or_(User.username == username, User.email == username)).first()

            if not user:
                flash("Invalid Username or E-mail")
                return redirect(url_for('login'))
            
            create_security_logs(user, SecurityAction.USER_ATTEMPT_RECOVER_ACCOUNT)

            token = create_token(user, TokenAction.ACCOUNT_RECOVERY)

            recover_url = url_for('recover_account', token=token, _external=True)

            send_email(user.email, "Recover your account with", f"Click here to recover: {recover_url}")

            create_security_logs(user, SecurityAction.ACCOUNT_RECOVERY_MAIL_SENT)

            flash("Recovery Mail Has Been Sent!")
            return redirect(url_for('login'))

        else:
            flash('Unexpected Error')
            return redirect(url_for('login'))

    @app.route('/recover/<token>')
    def recover_account(token):


        record, error = validate_token(token,TokenAction.ACCOUNT_RECOVERY)

        if error:
            flash(error)
            return redirect(url_for('login'))

        
     

        return render_template('recover.html', auth=record.token)
    
    @app.route('/change', methods=['POST'])
    def change_password():

        token = request.form.get('auth')
        password = request.form.get('password')
        confirm = request.form.get('password-confirm')

 

        record, error = validate_token(token,TokenAction.ACCOUNT_RECOVERY)

        if error:
            flash(error)
            return redirect(url_for('login'))

       
        
        if not password == confirm:
            flash("Passwords do not match")
            return redirect(request.referrer)

        user = record.user
        if not user:
            flash("User not found")
            return redirect(url_for('login'))

        user.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        db.session.delete(record)
        db.session.commit()
        create_security_logs(user, SecurityAction.PASSWORD_CHANGED)
        flash("Password has been changed successfully!")
        return redirect(url_for('login'))


    # ======================
    # ACCOUNT VERIFY
    # ======================

    @app.route('/verify')
    def verify_notice():
        return "Verification e-mail has been sent, please verify your email in an hour! Otherwise your account will be deleted!"
   

    @app.route('/verify/<token>')
    def verify_mail(token):

        record, error = validate_token(token,TokenAction.EMAIL_VERIFICATION)
        
        
        if error == TokenError.TOKEN_EXPIRED.value:
            flash(error)
            user = record.user
            token = create_token(user, TokenAction.ACCOUNT_DELETION, True)
            return redirect(url_for('delete', token=token))
        elif error:
            flash(error)
            return redirect(url_for('login'))

       
        #Successful Verification

        user = record.user
        user.email_verified = True
        db.session.delete(record)
        db.session.commit()
        create_security_logs(user, SecurityAction.EMAIL_VERIFIED)
        flash("E-mail has successfuly verified!")
        return redirect(url_for('login'))
    

    # ======================
    # TODO: CRUD OPERATIONS
    # ======================

    @app.route('/todo-page')
    @login_required
    def todo_page():

        notes = Notes.query.filter(Notes.owner == current_user).all()
        return render_template('todo_page.html', notes=notes)
    
    @app.route('/todo-create', methods=['POST'])
    @login_required
    def todo_create():

        if request.method == 'POST':
            title = request.form.get('title')
            content = request.form.get('content')
            tags = request.form.get('tags')

            new_note = Notes(owner_id = current_user.user_id, title=title, content=content, tags=tags)
            db.session.add(new_note)
            db.session.commit()
            new_action = Note_History(note_id = new_note.id, user_id = current_user.user_id ,title=title, action=NoteAction.NOTE_CREATED.value)
            db.session.add(new_action)
            db.session.commit()

            flash("Note Added Successfully!")
            
        else:
            flash("Unexpected Error!")
        return redirect(url_for('todo_page'))
        
    @app.route('/todo-delete/<note_id>', methods=['POST'])
    @login_required
    def todo_delete(note_id):
        
        if request.method == 'POST':
            note = Notes.query.get(note_id)
            
            if not note or note.owner != current_user:
                flash("Note not found or unauthorized!")
                return redirect(url_for('todo_page'))

            db.session.delete(note)
            db.session.commit()
            new_action = Note_History(note_id = note.id, title=note.title, action=NoteAction.NOTE_DELETED.value)
            db.session.add(new_action)
            db.session.commit()

            flash("Note deleted successfully!!")
            return '', 200
        
        else:
            flash("Unexpected Error!")

        return redirect(url_for('todo_page'))

    @app.route('/todo-update/<note_id>', methods=['POST'])
    @login_required
    def todo_update(note_id):

        if request.method == 'POST':
            note = Notes.query.get(note_id)
            
            if not note or note.owner != current_user:
                flash("Note not found or unauthorized!")
                return redirect(url_for('todo_page'))

            data = request.get_json()
            
            original_values = {
            'title': note.title,
            'content': note.content,
            'tags': note.tags,
            'done': note.done
             }
            

            note.title = data.get('title', note.title)  #data['title'] 
            note.content = data.get('content', note.content) #data['content'] 
            note.tags = data.get('tags', note.tags) #data['tags'] 
            note.done = data.get('done', note.done) #data['done']
            note.updated_at = utc_now_naive()

            fields_to_check = ['title', 'content', 'tags', 'done']
            changes = []
            for key in fields_to_check:
                original_value = original_values[key]
                new_value = getattr(note, key)

                if original_value != new_value:
                    if key == 'done':
                        original_value = 'DONE' if original_value else 'IN PROGRESS'
                        new_value = 'DONE' if new_value else 'IN PROGRESS'
                        action = f"{key.capitalize()} is changed from {original_value}>> to {new_value}"
                    elif key == 'content' and len(str(original_value)) > 10:
                        action = f"{key.capitalize()} area has been updated!"
                    else:
                        action = f"{key.capitalize()} is changed from {original_value}>> to {new_value}"
                    
                    changes.append(action)

            if changes:
                action_log = " | ".join(changes)
                new_action = Note_History(note_id = note.id,user_id = current_user.user_id ,title=note.title, action=action_log)
                db.session.add(new_action)

            db.session.commit()
            

            return jsonify({'message': 'Note status updated successfully'}), 200
        
        else:
            flash("Unexpected Error!")

        return redirect(url_for('todo_page'))
    

    @app.route('/todo-history')
    @login_required
    def todo_history():
        note_history = Note_History.query.filter(Note_History.user_id == current_user.user_id).order_by(Note_History.created_at.desc()).all()
        return render_template('todo_history.html', notes=note_history)
    
    # Gemini help on this part.
    @app.route('/api/todo-history', methods=['GET'])
    @login_required
    def api_todo_history():
       
        filter_value = request.args.get('filter', 'all') 
        sort_value = request.args.get('sort', 'desc')
        
        
        query = Note_History.query.filter(Note_History.user_id == current_user.user_id)
        
     
       
        if filter_value == 'created':
            query = query.filter(Note_History.action.like('%CREATED%'))
        elif filter_value == 'updated':
            query = query.filter(Note_History.action.like('%UPDATED%'))
        elif filter_value == 'deleted':
            query = query.filter(Note_History.action.like('%DELETED%'))
            
       
        elif filter_value == 'today':
          
            start_of_day = datetime.combine(utc_now_naive().date(), datetime.min.time())
            query = query.filter(Note_History.created_at >= start_of_day)
        elif filter_value == 'week':
            
            one_week_ago = utc_now_naive() - timedelta(days=7)
            query = query.filter(Note_History.created_at >= one_week_ago)
        elif filter_value == 'month':
           
            one_month_ago = utc_now_naive() - timedelta(days=30)
            query = query.filter(Note_History.created_at >= one_month_ago)

     
        if sort_value == 'asc':
            
            query = query.order_by(Note_History.created_at.asc())
        else: 
            query = query.order_by(Note_History.created_at.desc())
        
     


        all_history_records = query.all() 

       
        history_data = []
        for record in all_history_records:
            history_data.append({
                'note_id': record.note_id,
                'title': record.title,
                'action': record.action,
              
                'created_at': record.created_at.isoformat() 
            })

        return jsonify(history_data), 200
    
# will be done
    @app.route('/password-change', methods=['GET','POST'])
    def password_change():

        if request.method == 'POST':
            username = request.form.get('username')
            auth = request.form.get('auth')
            password = request.form.get('password')
            confirm = request.form.get('password-confirm')

            if not password == confirm:
                flash("Passwords do not match")
                return redirect(request.referrer)
            if not username == current_user.username:
                flash("Unauthorized Action")
                return redirect(request.referrer)
            
            user = User.query.filter(or_(User.username == username)).first()

            if not user:
                flash("Invalid Username")
                return redirect(request.referrer)
            
            create_security_logs(user, SecurityAction.USER_ATTEMPT_PASSWORD_CHANGE)

            token = create_token(user, TokenAction.PASSWORD_CHANGE)
            record, error = validate_token(token,TokenAction.PASSWORD_CHANGE)

            if error:
                flash(error)
                return redirect(request.referrer)

            user.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            db.session.delete(record)
            db.session.commit()
            create_security_logs(user, SecurityAction.PASSWORD_CHANGED)
            flash("Password has been changed successfully!")
            return redirect(request.referrer)

        else:
            flash('Unexpected Error')
            return redirect(request.referrer)
        
        
