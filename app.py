import os
import secrets
from datetime import datetime, time
from flask import Flask, render_template, url_for, request, redirect, session, flash, current_app, \
    render_template_string, jsonify, send_from_directory
from models import db, User, Project, Participant, Document, Appointment, Note, Group
from werkzeug.security import generate_password_hash, check_password_hash
from utils import doc_table
import csv

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.sqlite"
db.init_app(app)


@app.route('/')
def index():
    db.create_all()
    try:
        if session["is_logged_in"] == True:
            email = session["email"]
            user = User.query.filter_by(email=email).first()
            p = Project.query.filter_by(user=user)
            return render_template("project.html", projects=p, page_title='Projects', user=user)

        else:
            return render_template("index.html")
    except:
        session["is_logged_in"] = False
        email = session["email"] = None
        return render_template("index.html")


@app.route('/add_project', methods=["POST", "GET"])
def add_project():
    user = User.query.filter_by(email=session['email']).first()
    new_values = request.form.to_dict()
    project = Project.get_or_create(name=new_values['name'], user_id=user.id)
    if new_values['start_date']:
        start_date = datetime.strptime(new_values['start_date'], '%Y-%m-%d').date()
        project.start_date = start_date

    if new_values['end_date']:
        end_date = datetime.strptime(new_values['end_date'], '%Y-%m-%d').date()
        project.end_date = end_date
    db.session.commit()

    return redirect(url_for("index"))


@app.route('/add_notes', methods=["POST", "GET"])
def add_notes():
    admin = request.args.get('admin')
    participant = Participant.query.filter_by(id=request.form.get('pid')).first()
    note = Note.get_or_create(content=request.form.get('notes'), participant=participant)
    print(note)
    if admin:
        return redirect(url_for('participants'))
    return redirect(f'/project_participants/{participant.project.id}')


@app.route('/add_group', methods=["POST", "GET"])
def add_group():
    email = session["email"]
    user = User.query.filter_by(email=email).first()
    gr = Group.get_or_create(name=request.form.get('name'), user=user)
    return redirect(url_for('groups'))


@app.route('/edit_notes', methods=["POST", "GET"])
def edit_notes():
    admin = request.args.get('admin')
    note = Note.query.get(request.form.get('id'))
    note.content = request.form.get('notes')
    db.session.commit()
    if admin:
        return redirect(url_for('participants'))
    return redirect(f'/notes/{note.participant.id}')


@app.route('/notes/<pid>', methods=["POST", "GET"])
def notes(pid):
    if session["is_logged_in"] == True:
        email = session["email"]
        user = User.query.filter_by(email=email).first()
        participant = Participant.query.filter_by(id=pid).first()
        notes = Note.query.filter_by(participant=participant)
        print(notes, participant)
        return render_template("notes.html", notes=notes, page_title='Notes', participant=participant, user=user)

    else:
        return render_template("index.html")


@app.route('/groups', methods=["POST", "GET"])
def groups():
    if session["is_logged_in"] == True:
        email = session["email"]
        user = User.query.filter_by(email=email).first()
        groups = Group.query.filter_by(user=user)

        return render_template("groups.html", groups=groups, page_title='Groups', user=user)

    else:
        return render_template("index.html")


@app.route("/delete_note/<id>/<pid>/", methods=["POST", "GET"])
def delete_note(id, pid):
    p = Note.query.filter_by(id=id).first()
    db.session.delete(p)
    db.session.commit()
    return redirect(f'/notes/{pid}')


@app.route("/delete_group/<id>/", methods=["POST", "GET"])
def delete_group(id):
    p = Group.query.filter_by(id=id).first()
    db.session.delete(p)
    db.session.commit()
    return redirect(f'/groups')


@app.route('/edit_project', methods=["POST", "GET"])
def edit_project():
    if request.method == "POST":
        pid = request.form['id']
        project = Project.query.get(pid)
        project.name = request.form['name']

        if request.form['start_date']:
            start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
            project.start_date = start_date

        if request.form['end_date']:
            end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
            project.end_date = end_date
        db.session.commit()
        return redirect(url_for('index'))


@app.route("/delete_project/<id>", methods=["POST", "GET"])
def delete_project(id):
    project = Project.query.filter_by(id=id).first()
    db.session.delete(project)
    db.session.commit()
    message = "project Deleted"
    return redirect(url_for("index"))


