from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    # reviews = db.relationship('CourseReview', backref='student', lazy=True)


class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    # reviews = db.relationship('CourseReview', backref='teacher', lazy=True)


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))  # 增加外键关联到Teacher表
    teacher = db.relationship('Teacher', backref=db.backref('courses', lazy=True))
    # reviews = db.relationship('CourseReview', backref='course', lazy=True)


class CourseRegistration(db.Model):
    __tablename__ = 'course_registration'
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), primary_key=True)


class CourseComments(db.Model):
    __tablename__ = 'course_comments'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    sentiment = db.relationship('ReviewSentiment', back_populates='comment', uselist=False)


class ReviewSentiment(db.Model):
    __tablename__ = 'review_sentiment'
    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('course_comments.id'), nullable=False)
    negative_probability = db.Column(db.Float)
    neutral_probability = db.Column(db.Float)
    positive_probability = db.Column(db.Float)

    comment = db.relationship('CourseComments', back_populates='sentiment')
