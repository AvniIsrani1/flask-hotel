from flask import Flask, Blueprint, jsonify, render_template, request, redirect, url_for, session, flash, get_flashed_messages
from .db import db
from .model_dbs import Users, Bookings, YesNo

bp_profile = Blueprint('profile',__name__)

@bp_profile.route("/profile",methods=["GET", "POST"])
def profile():
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("log_in"))
    
    user_db = Users.query.get(session["user_id"])
    if not user_db:
        flash('Account not found','error')
        session.clear()
        return redirect(url_for("log_in"))
    user = user_db.create_user_object()
    if user.first_login:
        flash("Please update your profile information!", "action")
    message = status = ''
    if request.method == "POST":
        ptype = request.form.get('ptype')
        if ptype == 'profile':
            user.update_profile(
                name = request.form.get("name"),
                phone = request.form.get("phone"),
                address_line1 = request.form.get("address"),
                address_line2 = request.form.get("address2"),
                city = request.form.get("city"),
                state = request.form.get("state"),
                zipcode = request.form.get("zipcode")
            )
            message = 'Profile has been updated!'
            status = 'success'
        elif ptype=='notifications':
            tremind = request.form.get('tremind') is not None
            eremind = request.form.get('eremind') is not None
            user.update_notifications(tremind,eremind)
            message = 'Notification preferences have been updated!'
            status = 'success'
        elif ptype=='password_change':
            cur_password = request.form.get("cur_pass")
            if user.verify_password(cur_password):
                new_password = request.form.get("new_pass")
                user.change_password(new_password)
                message = 'Password has been changed.'
                status = 'success'
            else:
                message = 'Unable to update password.'
                status = 'error'
        elif ptype=='account_deletion': #not working right now
            db.session.delete(user_db)
            session.clear()
            db.session.commit()
            return render_template("home.html")
        try:
            result = Users.update_users_db(user)
            print(f'Update result: {result}')
            db.session.commit()
            print('Successful commit')
            flash(message, status)
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}. Please try again later.", "error")
        finally:
            return redirect(url_for("profile.profile"))
    return render_template("profile.html", user=user_db, YesNo = YesNo)