@app.route("/project_participants/<pid>", methods=["POST", "GET"])
def project_participants(pid):
    if session["is_logged_in"] == True:
        email = session["email"]
        user = User.query.filter_by(email=email).first()
        project = Project.query.filter_by(id=pid).first()
        participants = Participant.query.filter_by(project=project)
        groups = Group.query.filter_by(user=user)
        return render_template("participants.html", participants=participants, project=project,
                               page_title='Participants', user=user, groups=groups)

    return redirect(url_for("index"))


@app.route("/group_participants/<id>", methods=["POST", "GET"])
def group_participants(id):
    if session["is_logged_in"] == True:
        email = session["email"]
        user = User.query.filter_by(email=email).first()
        group = Group.query.get(id)
        participants = group.participants
        return render_template("group_participants.html", participants=participants,
                               page_title=' Group Participants', user=user)

    return redirect(url_for("index"))


@app.route('/add_participant_to_group', methods=['POST'])
def add_participant_to_group():
    group_id = request.form.get('group_id')
    participant_id = request.form.get('pid')
    group = Group.query.get(group_id)
    participant = Participant.query.get(participant_id)
    if group and participant:
        group.participants.append(participant)
        db.session.commit()
        return redirect(f'/project_participants/{participant.project.id}')
    else:
        return 'Invalid group or participant ID.'


@app.route("/participants", methods=["POST", "GET"])
def participants():
    if session["is_logged_in"] == True:
        email = session["email"]
        user = User.query.filter_by(email=email).first()
        projects = Project.query.filter_by(user=user)
        participants = Participant.query.join(Participant.project).filter(Project.user == user).all()
        groups = Group.query.filter_by(user=user)
        return render_template("all_participants.html", participants=participants,
                               page_title='Participants', user=user, projects=projects, groups=groups)

    return redirect(url_for("index"))


@app.route("/add_participant", methods=["POST", "GET"])
def add_participant():
    admin = request.args.get("admin")
    if request.method == "POST":
        file_path = os.path.join(current_app.root_path, 'static')
        Docs = file_path + "/Docs/"
        try:
            os.makedirs(f'{Docs}')
        except:
            print("Dir allready exsits")
        project_id = request.form['pid']
        project = Project.query.filter_by(id=project_id).first()
        print(request.form['participant_id'])

        participant = Participant.get_or_create(
            pid=request.form['participant_id'],
            name=request.form['name'],
            phone=request.form['phone'],
            email=request.form['email'],
            address=request.form['address'],
            nk_name=request.form['nk_name'],
            nk_phone=request.form['nk_phone'],
            nk_email=request.form['nk_email'],
            nk_address=request.form['nk_address'],
            project=project
        )
        files = request.files.getlist("document")
        if len(files) > 0:
            for file in files:
                if file.filename != '':
                    doc_id = secrets.token_hex(3) + "-" + secrets.token_hex(3) + "-" + secrets.token_hex(3)
                    _, f_ext = os.path.splitext(file.filename)
                    file_name = _ + '&&' + doc_id + f_ext
                    file_path = os.path.join(current_app.root_path, f'static/Docs/',
                                             file.filename)
                    doc = Document.get_or_create(participant=participant, file_path=file_path, file_name=file.filename)
                    file.save(file_path)
        if admin is None:
            return redirect(f'/project_participants/{project_id}')
        else:
            return redirect(url_for('participants'))


@app.route("/edit_participant", methods=["POST", "GET"])
def edit_participant():
    if request.method == "POST":
        participant_id = request.form['id']
        participant = Participant.query.get(participant_id)
        name = request.form.get('name1'),
        phone = request.form['phone'],
        email = request.form['email'],
        pid = request.form.get('participant_id'),
        address = request.form['address'],
        nk_name = request.form['nk_name'],
        nk_phone = request.form['nk_phone'],
        nk_email = request.form['nk_email'],
        nk_address = request.form['nk_address'],

        participant.name = name[0]
        participant.address = address[0]
        participant.phone = phone[0]
        participant.email = email[0]

        participant.nk_name = nk_name[0]
        participant.nk_address = nk_address[0]
        participant.nk_phone = nk_phone[0]
        participant.nk_email = nk_email[0]
        participant.pid = pid[0]

        files = request.files.getlist("document")
        if len(files) > 0:
            for file in files:
                if file.filename != '':
                    doc_id = secrets.token_hex(3) + "-" + secrets.token_hex(3) + "-" + secrets.token_hex(3)
                    _, f_ext = os.path.splitext(file.filename)
                    file_name = _ + '&&' + doc_id + f_ext
                    file_path = os.path.join(current_app.root_path, f'static/Docs/',
                                             file.filename)
                    doc = Document.get_or_create(participant=participant, file_path=file_path, file_name=file.filename)
                    file.save(file_path)
        db.session.commit()
        return redirect(f'/project_participants/{participant.project.id}')


