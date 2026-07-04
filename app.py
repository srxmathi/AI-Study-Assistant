
import PyPDF2
import os
from gemini_helper import generate_summary, ask_question
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session

from flask import Flask, render_template, request, redirect, session
from database import db, User

app = Flask(__name__)
app.secret_key = "my_super_secret_key_123"
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ---------------- DATABASE CONFIG ----------------
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///studyassistant.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()


# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("index.html")


# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password)

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return render_template(
                "register.html",
                message="User already exists! Please login."
            )

        # Create new user
        new_user = User(
            name=name,
            email=email,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect("/login")

    return render_template("register.html")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        # Find user by email
        user = User.query.filter_by(email=email).first()

        if user:

            if check_password_hash(user.password, password):
                session["user"] = user.name

                return redirect("/dashboard")
                
        
            

            else:
                return render_template(
                    "login.html",
                    message=" Incorrect password!"
                )

        else:
            return render_template(
                "login.html",
                message=" User not found!"
            )

    return render_template("login.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    return render_template(
        "dashboard.html",
        name=session["user"]
    )

@app.route("/upload", methods=["GET", "POST"])
def upload():

    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":

        file = request.files["file"]

        if file and file.filename != "":

            filename = secure_filename(file.filename)

            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

            file.save(filepath)

            # Read PDF
            text = ""

            with open(filepath, "rb") as pdf_file:

                reader = PyPDF2.PdfReader(pdf_file)

                for page in reader.pages:
                    extracted = page.extract_text()

                    if extracted:
                        text += extracted

            # Save the extracted text into a .txt file
            text_filename = filename.rsplit(".", 1)[0] + ".txt"
            text_filepath = os.path.join(app.config["UPLOAD_FOLDER"], text_filename)

            with open(text_filepath, "w", encoding="utf-8") as f:
                f.write(text)

            # Save only the text file name in the session
            session["text_file"] = text_filename

            

            summary = generate_summary(text)

            return render_template(
                "summary.html",
                filename=filename,
                summary=summary
            )

    return render_template("upload.html")

@app.route("/chat", methods=["GET", "POST"])
def chat():

    if "user" not in session:
        return redirect("/login")

    answer = ""

    if request.method == "POST":

        print("Session contents:", session)
        print("Text file:", session.get("text_file"))

        question = request.form["question"]

        text_file = session.get("text_file")

        if text_file:

            text_path = os.path.join(app.config["UPLOAD_FOLDER"], text_file)

            with open(text_path, "r", encoding="utf-8") as f:
                pdf_text = f.read()

            answer = ask_question(pdf_text, question)

        else:
            answer = "Please upload a PDF first."

    return render_template("chat.html", answer=answer)            
            
    
                
                
            

    


@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect("/")

# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)