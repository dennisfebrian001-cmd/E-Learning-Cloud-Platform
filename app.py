from flask import (
    Flask,
    render_template,
    request,
    redirect,
    send_from_directory,
    url_for
)

import pymysql
import boto3
import json
import os
app = Flask(__name__)

SECRET_NAME = "project/rds/mysql-v2"

client = boto3.client(
    "secretsmanager",
    region_name="ap-southeast-1"
)

def get_db_secret():

    response = client.get_secret_value(
        SecretId=SECRET_NAME
    )

    return json.loads(
        response["SecretString"]
    )

def get_connection():

    secret = get_db_secret()

    return pymysql.connect(
        host=secret["host"],
        user=secret["username"],
        password=secret["password"],
        database=secret["dbname"],
        port=secret["port"]
    )

UPLOAD_FOLDER = "uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/student")
def student():

    return render_template(
        "student_dashboard.html"
    )

@app.route("/lecturer")
def lecturer():

    return render_template(
        "lecturer_dashboard.html"
    )

@app.route("/courses")
def courses():

    return render_template(
        "courses.html"
    )

@app.route("/upload-material", methods=["GET","POST"])
def upload_material():

    if request.method == "POST":

        title = request.form["title"]
        file = request.files["file"]

        bucket_name = "dennisfebrian-project-bucket-2026"

        s3 = boto3.client("s3")

        s3.upload_fileobj(
            file,
            bucket_name,
            file.filename
        )

        file_url = (
            f"https://{bucket_name}.s3.ap-southeast-1.amazonaws.com/"
            f"{file.filename}"
        )

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO materials
            (course_id,title,file_url)
            VALUES(%s,%s,%s)
            """,
            (1, title, file_url)
        )

        conn.commit()
        conn.close()

        return redirect("/lecturer")

    return render_template(
        "upload_material.html"
    )

@app.route("/upload-video",
methods=["GET","POST"])
def upload_video():

    if request.method == "POST":

        title = request.form["title"]

        youtube_url = request.form["youtube"]

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO videos
            (course_id,title,video_url)
            VALUES(%s,%s,%s)
            """,
            (1, title, youtube_url)
        )

        conn.commit()

        conn.close()

        return redirect("/lecturer")

    return render_template(
        "upload_video.html"
    )

@app.route("/videos")
def videos():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM videos"
    )

    data = cursor.fetchall()

    conn.close()

    return render_template(
        "videos.html",
        videos=data
    )

@app.route("/create-assignment",
methods=["GET","POST"])
def create_assignment():

    if request.method=="POST":

        title = request.form["title"]

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO assignments
            (course_id,title)
            VALUES(%s,%s)
            """,
            (1, title)
        )

        conn.commit()

        conn.close()

        return redirect("/lecturer")

    return render_template(
        "create_assignment.html"
    )

@app.route("/submit-assignment",
methods=["GET","POST"])
def submit_assignment():

    if request.method=="POST":

        student = request.form["student"]

        file = request.files["file"]

        bucket_name = "dennisfebrian-project-bucket-2026"

        s3 = boto3.client("s3")

        s3.upload_fileobj(
            file,
            bucket_name,
            file.filename
        )

        file_url = (
            f"https://{bucket_name}.s3.ap-southeast-1.amazonaws.com/"
            f"{file.filename}"
        )

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO submissions
            (assignment_id,student_name,file_url)
            VALUES(%s,%s,%s)
            """,
            (1, student, file_url)
        )

        conn.commit()
        conn.close()

        return redirect("/student")

        conn.commit()

        conn.close()

        return redirect("/student")

    return render_template(
        "submit_assignment.html"
    )

@app.route("/materials")
def materials():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM materials"
    )

    data = cursor.fetchall()

    conn.close()

    return render_template(
        "materials.html",
        materials=data
    )

@app.route("/assignments")
def assignments():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM assignments"
    )

    data = cursor.fetchall()

    conn.close()

    return render_template(
        "assignments.html",
        assignments=data
    )

@app.route("/submissions")
def submissions():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM submissions"
    )

    data = cursor.fetchall()

    conn.close()

    return render_template(
        "submissions.html",
        submissions=data
    )

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )

