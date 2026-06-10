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

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM courses")
    total_courses = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM videos")
    total_videos = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM materials")
    total_materials = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM assignments")
    total_assignments = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "index.html",
        total_courses=total_courses,
        total_videos=total_videos,
        total_materials=total_materials,
        total_assignments=total_assignments
    )

@app.route("/student")
def student():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM courses"
    )
    total_courses = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM videos"
    )
    total_videos = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM materials"
    )
    total_materials = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM assignments"
    )
    total_assignments = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "student_dashboard.html",
        total_courses=total_courses,
        total_videos=total_videos,
        total_materials=total_materials,
        total_assignments=total_assignments
    )

@app.route("/lecturer")
def lecturer():

    return render_template(
        "lecturer_dashboard.html"
    )

@app.route("/courses")
def courses():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM courses"
    )

    courses = cursor.fetchall()

    conn.close()

    return render_template(
        "courses.html",
        courses=courses
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

    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]
        deadline = request.form["deadline"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO assignments
            (course_id,title,description,deadline)
            VALUES(%s,%s,%s,%s)
            """,
            (1, title, description, deadline)
        )

        conn.commit()
        conn.close()

        return redirect("/assignments")

    return render_template(
        "create_assignment.html"
    )

@app.route(
    "/submit-assignment/<int:assignment_id>",
    methods=["GET", "POST"]
)
def submit_assignment(assignment_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM assignments
        WHERE id=%s
        """,
        (assignment_id,)
    )

    assignment = cursor.fetchone()

    if request.method == "POST":

        student = request.form["student"]

        file = request.files["file"]

        bucket_name = (
            "dennisfebrian-project-bucket-2026"
        )

        s3 = boto3.client("s3")

        s3.upload_fileobj(
            file,
            bucket_name,
            file.filename
        )

        file_url = (
            f"https://{bucket_name}"
            f".s3.ap-southeast-1.amazonaws.com/"
            f"{file.filename}"
        )

        cursor.execute(
            """
            INSERT INTO submissions
            (
                assignment_id,
                student_name,
                file_url
            )
            VALUES(%s,%s,%s)
            """,
            (
                assignment_id,
                student,
                file_url
            )
        )

        conn.commit()
        conn.close()

        return redirect("/student")

    conn.close()

    return render_template(
        "submit_assignment.html",
        assignment=assignment
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

    assignments = cursor.fetchall()

    conn.close()

    return render_template(
        "assignments.html",
        assignments=assignments
    )

@app.route("/submissions")
def submissions():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            submissions.id,
            assignments.title,
            submissions.student_name,
            submissions.file_url
        FROM submissions
        JOIN assignments
        ON submissions.assignment_id =
           assignments.id
        """
    )

    submissions = cursor.fetchall()

    conn.close()

    return render_template(
        "submissions.html",
        submissions=submissions
    )

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )

