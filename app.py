from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from flask_cors import CORS  # เพิ่มเข้ามา

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/studentdb"
CORS(app)  # เปิดใช้งาน CORS สำหรับทุกแหล่งที่มาของการร้องขอ
mongo = PyMongo(app)

@app.route("/attendance", methods=["POST"])
def add_attendance():
    data = request.get_json()
    student_id = data["id"]
    attendance_status = data["attendance"]  # true or false
    date = data["date"]

    # บันทึกข้อมูลสถานะการมาเรียน
    mongo.db.attendance.insert_one({
        "student_id": student_id,
        "attendance": attendance_status,
        "date": date
    })

    return jsonify({"message": "Attendance added"}), 201


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


@app.route("/students", methods=["POST"])
def add_student():
    data = request.get_json()
    mongo.db.students.insert_one({
        "id": data["id"],
        "firstName": data["firstName"],
        "lastName": data["lastName"],
        "image": data.get("image", "")
    })
    return jsonify({"message": "Student added"}), 201

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

@app.route("/students/<id>", methods=["PUT"])  # เพิ่มเส้นทาง PUT
def update_student(id):
    data = request.get_json()
    student = mongo.db.students.find_one({"id": id})
    if student:
        mongo.db.students.update_one(
            {"id": id},
            {"$set": {
                "firstName": data["firstName"],
                "lastName": data["lastName"],
                "image": data.get("image", "")
            }}
        )
        return jsonify({"message": "Student updated"}), 200
    else:
        return jsonify({"message": "Student not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
