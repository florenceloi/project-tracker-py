"""Hackbright Project Tracker.

A front-end for a database that allows users to work with students, class
projects, and the grades students receive in class projects.
"""
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def connect_to_db(app):
    """Connect the database to our Flask app."""

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///hackbright'
    db.app = app
    db.init_app(app)


def get_student_by_github(github):
    """Given a github account name, print information about the matching student."""

    QUERY = """
        SELECT first_name, last_name, github
        FROM Students
        WHERE github = :github
        """
    db_cursor = db.session.execute(QUERY, {'github': github})
    row = db_cursor.fetchone()
    print "Student: %s %s\nGithub account: %s" % (row[0], row[1], row[2])


def make_new_student(first_name, last_name, github):
    """Add a new student and print confirmation.

    Given a first name, last name, and GitHub account, add student to the
    database and print a confirmation message.
    """
    
    QUERY = """INSERT INTO Students VALUES (:first_name, :last_name, :github)"""
    db_cursor = db.session.execute(QUERY, {'first_name': first_name,
                                            'last_name': last_name,
                                            'github': github})
    db.session.commit()

    print "Successfully added student: %s %s" % (first_name, last_name)


def get_project_by_title(title):
    """Given a project title, print information about the project."""
    
    QUERY = """SELECT title, description FROM Projects WHERE title = :title"""
    db_cursor = db.session.execute(QUERY, {'title': title})

    row = db_cursor.fetchone()
    print "Title: %s \n Description: %s" % (row[0], row[1])


def get_grade_by_github_title(github, title):
    """Print grade student received for a project."""
    
    QUERY = """SELECT grade FROM grades WHERE (student_github = :github) AND (project_title = :title)"""
    db_cursor = db.session.execute(QUERY, {'github': github, 'title': title})

    row = db_cursor.fetchone()
    print "Grade: %s" % (row[0])


def assign_grade(github, title, grade):
    """Assign a student a grade on an assignment and print a confirmation."""
    
    QUERY = """UPDATE grades SET grade = :grade WHERE (student_github = :github) AND (project_title = :title)"""
    db_cursor = db.session.execute(QUERY, {'github': github, 'title': title, 'grade': grade})
    db.session.commit()

    print "Success! %s is now assigned grade %s for project %s" % (github, grade, title)


def add_project(title, description, max_grade):
    """Add new project with description and max grade to table Projects"""

    QUERY = """INSERT INTO Projects (title, description, max_grade) VALUES (:title, :description, :max_grade)"""
    db_cursor = db.session.execute(QUERY, {'title': title, 'description': description, 'max_grade': max_grade})
    db.session.commit()

    print "New project %s successfully added! \nDescription: %s \nMax grade: %s" % (title, description, max_grade)


def print_grades(first_name, last_name):
    """For student, print out all projects and grades"""

    QUERY = """SELECT project_title, grade FROM grades JOIN students ON (students.github = grades.student_github) WHERE students.first_name = :first_name AND students.last_name = :last_name"""
    db_cursor = db.session.execute(QUERY, {'first_name': first_name, 'last_name': last_name})

    row = db_cursor.fetchall()
    if not row:
        print "No record found."
    for line in row:
        print "%s: %s" % (line[0], line[1])


def handle_input():
    """Main loop.

    Repeatedly prompt for commands, performing them, until 'quit' is received as a
    command."""

    command = None

    while command != "quit":
        input_string = raw_input("HBA Database> ")
        tokens = input_string.split()
        command = tokens[0]
        args = tokens[1:]

        if command == "student":
            github = args[0]
            get_student_by_github(github)

        elif command == "new_student":
            first_name, last_name, github = args   # unpack!
            make_new_student(first_name, last_name, github)

        elif command == "project_description":
            title = args[0] 
            get_project_by_title(title)

        elif command == "project_grade":
            github, title = args 
            get_grade_by_github_title(github, title)

        elif command == "assign_grade":
            github, title, grade = args 
            assign_grade(github, title, grade)

        elif command == "add_project":
            title = args[0]
            description = " ".join(args[1:-1])
            max_grade = args[-1]
            add_project(title, description, max_grade)

        elif command == "print_grades":
            try:
                first_name, last_name = args
                print_grades(first_name, last_name)
            except ValueError:
                print "Try typing a student name again."


        else:
            if command != "quit":
                print "Invalid Entry. Try again."


if __name__ == "__main__":
    app = Flask(__name__)
    connect_to_db(app)

    handle_input()

    db.session.close()
