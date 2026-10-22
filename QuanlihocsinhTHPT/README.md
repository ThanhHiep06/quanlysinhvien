# Quản lý học sinh cấp THPT

Ứng dụng desktop Python + Tkinter + MySQL, tổ chức theo lớp.

## Chức năng có trong bản nền
- Dashboard thống kê học sinh, lớp, giáo viên, môn học.
- CRUD hồ sơ học sinh và tìm kiếm theo mã/tên.
- CRUD giáo viên, lớp học, môn học.
- Tra cứu điểm đã có trong database.
- Menu hệ thống và kiểm tra kết nối MySQL.

## Cài đặt
1. Mở MySQL Workbench hoặc phpMyAdmin và chạy toàn bộ `schema.sql`.
2. Chỉnh `app/config.py`: host, port, user, password.
3. Cài Python 3.10+ và MySQL Server. Trên Windows, Tkinter thường có sẵn theo Python.
4. Mở Terminal tại thư mục dự án:
   `python -m venv .venv`
5. Windows CMD: `.venv\\Scripts\\activate`
6. Cài thư viện: `python -m pip install -r requirements.txt`
7. Chạy: `python main.py`

## Cấu trúc
- `main.py`: điểm khởi chạy
- `app/config.py`: cấu hình kết nối
- `app/database.py`: lớp truy cập MySQL
- `app/ui.py`: MainWindow, BaseTab, StudentTab, SimpleCrudTab, DashboardTab, GradeTab
- `schema.sql`: thiết kế cơ sở dữ liệu

## Trường dữ liệu chính
`students`: student_id, student_code, full_name, date_of_birth, gender, phone, email, address, parent_name, parent_phone, class_id, enrollment_date, status, notes, created_at, updated_at.

`school_classes`: class_id, class_name, grade_level, school_year_id, homeroom_teacher_id.
`teachers`: teacher_id, teacher_code, full_name, phone, email, address.
`subjects`: subject_id, subject_code, subject_name, description.
`school_years`: school_year_id, year_name, start_date, end_date.
`semesters`: semester_id, school_year_id, semester_name.
`grades`: grade_id, student_id, subject_id, semester_id, oral_score, fifteen_min_score, midterm_score, final_score, average_score.
`attendance`: attendance_id, student_id, attendance_date, attendance_status, note.
`conduct_records`: record_id, student_id, record_date, record_type, description.
`users`: user_id, username, password_hash, full_name, role, is_active, created_at.

## Quan trọng
Đây là bản nền đồ án, chưa phải hệ thống sẵn sàng triển khai trong trường học thật. Tab điểm hiện chỉ tra cứu, chưa có form nhập/sửa điểm; đăng nhập/phân quyền, điểm danh, khen thưởng/kỷ luật, sao lưu/phục hồi và xuất báo cáo là các phần cần phát triển tiếp. Trước khi dùng dữ liệu thật, cần bổ sung xác thực dữ liệu, phân quyền, nhật ký thao tác và chính sách sao lưu.
