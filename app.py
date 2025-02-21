import os
from flask import Flask, jsonify, request, send_from_directory
from flask_pymongo import PyMongo
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/studentdb"
app.config["UPLOAD_FOLDER"] = "uploads"  # โฟลเดอร์เก็บไฟล์รูปภาพ
app.config["ALLOWED_EXTENSIONS"] = {'png', 'jpg', 'jpeg', 'gif'}
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)  # สร้างโฟลเดอร์ถ้ายังไม่มี
CORS(app)
mongo = PyMongo(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route("/students", methods=["POST"])
def add_student():
    if 'image' not in request.files:
        return jsonify({"message": "No image file found"}), 400
    image = request.files['image']
    if image and allowed_file(image.filename):
        filename = f"{request.form['id']}_{image.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(filepath)  # บันทึกรูปภาพในเซิร์ฟเวอร์
        image_url = f"/uploads/{filename}"
    else:
        return jsonify({"message": "Invalid image format"}), 400

    # บันทึกข้อมูลนักศึกษาใน MongoDB
    student_data = {
        "id": request.form["id"],
        "firstName": request.form["firstName"],
        "lastName": request.form["lastName"],
        "image": image_url,
    }
    mongo.db.students.insert_one(student_data)
    return jsonify({"message": "Student added successfully!"}), 201

@app.route("/uploads/<filename>")  # เสิร์ฟไฟล์รูปภาพ
def get_image(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

@app.route("/students", methods=["GET"])
def get_students():
    students = mongo.db.students.find({}, {"_id": 0})  # Exclude `_id`
    output = []
    for student in students:
        output.append({
            "id": student.get("id", "Unknown"),  # ใช้ get() เพื่อหลีกเลี่ยง KeyError
            "firstName": student.get("firstName", ""),
            "lastName": student.get("lastName", ""),
            "image": student.get("image", "")
        })
    return jsonify(output)

@app.route("/students/<id>", methods=["GET"])
def get_student_by_id(id):
    student = mongo.db.students.find_one({"id": id})
    if student:
        return jsonify({
            "id": student["id"],
            "firstName": student["firstName"],
            "lastName": student["lastName"],
            "image": student["image"]
        })
    else:
        return jsonify({"message": "Student not found"}), 404

@app.route("/students/<id>", methods=["DELETE"])
def delete_student(id):
    mongo.db.students.delete_one({"id": id})
    return jsonify({"message": "Student deleted"}), 200

@app.route('/students/<id>', methods=['PUT'])
def update_student(id):
    student = mongo.db.students.find_one({"id": id})
    if student:
        # ตรวจสอบและรับไฟล์ภาพใหม่
        image_file = request.files.get('image')
        if image_file:
            # บันทึกรูปภาพลงในโฟลเดอร์ที่คุณต้องการ
            filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_url = f"/uploads/{filename}"  # URL สำหรับไฟล์ที่อัปโหลด
        else:
            image_url = student['image']  # ใช้ภาพเดิมถ้าไม่มีการอัปโหลดภาพใหม่
        
        # อัปเดตข้อมูลนักศึกษา
        mongo.db.students.update_one(
            {"id": id},
            {"$set": {
                "firstName": request.form['firstName'],
                "lastName": request.form['lastName'],
                "image": image_url  # อัปเดต URL รูปภาพใหม่
            }}
        )
        return jsonify({"message": "Student updated"}), 200
    else:
        return jsonify({"message": "Student not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