@app.route("/edit_participant_", methods=["POST", "GET"])
def edit_participant_():
    if request.method == "POST":
        participant_id = request.form['id']
        participant = Participant.query.get(participant_id)
        name = request.form.get('name1'),
        pid = request.form.get('participant_id'),
        phone = request.form['phone'],
        email = request.form['email'],
        address = request.form['address'],
        nk_name = request.form['nk_name'],
        nk_phone = request.form['nk_phone'],
        nk_email = request.form['nk_email'],
        nk_address = request.form['nk_address'],

        participant.name = name[0]
        participant.address = address[0]
        participant.phone = phone[0]
        participant.email = email[0]

        participant.nk_name = nk_name[0]
        participant.nk_address = nk_address[0]
        participant.nk_phone = nk_phone[0]
        participant.nk_email = nk_email[0]
        participant.pid = pid[0]

        files = request.files.getlist("document")
        if len(files) > 0:
            for file in files:
                if file.filename != '':
                    doc_id = secrets.token_hex(3) + "-" + secrets.token_hex(3) + "-" + secrets.token_hex(3)
                    _, f_ext = os.path.splitext(file.filename)
                    file_name = _ + '&&' + doc_id + f_ext
                    file_path = os.path.join(current_app.root_path, f'static/Docs/',
                                             file.filename)
                    doc = Document.get_or_create(participant=participant, file_path=file_path, file_name=file.filename)
                    file.save(file_path)
        db.session.commit()
        return redirect(url_for('participants'))


@app.route("/delete_participant/<id>/<pid>/", methods=["POST", "GET"])
def delete_participant(id, pid):
    p = Participant.query.filter_by(id=id).first()
    docs = Document.query.filter_by(participant=p).all()
    try:
        for doc in docs:
            db.session.delete(doc)
            db.session.commit()
    except:
        pass

    db.session.delete(p)
    db.session.commit()
    message = "Participant Deleted"
    return redirect(f'/project_participants/{pid}')


@app.route("/delete_participant_/<id>", methods=["POST", "GET"])
def delete_participant_(id):
    p = Participant.query.filter_by(id=id).first()
    docs = Document.query.filter_by(participant=p).all()
    try:
        for doc in docs:
            db.session.delete(doc)
            db.session.commit()
    except:
        pass

    db.session.delete(p)
    db.session.commit()
    message = "Participant Deleted"
    return redirect(url_for("participants"))


@app.route("/participant_documents/<id>/", methods=["POST", "GET"])
def participant_documents(id):
    p = Participant.query.filter_by(id=id).first()
    docs = Document.query.filter_by(participant=p).all()
    document = []
    tem_str = render_template_string(doc_table, docs=docs)
    print(tem_str)
    return jsonify({'table': tem_str})


@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(current_app.root_path, f'static/Docs/')
    return send_from_directory(file_path, filename, as_attachment=True)


# add_participant_appointment

@app.route("/add_participant_appointment", methods=["POST", "GET"])
def add_participant_appointment():
    admin = request.args.get("admin")
    if request.method == "POST":
        checkbox = request.form.get("checkbox")
        date = request.form.get("date")
        time = request.form.get("time")
        participant_id = request.form.get("participant_id")
        next_appointment_date = request.form.get("next_appointment_date", None)
        p = Participant.query.filter_by(id=participant_id).first()
        if checkbox is not None:
            appointment = Appointment.get_or_create(
                participant=p,
                appointment_date=datetime.strptime(date, '%Y-%m-%d').date(),
                appointment_time=datetime.strptime(time, '%H:%M').time(),
                next_appointment_date=datetime.strptime(next_appointment_date, '%Y-%m-%d').date()
            )
        else:
            appointment = Appointment.get_or_create(
                participant=p,
                appointment_date=datetime.strptime(date, '%Y-%m-%d').date(),
                appointment_time=datetime.strptime(time, '%H:%M').time(),

            )
        appointments = Appointment.query.all()
        if admin:
            return redirect(url_for("appointments"))
        return redirect(f'/participant_appointments/{participant_id}')


