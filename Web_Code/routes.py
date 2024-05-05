from flask import request, redirect, url_for, render_template, flash

from TextPreprocessor import TextPreprocessor
from models import db, Teacher, Student, Course, CourseRegistration, CourseComments, ReviewSentiment
from flask import flash
from flask import session
from flask import request, jsonify
from model_loader import get_model
from transformers import AutoTokenizer
import numpy as np
from collections import Counter


def configure_routes(app):
    @app.route('/')
    def index():
        return render_template('login.html')

    @app.route('/login', methods=['POST'])
    def login():
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        if role == "teacher":
            user = Teacher.query.filter_by(username=username).first()
        else:  # 默认为学生
            user = Student.query.filter_by(username=username).first()

        if user and user.password == password:
            session['user_id'] = user.id  # 存储用户的ID在session中
            session['user_name'] = user.name  # 存储用户的名字在session中
            session['role'] = role  # 存储用户的角色在session中

            if role == "teacher":
                return redirect(url_for('teacher_home'))
            else:
                return redirect(url_for('student_home'))
        else:
            flash('Invalid username or password', 'error')
            return redirect(url_for('index'))

    @app.route('/logout')
    def logout():
        # 清除 session 中的所有信息
        session.clear()
        flash('You have been logged out.', 'info')
        return redirect(url_for('index'))

    @app.route('/student/home')
    def student_home():
        student_id = session.get('user_id')  # 假设学生ID已存储在session中
        if student_id:
            # 使用 JOIN 查询获取当前学生的课程列表及对应教师信息
            courses_info = db.session.query(
                Course.id,
                Course.name,
                Course.description,
                Course.image_url,
                Teacher.id.label("teacher_id"),
                Teacher.name.label("teacher_name")
            ).join(CourseRegistration, Course.id == CourseRegistration.course_id) \
                .join(Teacher, CourseRegistration.teacher_id == Teacher.id) \
                .filter(CourseRegistration.student_id == student_id) \
                .all()

            return render_template('student_home.html', courses_info=courses_info)
        else:
            # 适当处理未登录的情况
            return redirect(url_for('login'))

    @app.route('/course/<int:course_id>')
    def course_detail(course_id):
        course = Course.query.get_or_404(course_id)
        # 获取与课程关联的教师信息
        registration_info = CourseRegistration.query.filter_by(course_id=course_id).first()
        teacher = Teacher.query.get(registration_info.teacher_id) if registration_info else None

        # 获取学生的评论以及相关的情感分析结果
        student_id = session.get('user_id')
        review = CourseComments.query.filter_by(course_id=course_id, student_id=student_id).first()
        sentiment_result = None
        if review:
            sentiment = ReviewSentiment.query.filter_by(comment_id=review.id).first()
            if sentiment:
                sentiment_result = {
                    'Negative_probability': sentiment.negative_probability,
                    'Neutral_probability': sentiment.neutral_probability,
                    'Positive_probability': sentiment.positive_probability
                }

        return render_template('course_detail.html', course=course, teacher=teacher, review=review,
                               sentiment=sentiment_result)

    @app.route('/submit_review/<int:course_id>', methods=['POST'])
    def submit_review(course_id):
        if 'user_id' not in session:
            flash('You must be logged in to submit reviews.')
            return redirect(url_for('login'))

        review_text = request.form.get('review_text')
        if review_text:
            existing_comment = CourseComments.query.filter_by(
                course_id=course_id,
                student_id=session['user_id']
            ).first()

            if existing_comment:
                existing_comment.comment = review_text
                db.session.commit()
                comment_id = existing_comment.id
                flash('Your review has been updated successfully.')
            else:
                new_comment = CourseComments(
                    course_id=course_id,
                    student_id=session['user_id'],
                    comment=review_text
                )
                db.session.add(new_comment)
                db.session.commit()
                comment_id = new_comment.id
                flash('Your review has been submitted successfully.')

            # 进行情感分析
            processed_inputs = preprocess(review_text)
            model = get_model()
            prediction = model.predict([processed_inputs['input_ids'], processed_inputs['attention_mask']])
            decoded_prediction = decode_prediction(prediction)

            # 查找或创建情感分析记录
            existing_sentiment = ReviewSentiment.query.filter_by(comment_id=comment_id).first()
            if existing_sentiment:
                existing_sentiment.negative_probability = decoded_prediction['Negative_probability']
                existing_sentiment.neutral_probability = decoded_prediction['Neutral_probability']
                existing_sentiment.positive_probability = decoded_prediction['Positive_probability']
            else:
                new_sentiment = ReviewSentiment(
                    comment_id=comment_id,
                    negative_probability=decoded_prediction['Negative_probability'],
                    neutral_probability=decoded_prediction['Neutral_probability'],
                    positive_probability=decoded_prediction['Positive_probability']
                )
                db.session.add(new_sentiment)

            db.session.commit()

            return redirect(url_for('course_detail', course_id=course_id))
        else:
            flash('Review text is required.')
            return redirect(url_for('course_detail', course_id=course_id))

    tokenizer = AutoTokenizer.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment-latest")
    preprocessor = TextPreprocessor(contractions_path='static/contraction/contractions.json')

    def preprocess(text):
        text = preprocessor.preprocess_text(text)

        encoded_input = tokenizer(text, return_tensors='tf', padding=True, truncation=True, max_length=128)
        return encoded_input

    def decode_prediction(prediction):
        # 假设 prediction 是一个形状为 (1, 3) 的数组，包含三个类别的概率
        class_probabilities = prediction[0]
        return {
            'Negative_probability': float(class_probabilities[0]),
            'Neutral_probability': float(class_probabilities[1]),
            'Positive_probability': float(class_probabilities[2])
        }

    @app.route('/teacher/home')
    def teacher_home():
        if 'user_id' not in session or session['role'] != 'teacher':
            flash('You must be logged in as a teacher to view this page.')
            return redirect(url_for('login'))

        teacher_id = session['user_id']
        courses = Course.query.filter_by(teacher_id=teacher_id).all()

        # 创建一个字典，其中包括每个课程的额外信息
        courses_info = []
        for course in courses:
            # 计算注册的学生数
            enrolled_students_count = CourseRegistration.query.filter_by(course_id=course.id).count()

            # 计算提交了评论的学生数
            reviewed_students_count = CourseComments.query.filter(CourseComments.course_id == course.id).distinct(
                CourseComments.student_id).count()

            courses_info.append({
                'id': course.id,
                'name': course.name,
                'image_url': course.image_url,
                'enrolled_students_count': enrolled_students_count,
                'reviewed_students_count': reviewed_students_count
            })

        return render_template('teacher_home.html', courses=courses_info)

    @app.route('/teacher/course/<int:course_id>')
    def teacher_course_detail(course_id):
        if 'user_id' not in session or session['role'] != 'teacher':
            flash('You must be logged in as a teacher to view this page.')
            return redirect(url_for('login'))

        course = Course.query.get_or_404(course_id)
        # 获取所有注册此课程的学生
        registrations = CourseRegistration.query.filter_by(course_id=course_id).all()
        student_ids = [registration.student_id for registration in registrations]

        # 计算已注册和已评论的学生数量
        enrolled_students_count = len(student_ids)
        reviewed_students_count = CourseComments.query.filter(CourseComments.course_id == course_id).count()

        # 获取所有评论及其作者信息
        reviews = db.session.query(CourseComments, Student.name).join(Student,
                                                                      CourseComments.student_id == Student.id).filter(
            CourseComments.course_id == course_id).all()

        return render_template('teacher_course_detail.html', course=course, reviews=reviews,
                               enrolled_students_count=enrolled_students_count,
                               reviewed_students_count=reviewed_students_count)

    @app.route('/analyze_sentiments/<int:course_id>', methods=['GET'])
    def analyze_sentiments(course_id):
        if 'user_id' not in session or session['role'] != 'teacher':
            return jsonify({'error': 'Unauthorized'}), 401

        comments = ReviewSentiment.query.join(CourseComments).filter(CourseComments.course_id == course_id).all()
        if not comments:
            return jsonify({'error': 'No sentiment data found for this course.'}), 404

        sentiment_counts = {'Negative': 0, 'Neutral': 0, 'Positive': 0}

        for sentiment in comments:

            max_sentiment = max(sentiment.negative_probability, sentiment.neutral_probability,
                                sentiment.positive_probability)
            if max_sentiment == sentiment.negative_probability:
                sentiment_counts['Negative'] += 1
            elif max_sentiment == sentiment.neutral_probability:
                sentiment_counts['Neutral'] += 1
            else:
                sentiment_counts['Positive'] += 1

        return jsonify(sentiment_counts)

    @app.route('/get_wordcloud_data/<int:course_id>', methods=['GET'])
    def get_wordcloud_data(course_id):
        comments = CourseComments.query.filter_by(course_id=course_id).all()
        if not comments:
            return jsonify({'error': 'No comments found for this course'}), 404

        words_list = []

        # 遍历评论，对每条评论进行预处理并计数
        counter = Counter()
        for comment in comments:
            processed_text = preprocessor.preprocess_text(comment.comment)
            words = processed_text.split()  # 简单分词
            counter.update(words)  # 更新计数器

        # 将Counter对象转换为适合JSON序列化的格式
        words_list = [(word, count) for word, count in counter.items()]

        return jsonify(words_list)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            name = request.form['name']
            role = request.form['role']

            # 检查用户名是否已被注册
            user_exists = Student.query.filter_by(username=username).first() or Teacher.query.filter_by(
                username=username).first()
            if user_exists:
                flash('Username already taken')
                return redirect(url_for('register'))

            # 根据角色创建新用户
            if role == 'teacher':
                new_user = Teacher(username=username, password=password, name=name)
            else:
                new_user = Student(username=username, password=password, name=name)

            db.session.add(new_user)
            db.session.commit()

            flash('Registration successful')
            return redirect(url_for('index'))

        return render_template('login.html')  # 显示注册表单

    @app.route('/edit_course', methods=['POST'])
    def edit_course():
        course_id = request.form.get('course_id')
        course = Course.query.get(course_id)

        if course:
            course.name = request.form.get('name', course.name)
            course.description = request.form.get('description', course.description)
            course.image_url = request.form.get('image_url', course.image_url)
            try:
                db.session.commit()
                return jsonify({'message': 'Course updated successfully'}), 200
            except Exception as e:
                db.session.rollback()
                return jsonify({'error': str(e)}), 500
        else:
            return jsonify({'error': 'Course not found'}), 404

    @app.route('/add_course', methods=['POST'])
    def add_course():
        if 'user_id' not in session or session['role'] != 'teacher':
            return jsonify({'error': 'Unauthorized'}), 401

        try:
            # 从表单数据获取字段
            name = request.form['name']
            description = request.form['description']
            image_url = request.form.get('image_url', '')  # 如果未提供image_url，默认为空字符串
            teacher_id = session['user_id']  # 从会话中获取教师ID

            # 创建新的课程实例
            new_course = Course(
                name=name,
                description=description,
                image_url=image_url,
                teacher_id=teacher_id  # 设置课程的教师ID
            )

            # 添加到数据库
            db.session.add(new_course)
            db.session.commit()  # 提交数据库会话

            flash('Course added successfully!', 'success')
            return jsonify({'message': 'Course added successfully!'}), 200
        except Exception as e:
            # 输出错误信息到控制台，实际部署时应考虑日志记录
            print("Error adding course:", str(e))
            db.session.rollback()  # 回滚事务
            return jsonify({'error': 'Failed to add course.'}), 500

    from sqlalchemy import delete

    @app.route('/delete_course/<int:course_id>', methods=['DELETE'])
    def delete_course(course_id):
        if not Course.query.get(course_id):
            return jsonify({'error': 'Course not found'}), 404

        try:
            # 获取需要删除的评论情绪的ID
            sentiment_ids = db.session.query(ReviewSentiment.id).join(CourseComments).filter(
                CourseComments.course_id == course_id).all()
            sentiment_ids = [s[0] for s in sentiment_ids]
            if sentiment_ids:
                # 删除评论情绪
                db.session.execute(delete(ReviewSentiment).where(ReviewSentiment.id.in_(sentiment_ids)))

            # 删除评论
            db.session.execute(delete(CourseComments).where(CourseComments.course_id == course_id))

            # 删除注册信息
            db.session.execute(delete(CourseRegistration).where(CourseRegistration.course_id == course_id))

            # 删除课程
            db.session.delete(Course.query.get(course_id))
            db.session.commit()
            return jsonify({'message': 'Course deleted successfully'}), 200
        except Exception as e:
            db.session.rollback()
            print(e)  # 输出异常到控制台或日志
            return jsonify({'error': str(e)}), 500

    @app.route('/get_course/<int:course_id>', methods=['GET'])
    def get_course(course_id):
        course = Course.query.get(course_id)
        if course:
            course_data = {
                'id': course.id,
                'name': course.name,
                'description': course.description,
                'image_url': course.image_url
            }
            return jsonify(course_data), 200
        else:
            return jsonify({'error': 'Course not found'}), 404

    @app.route('/available_courses')
    def available_courses():
        # 假设已有当前用户ID从session中获取
        student_id = session.get('user_id')
        # 查询当前用户尚未注册的课程
        already_registered = db.session.query(CourseRegistration.course_id).filter(
            CourseRegistration.student_id == student_id)
        courses = Course.query.filter(Course.id.notin_(already_registered)).all()

        courses_data = [{
            'id': course.id,
            'name': course.name,
            'description': course.description,
            'image_url': course.image_url,
            'teacher_name': course.teacher.name
        } for course in courses]

        return jsonify(courses_data)

    @app.route('/register_course/<int:course_id>', methods=['POST'])
    def register_course(course_id):
        if 'user_id' not in session or session['role'] != 'student':
            return jsonify({'error': 'Unauthorized access'}), 401

        student_id = session['user_id']
        # 获取课程信息以检索教师ID
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'error': 'Course not found'}), 404

        existing_registration = CourseRegistration.query.filter_by(
            student_id=student_id, course_id=course_id).first()

        if existing_registration:
            return jsonify({'message': 'You are already registered for this course'}), 409

        # 创建新的课程注册实例，包括教师ID
        new_registration = CourseRegistration(
            course_id=course_id,
            teacher_id=course.teacher_id,  # 从课程实例中获取教师ID
            student_id=student_id
        )
        db.session.add(new_registration)
        try:
            db.session.commit()
            return jsonify({'message': 'Course registered successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to register course: ' + str(e)}), 500
