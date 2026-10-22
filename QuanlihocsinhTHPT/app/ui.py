import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from app.database import Database

class BaseTab(ttk.Frame):
    """Lớp cơ sở cho các màn hình quản lý."""
    def __init__(self, master, db):
        super().__init__(master, padding=12)
        self.db = db
        self.tree = None

    def make_tree(self, columns, headings, widths=None):
        frame = ttk.Frame(self)
        frame.pack(fill="both", expand=True, pady=10)
        self.tree = ttk.Treeview(frame, columns=columns, show="headings")
        ys = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        xs = ttk.Scrollbar(frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=ys.set, xscrollcommand=xs.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        ys.grid(row=0, column=1, sticky="ns")
        xs.grid(row=1, column=0, sticky="ew")
        frame.rowconfigure(0, weight=1); frame.columnconfigure(0, weight=1)
        for i, col in enumerate(columns):
            self.tree.heading(col, text=headings[i])
            self.tree.column(col, width=widths[i] if widths else 130, anchor="w")
        return self.tree

    def selected_id(self):
        if not self.tree or not self.tree.selection():
            messagebox.showwarning("Thông báo", "Hãy chọn một dòng dữ liệu.")
            return None
        return self.tree.item(self.tree.selection()[0], "values")[0]

class DashboardTab(ttk.Frame):
    def __init__(self, master, db):
        super().__init__(master, padding=22)
        self.db = db
        ttk.Label(self, text="TỔNG QUAN NHÀ TRƯỜNG", font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(0,18))
        self.labels = {}
        row = ttk.Frame(self); row.pack(fill="x")
        for key, title in [("students","Học sinh"),("classes","Lớp học"),("teachers","Giáo viên"),("subjects","Môn học")]:
            box = ttk.LabelFrame(row, text=title, padding=18); box.pack(side="left", expand=True, fill="x", padx=5)
            label = ttk.Label(box, text="0", font=("Segoe UI", 24, "bold")); label.pack()
            self.labels[key] = label
        ttk.Label(self, text="Nên tạo giáo viên, năm học và lớp học trước khi nhập học sinh.").pack(anchor="w", pady=25)
        ttk.Button(self, text="Làm mới thống kê", command=self.refresh).pack(anchor="w")
        self.refresh()

    def refresh(self):
        try:
            for key, table in [("students","students"),("classes","school_classes"),("teachers","teachers"),("subjects","subjects")]:
                self.labels[key].configure(text=str(self.db.fetch_one(f"SELECT COUNT(*) AS n FROM {table}")["n"]))
        except Exception as e:
            messagebox.showerror("Lỗi MySQL", str(e))

class StudentTab(BaseTab):
    FIELDS = [
        ("student_code","Mã học sinh"),("full_name","Họ và tên"),("date_of_birth","Ngày sinh YYYY-MM-DD"),
        ("gender","Giới tính"),("phone","Điện thoại"),("email","Email"),("address","Địa chỉ"),
        ("parent_name","Họ tên phụ huynh"),("parent_phone","SĐT phụ huynh"),("class_id","ID lớp"),
        ("enrollment_date","Ngày nhập học YYYY-MM-DD"),("status","Trạng thái"),("notes","Ghi chú")
    ]
    def __init__(self, master, db):
        super().__init__(master, db)
        ttk.Label(self, text="QUẢN LÝ HỌC SINH", font=("Segoe UI",16,"bold")).pack(anchor="w")
        bar = ttk.Frame(self); bar.pack(fill="x", pady=8)
        ttk.Label(bar,text="Tìm mã/tên:").pack(side="left")
        self.term = tk.StringVar()
        ttk.Entry(bar,textvariable=self.term,width=28).pack(side="left",padx=6)
        ttk.Button(bar,text="Tìm",command=self.refresh).pack(side="left")
        ttk.Button(bar,text="Tất cả",command=self.clear).pack(side="left",padx=4)
        ttk.Button(bar,text="Thêm",command=self.add).pack(side="right",padx=3)
        ttk.Button(bar,text="Sửa",command=self.edit).pack(side="right",padx=3)
        ttk.Button(bar,text="Xóa",command=self.delete).pack(side="right",padx=3)
        self.make_tree(("id","code","name","dob","gender","class","parent_phone","status"),
            ("ID","Mã HS","Họ tên","Ngày sinh","Giới tính","Lớp","SĐT phụ huynh","Trạng thái"),
            (50,100,180,100,80,90,130,130))
        self.refresh()

    def clear(self):
        self.term.set(""); self.refresh()

    def refresh(self):
        if self.tree is None: return
        self.tree.delete(*self.tree.get_children())
        try:
            sql = """SELECT s.student_id,s.student_code,s.full_name,s.date_of_birth,s.gender,
                     c.class_name,s.parent_phone,s.status FROM students s
                     LEFT JOIN school_classes c ON c.class_id=s.class_id"""
            params = ()
            if self.term.get().strip():
                sql += " WHERE s.student_code LIKE %s OR s.full_name LIKE %s"
                params = (f"%{self.term.get().strip()}%", f"%{self.term.get().strip()}%")
            sql += " ORDER BY s.student_id DESC"
            for r in self.db.fetch_all(sql,params):
                self.tree.insert("","end",values=(r["student_id"],r["student_code"],r["full_name"],
                    r["date_of_birth"] or "",r["gender"] or "",r["class_name"] or "(Chưa xếp lớp)",
                    r["parent_phone"] or "",r["status"]))
        except Exception as e: messagebox.showerror("Lỗi tải học sinh",str(e))

    def dialog(self, title, initial=None):
        initial = initial or {}
        win = tk.Toplevel(self); win.title(title); win.geometry("570x650"); win.transient(self.winfo_toplevel()); win.grab_set()
        canvas = tk.Canvas(win,highlightthickness=0); scroll = ttk.Scrollbar(win,orient="vertical",command=canvas.yview)
        form = ttk.Frame(canvas,padding=15); form.bind("<Configure>",lambda e:canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0),window=form,anchor="nw"); canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left",fill="both",expand=True); scroll.pack(side="right",fill="y")
        widgets = {}
        for i,(key,label) in enumerate(self.FIELDS):
            ttk.Label(form,text=label).grid(row=i,column=0,sticky="w",pady=5,padx=(0,12))
            if key == "gender":
                w=ttk.Combobox(form,values=["Nam","Nữ","Khác"],state="readonly",width=34); w.set(initial.get(key) or "Nam")
            elif key == "status":
                w=ttk.Combobox(form,values=["Đang học","Bảo lưu","Đã chuyển trường","Đã tốt nghiệp"],state="readonly",width=34); w.set(initial.get(key) or "Đang học")
            else:
                w=ttk.Entry(form,width=37)
                if initial.get(key) is not None: w.insert(0,str(initial[key]))
            w.grid(row=i,column=1,pady=5); widgets[key]=w

        def save():
            d={k:w.get().strip() for k,w in widgets.items()}
            if not d["student_code"] or not d["full_name"]:
                messagebox.showwarning("Thiếu dữ liệu","Mã học sinh và họ tên là bắt buộc.",parent=win); return
            try:
                for k in ("date_of_birth","enrollment_date"):
                    if d[k]: date.fromisoformat(d[k])
                    d[k]=d[k] or None
                d["class_id"]=int(d["class_id"]) if d["class_id"] else None
                for k in ("phone","email","address","parent_name","parent_phone","notes"): d[k]=d[k] or None
                if initial.get("student_id"):
                    self.db.execute("UPDATE students SET "+", ".join(f"{k}=%s" for k in d)+" WHERE student_id=%s",
                                    tuple(d.values())+(initial["student_id"],))
                else:
                    self.db.execute("INSERT INTO students ("+",".join(d)+") VALUES ("+",".join(["%s"]*len(d))+")",tuple(d.values()))
                win.destroy(); self.refresh()
            except ValueError:
                messagebox.showerror("Dữ liệu sai","Kiểm tra ID lớp và ngày tháng (YYYY-MM-DD).",parent=win)
            except Exception as e: messagebox.showerror("Không lưu được",str(e),parent=win)
        ttk.Button(form,text="Lưu",command=save).grid(row=len(self.FIELDS),column=0,pady=15)
        ttk.Button(form,text="Hủy",command=win.destroy).grid(row=len(self.FIELDS),column=1,pady=15)

    def add(self): self.dialog("Thêm học sinh")
    def edit(self):
        sid=self.selected_id()
        if sid is None:return
        try:self.dialog("Sửa học sinh",self.db.fetch_one("SELECT * FROM students WHERE student_id=%s",(sid,)))
        except Exception as e:messagebox.showerror("Lỗi",str(e))
    def delete(self):
        sid=self.selected_id()
        if sid is None:return
        if messagebox.askyesno("Xác nhận","Xóa học sinh này? Dữ liệu điểm và điểm danh liên quan có thể bị xóa."):
            try:self.db.execute("DELETE FROM students WHERE student_id=%s",(sid,));self.refresh()
            except Exception as e:messagebox.showerror("Không xóa được",str(e))