@app.route("/edit_participant_appointment", methods=["POST", "GET"])
def edit_participant_appointment():
    admin = request.args.get("admin")
    if request.method == "POST":
        checkbox = request.form.get("checkbox")
        date = request.form.get("date")
        time_ = request.form.get("time")
        participant_id = request.form.get("participant_id")
        appointment_id = request.form.get("appointment_id")
        next_appointment_date = request.form.get("next_appointment_date", None)

        print(date, time_, participant_id, appointment_id, next_appointment_date)
        appointment = Appointment.query.get(appointment_id)
        if next_appointment_date is not None:
            appointment_date = datetime.strptime(date, '%Y-%m-%d').date()
            appointment.appointment_date = appointment_date
            try:
                appointment_time = datetime.strptime(time_ + ':00', '%H:%M:%S').time()
            except:
                appointment_time = datetime.strptime(time_, '%H:%M:%S').time()
            appointment.appointment_time = appointment_time

            next_appointment_date = datetime.strptime(next_appointment_date, '%Y-%m-%d').date()
            appointment.next_appointment_date = next_appointment_date
            db.session.commit()
        else:
            appointment.appointment_date = date
            appointment.appointment_time = time
            db.session.commit()
        if admin:
            return redirect(url_for('appointments'))
        return redirect(f'/participant_appointments/{participant_id}')


@app.route("/participant_appointments/<id>", methods=["POST", "GET"])
def participant_appointments(id):
    if session["is_logged_in"] == True:
        email = session["email"]
        user = User.query.filter_by(email=email).first()
        participant = Participant.query.filter_by(id=id).first()
        appointments = Appointment.query.filter_by(participant=participant).order_by(Appointment.appointment_date.asc())
        return render_template("appointments.html", appointments=appointments, participant=participant,
                               page_title='Appointments', user=user)

    return redirect(url_for("index"))


@app.route("/appointments", methods=["POST", "GET"])
def appointments():
    if session["is_logged_in"] == True:
        email = session["email"]
        user = User.query.filter_by(email=email).first()
        projects = Project.query.filter_by(user=user)
        participants = Participant.query.join(Participant.project).filter(Project.user == user).all()
        appointments = []
        for project in user.assigned_projects:
            for participant in project.participants:
                appointments.extend(Appointment.query.filter_by(participant=participant).order_by(Appointment.appointment_date.asc()))
        return render_template("all_appointment.html", appointments=appointments, participants=participants,
                               page_title='Appointments', user=user)

    return redirect(url_for("index"))


@app.route('/signin', methods=["POST", "GET"])
def signin():  # put application's code here
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
        else:
            session["is_logged_in"] = True
            session["username"] = user.username
            session["email"] = user.email
            return redirect(url_for("index"))

    return render_template("sign-in.html")


@app.route("/delete_appointment/<id>/<pid>/", methods=["POST", "GET"])
def delete_appointment(id, pid):
    admin = request.args.get("admin")
    p = Appointment.query.filter_by(id=id).first()
    db.session.delete(p)
    db.session.commit()
    message = "Participant Deleted"
    if admin:
        return redirect(url_for('appointments'))
    return redirect(f'/participant_appointments/{pid}')


@app.route('/signup', methods=["POST", "GET"])
def signup():
    db.create_all()  # put application's code here
    if request.method == 'POST':
        username = request.form['name']
        email = request.form['email']
        password = request.form['password']
        password_2 = request.form['password_2']
        if password == password_2:
            new_user = User.get_or_create(email=email, username=username,
                                          password=generate_password_hash(password, method='sha256'))

            session["is_logged_in"] = False
            session["email"] = email
            session["username"] = username
            flash("User Registered successfully , Login to continue")
            return redirect('/signin')
        else:
            flash('Passwords are not same')
    return render_template("sign-up.html")


@app.route('/import_csv', methods=['GET', 'POST'])
def import_csv():
    if request.method == 'POST':
        file = request.files['file']
        project_id = request.form['pid']
        project = Project.query.filter_by(id=project_id).first()

        if file.filename.endswith('.csv'):
            participants = []
            csv_data = csv.reader(file.stream.read().decode("utf-8-sig").splitlines())
            for row in csv_data:
                if row[0] == '' or row[1] == '' or row[2] == '' or row[3] == '':
                    pass
                else:
                    participant = Participant.get_or_create(
                        name=row[0],
                        address=row[1],
                        phone=row[2],
                        email=row[3],
                        project=project
                    )
                    participants.append(participant)
                db.session.add_all(participants)
                db.session.commit()
        return redirect(f'/project_participants/{project_id}')


@app.route("/logout")
def logout():
    session["username"] = ''
    session["is_logged_in"] = False
    return redirect(url_for('signin'))


if __name__ == '__main__':
    app.run(debug=True)