class SimpleCrudTab(BaseTab):
    """CRUD dùng chung cho giáo viên, lớp học và môn học."""
    def __init__(self, master, db, title, table, id_col, fields, columns, headings, widths):
        super().__init__(master,db); self.table=table; self.id_col=id_col; self.fields=fields
        ttk.Label(self,text=title,font=("Segoe UI",16,"bold")).pack(anchor="w")
        bar=ttk.Frame(self);bar.pack(fill="x",pady=8)
        for text,cmd in [("Thêm",self.add),("Sửa",self.edit),("Xóa",self.delete),("Làm mới",self.refresh)]:
            ttk.Button(bar,text=text,command=cmd).pack(side="left",padx=3)
        self.make_tree(columns,headings,widths);self.refresh()
    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        try:
            cols=[x[0] for x in self.fields]
            for r in self.db.fetch_all(f"SELECT {','.join(cols)} FROM {self.table} ORDER BY {self.id_col} DESC"):
                self.tree.insert("","end",values=tuple(r[c] or "" for c in cols))
        except Exception as e:messagebox.showerror("Lỗi tải dữ liệu",str(e))
    def dialog(self,title,initial=None):
        initial=initial or {}; win=tk.Toplevel(self);win.title(title);win.transient(self.winfo_toplevel());win.grab_set()
        form=ttk.Frame(win,padding=18);form.pack(fill="both",expand=True); widgets={}
        for i,(key,label) in enumerate(self.fields):
            ttk.Label(form,text=label).grid(row=i,column=0,sticky="w",pady=5,padx=(0,10))
            w=ttk.Entry(form,width=36);w.grid(row=i,column=1,pady=5)
            if initial.get(key) is not None:w.insert(0,str(initial[key]))
            widgets[key]=w
        def save():
            data={k:w.get().strip() for k,w in widgets.items()}
            keys=[k for k,_ in self.fields if k!=self.id_col]
            for k in keys:
                if not data[k]:data[k]=None
            try:
                if initial.get(self.id_col):
                    self.db.execute(f"UPDATE {self.table} SET "+",".join(f"{k}=%s" for k in keys)+f" WHERE {self.id_col}=%s",
                                    tuple(data[k] for k in keys)+(initial[self.id_col],))
                else:
                    self.db.execute(f"INSERT INTO {self.table} ("+",".join(keys)+") VALUES ("+",".join(["%s"]*len(keys))+")",
                                    tuple(data[k] for k in keys))
                win.destroy();self.refresh()
            except Exception as e:messagebox.showerror("Không lưu được",str(e),parent=win)
        ttk.Button(form,text="Lưu",command=save).grid(row=len(self.fields),column=0,pady=12)
        ttk.Button(form,text="Hủy",command=win.destroy).grid(row=len(self.fields),column=1,pady=12)
    def add(self):self.dialog("Thêm dữ liệu")
    def edit(self):
        ident=self.selected_id()
        if ident is None:return
        try:self.dialog("Sửa dữ liệu",self.db.fetch_one(f"SELECT * FROM {self.table} WHERE {self.id_col}=%s",(ident,)))
        except Exception as e:messagebox.showerror("Lỗi",str(e))
    def delete(self):
        ident=self.selected_id()
        if ident is None:return
        if messagebox.askyesno("Xác nhận","Bạn chắc chắn muốn xóa dòng này?"):
            try:self.db.execute(f"DELETE FROM {self.table} WHERE {self.id_col}=%s",(ident,));self.refresh()
            except Exception as e:messagebox.showerror("Không xóa được",str(e))

class GradeTab(BaseTab):
    def __init__(self,master,db):
        super().__init__(master,db)
        ttk.Label(self,text="TRA CỨU ĐIỂM SỐ",font=("Segoe UI",16,"bold")).pack(anchor="w")
        ttk.Label(self,text="Tab hiện dùng để tra cứu điểm đã có. Biểu mẫu nhập/sửa điểm là phần nên phát triển tiếp.").pack(anchor="w",pady=8)
        bar=ttk.Frame(self);bar.pack(fill="x",pady=5);ttk.Label(bar,text="Mã học sinh:").pack(side="left")
        self.code=tk.StringVar();ttk.Entry(bar,textvariable=self.code,width=20).pack(side="left",padx=5)
        ttk.Button(bar,text="Tra cứu",command=self.refresh).pack(side="left")
        ttk.Button(bar,text="Tất cả",command=self.all).pack(side="left",padx=5)
        self.make_tree(("code","name","subject","semester","oral","fifteen","mid","final","avg"),
            ("Mã HS","Họ tên","Môn","Học kỳ","Miệng","15 phút","Giữa kỳ","Cuối kỳ","TB"),
            (90,160,130,100,70,70,80,80,70));self.refresh()
    def all(self):self.code.set("");self.refresh()
    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        try:
            sql="""SELECT st.student_code,st.full_name,su.subject_name,se.semester_name,g.oral_score,
                   g.fifteen_min_score,g.midterm_score,g.final_score,g.average_score
                   FROM grades g JOIN students st ON st.student_id=g.student_id
                   JOIN subjects su ON su.subject_id=g.subject_id JOIN semesters se ON se.semester_id=g.semester_id"""
            params=()
            if self.code.get().strip():sql+=" WHERE st.student_code LIKE %s";params=(f"%{self.code.get().strip()}%",)
            for r in self.db.fetch_all(sql+" ORDER BY st.student_code,su.subject_name",params):
                self.tree.insert("","end",values=tuple(r[k] if r[k] is not None else "" for k in
                    ("student_code","full_name","subject_name","semester_name","oral_score","fifteen_min_score","midterm_score","final_score","average_score")))
        except Exception as e:messagebox.showerror("Lỗi tra cứu điểm",str(e))

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__();self.title("Quản lý học sinh cấp THPT");self.geometry("1250x760");self.minsize(1000,620)
        self.db=Database();self.style_ui();self.make_menu()
        header=tk.Frame(self,bg="#16324F",padx=20,pady=14);header.pack(fill="x")
        tk.Label(header,text="QUẢN LÝ HỌC SINH CẤP THPT",bg="#16324F",fg="white",font=("Segoe UI",17,"bold")).pack(side="left")
        tk.Label(header,text="PYTHON • TKINTER • MYSQL",bg="#16324F",fg="#D6E6F2").pack(side="right")
        self.nb=ttk.Notebook(self);self.nb.pack(fill="both",expand=True,padx=12,pady=12);self.tabs=[]
        self.add_tab(DashboardTab(self.nb,self.db),"Tổng quan")
        self.add_tab(StudentTab(self.nb,self.db),"Học sinh")
        self.add_tab(SimpleCrudTab(self.nb,self.db,"QUẢN LÝ GIÁO VIÊN","teachers","teacher_id",
            [("teacher_id","ID"),("teacher_code","Mã giáo viên"),("full_name","Họ tên"),("phone","Điện thoại"),("email","Email"),("address","Địa chỉ")],
            ("teacher_id","teacher_code","full_name","phone","email"),("ID","Mã GV","Họ tên","Điện thoại","Email"),(55,100,180,130,180)),"Giáo viên")
        self.add_tab(SimpleCrudTab(self.nb,self.db,"QUẢN LÝ LỚP HỌC","school_classes","class_id",
            [("class_id","ID"),("class_name","Tên lớp"),("grade_level","Khối 10/11/12"),("school_year_id","ID năm học"),("homeroom_teacher_id","ID GVCN")],
            ("class_id","class_name","grade_level","school_year_id","homeroom_teacher_id"),("ID","Tên lớp","Khối","ID năm học","ID GVCN"),(55,140,90,100,100)),"Lớp học")
        self.add_tab(SimpleCrudTab(self.nb,self.db,"QUẢN LÝ MÔN HỌC","subjects","subject_id",
            [("subject_id","ID"),("subject_code","Mã môn"),("subject_name","Tên môn"),("description","Mô tả")],
            ("subject_id","subject_code","subject_name","description"),("ID","Mã môn","Tên môn","Mô tả"),(55,100,180,250)),"Môn học")
        self.add_tab(GradeTab(self.nb,self.db),"Tra cứu điểm")
        self.protocol("WM_DELETE_WINDOW",self.destroy)
    def add_tab(self,tab,title):self.nb.add(tab,text=title);self.tabs.append(tab)
    def style_ui(self):
        s=ttk.Style(self)
        try:s.theme_use("clam")
        except tk.TclError:pass
        s.configure("TButton",padding=(8,5));s.configure("Treeview",rowheight=27)
        s.configure("Treeview.Heading",font=("Segoe UI",9,"bold"));s.configure("TNotebook.Tab",padding=(14,8))
    def make_menu(self):
        menu=tk.Menu(self);sys=tk.Menu(menu,tearoff=False)
        sys.add_command(label="Kiểm tra kết nối MySQL",command=self.test_db)
        sys.add_command(label="Làm mới dữ liệu",command=self.refresh_all);sys.add_separator()
        sys.add_command(label="Thoát",command=self.destroy);menu.add_cascade(label="Hệ thống",menu=sys)
        helpm=tk.Menu(menu,tearoff=False);helpm.add_command(label="Thông tin",command=lambda:messagebox.showinfo("Thông tin","Quản lý học sinh cấp THPT\nPython + Tkinter + MySQL"))
        menu.add_cascade(label="Trợ giúp",menu=helpm);self.config(menu=menu)
    def test_db(self):
        try:self.db.fetch_one("SELECT 1");messagebox.showinfo("MySQL","Kết nối thành công.")
        except Exception as e:messagebox.showerror("Kết nối thất bại",f"{e}\nKiểm tra app/config.py và dịch vụ MySQL.")
    def refresh_all(self):
        for t in self.tabs:
            if hasattr(t,"refresh"):t.refresh()

