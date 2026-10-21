from flask import Flask, request, redirect, jsonify, session
import sqlite3
from datetime import datetime, date
import os

app = Flask(__name__)
app.secret_key = "corphrms"

def db():
    conn = sqlite3.connect('corphrms.db')
    conn.row_factory = sqlite3.Row
    return conn

def init():
    conn = db(); c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS employees (id INTEGER PRIMARY KEY, name TEXT, designation TEXT, salary REAL, join_date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (id INTEGER PRIMARY KEY, emp_id INTEGER, date TEXT, status TEXT, check_in TEXT, check_out TEXT)''')
    c.execute("SELECT COUNT(*) FROM employees")
    if c.fetchone()[0]==0:
        c.execute("INSERT INTO employees VALUES (1,'Jessica Taylor','Senior Developer',1500,'2025-01-15')")
        c.execute("INSERT INTO employees VALUES (2,'Marcus Vance','Product Lead',7000,'2025-02-20')")
        c.execute("INSERT INTO employees VALUES (3,'Elena Rostova','UI/UX Specialist',4800,'2025-03-10')")
        c.execute("INSERT INTO employees VALUES (4,'dev','hr',121.67,'2025-10-20')")
    conn.commit(); conn.close()
init()

LOGIN_HTML = """
<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CorpHRMS - Login</title>
<style>body{margin:0;background:#0f172a;display:flex;align-items:center;justify-content:center;height:100vh;font-family:Inter,Arial;color:white}
.box{background:#1e293b;padding:35px;border-radius:16px;width:320px;text-align:center;box-shadow:0 10px 30px #0005}
.logo{width:45px;height:45px;background:#3b82f6;border-radius:12px;display:flex;align-items:center;justify-content:center;margin:0 auto 10px;font-weight:bold}
input{width:100%;padding:12px;margin:8px 0;border-radius:8px;border:1px solid #334155;background:#0f172a;color:white;box-sizing:border-box}
button{width:100%;padding:12px;background:#3b82f6;border:none;border-radius:8px;color:white;font-weight:bold;cursor:pointer;margin-top:10px}
small{color:#94a3b8}</style></head><body>
<div class="box"><div class="logo">C</div><h3>Admin Portal</h3><p><small>Attendance & Payroll System</small></p>
<form action="/login" method="POST"><input name="username" placeholder="Username" value="admin" required><input name="password" type="password" placeholder="Password" value="admin" required><button>Secure Login</button></form>
<p><small>Default: admin / admin</small></p></div></body></html>
"""

BASE = """
<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CorpHRMS</title>
<style>
body{margin:0;font-family:Inter,Arial;background:#f8fafc;display:flex}
.sidebar{width:220px;background:#0f172a;color:white;height:100vh;position:fixed;padding:15px;box-sizing:border-box}
.sidebar h3{margin:10px 0} .menu a{display:block;padding:10px 12px;color:#94a3b8;text-decoration:none;border-radius:8px;margin:4px 0}
.menu a.active{background:#1e293b;color:white}
.main{margin-left:220px;padding:20px;width:calc(100% - 220px);box-sizing:border-box}
.card{background:white;border-radius:12px;padding:15px;margin-bottom:15px;box-shadow:0 1px 3px #0001}
.top{display:grid;grid-template-columns:repeat(5,1fr);gap:12px}
.stat{border-left:4px solid #ddd;padding:10px} .stat b{font-size:20px}
table{width:100%;border-collapse:collapse} th,td{padding:10px;border-bottom:1px solid #eee;text-align:left;font-size:14px}
.btn{padding:6px 10px;border:none;border-radius:6px;cursor:pointer} .blue{background:#2563eb;color:white} .red{background:#ef4444;color:white}
.modal{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:#0006;align-items:center;justify-content:center}
.modal .box{background:white;padding:20px;border-radius:12px;width:350px}
input,select{width:100%;padding:8px;margin:5px 0;border:1px solid #ddd;border-radius:6px;box-sizing:border-box}
</style></head><body>
<div class="sidebar"><h3>CorpHRMS</h3><div class="menu">
<a href="/dashboard" class="{{d1}}">Dashboard</a>
<a href="/employees" class="{{d2}}">Employees & Crew</a>
<a href="/attendance" class="{{d3}}">Attendance & Shifts</a>
<a href="/payroll" class="{{d4}}">Payroll & Slips</a>
</div><div style="position:absolute;bottom:20px"><small>System Admin<br><a href="/logout" style="color:#f87171">Logout</a></small></div></div>
<div class="main">{{content}}</div>
<script>
function openModal(){document.getElementById('empModal').style.display='flex'}
function closeModal(){document.getElementById('empModal').style.display='none'}
function delEmp(id){if(confirm('Are you sure you want to delete the employee record and associated metadata?')){fetch('/delete/'+id).then(()=>location.reload())}}
</script>
</body></html>
"""

@app.route('/')
def index():
    return LOGIN_HTML

@app.route('/login', methods=['POST'])
def login():
    if request.form['username']=='admin' and request.form['password']=='admin':
        session['admin']=True
        return redirect('/dashboard')
    return "Wrong! admin/admin use karo <a href='/'>Back</a>"

@app.route('/logout')
def logout():
    session.clear(); return redirect('/')

@app.route('/dashboard')
def dashboard():
    if not session.get('admin'): return redirect('/')
    conn=db(); c=conn.cursor()
    c.execute("SELECT COUNT(*) FROM employees"); total=c.fetchone()[0]
    today=str(date.today())
    c.execute("SELECT COUNT(*) FROM attendance WHERE date=? AND status='Present'",(today,)); present=c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM attendance WHERE date=? AND status='Absent'",(today,)); absent=c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM attendance WHERE date=? AND status='Leave'",(today,)); leave=c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM attendance WHERE date=? AND status='Remote'",(today,)); remote=c.fetchone()[0]
    c.execute("SELECT SUM(salary) FROM employees"); gross=c.fetchone()[0] or 0
    c.execute("SELECT * FROM attendance JOIN employees ON attendance.emp_id=employees.id ORDER BY attendance.id DESC LIMIT 5"); history=c.fetchall()
    conn.close()
    gross_str = f"${gross:,.2f}"
    deduction = 183.00
    net = gross - deduction
    content = f"""
    <div style="display:flex;justify-content:space-between"><h2>Executive Dashboard</h2><small>{today} | System Admin</small></div>
    <div class="top">
      <div class="card stat" style="border-color:#3b82f6"><small>TOTAL STAFF</small><br><b>{total}</b></div>
      <div class="card stat" style="border-color:#22c55e"><small>PRESENT TODAY</small><br><b>{present}</b></div>
      <div class="card stat" style="border-color:#ef4444"><small>ABSENT TODAY</small><br><b>{absent}</b></div>
      <div class="card stat" style="border-color:#f59e0b"><small>ON LEAVE</small><br><b>{leave}</b></div>
      <div class="card stat" style="border-color:#8b5cf6"><small>REMOTE</small><br><b>{remote}</b></div>
    </div>
    <div class="card"><h3>Payroll & Financial Overview</h3><div style="display:grid;grid-template-columns:repeat(3,1fr);gap:15px">
      <div><small>Gross Salary Allocated</small><br><b>{gross_str}</b></div>
      <div><small>Absent Deduction Applied</small><br><b style="color:red">-${deduction:.2f}</b></div>
      <div><small>Net Payable Processed</small><br><b style="color:green">${net:,.2f}</b></div>
    </div></div>
    <div class="card"><h3>All Employees Attendance History Feed</h3>
    <table><tr><th>LOG ID</th><th>EMPLOYEE NAME</th><th>STATUS</th><th>DATE & TIME</th><th>CHECK IN/OUT</th></tr>
    {"".join([f"<tr><td>LOG-{h['id']:04d}</td><td>{h['name']}</td><td>{h['status']}</td><td>{h['date']}</td><td>{h['check_in'] or '--'} / {h['check_out'] or '--'}</td></tr>" for h in history])}
    </table></div>
    """
    return BASE.replace("{{content}}",content).replace("{{d1}}","active").replace("{{d2}}","").replace("{{d3}}","").replace("{{d4}}","")

@app.route('/employees')
def employees():
    if not session.get('admin'): return redirect('/')
    conn=db(); c=conn.cursor(); c.execute("SELECT * FROM employees"); emps=c.fetchall(); conn.close()
    rows="".join([f"<tr><td>{e['name']}</td><td>{e['designation']}</td><td>${e['salary']}</td><td>{e['join_date']}</td><td><button class='btn red' onclick='delEmp({e['id']})'>Delete</button></td></tr>" for e in emps])
    content=f"""
    <div style="display:flex;justify-content:space-between"><h2>Employee Directory</h2><button class="btn blue" onclick="openModal()">+ Add New Employee</button></div>
    <div class="card"><table><tr><th>EMPLOYEE NAME</th><th>DESIGNATION</th><th>MONTHLY BASE</th><th>JOIN DATE</th><th>ACTIONS</th></tr>{rows}</table></div>
    <div class="modal" id="empModal"><div class="box"><h3>Register New Employee</h3>
    <form action="/add_employee" method="POST"><input name="name" placeholder="Full Name" required><input name="designation" placeholder="Designation / Role" required><input name="salary" type="number" step="0.01" placeholder="Monthly Base Salary" required><input name="join_date" type="date" value="{date.today()}" required><div style="display:flex;gap:10px"><button type="button" onclick="closeModal()">Cancel</button><button class="btn blue" type="submit">Save Record</button></div></form></div></div>
    """
    return BASE.replace("{{content}}",content).replace("{{d1}}","").replace("{{d2}}","active").replace("{{d3}}","").replace("{{d4}}","")

@app.route('/add_employee', methods=['POST'])
def add_employee():
    conn=db(); c=conn.cursor()
    c.execute("INSERT INTO employees (name,designation,salary,join_date) VALUES (?,?,?,?)",(request.form['name'],request.form['designation'],request.form['salary'],request.form['join_date']))
    conn.commit(); conn.close(); return redirect('/employees')

@app.route('/delete/<int:id>')
def delete_emp(id):
    conn=db(); c=conn.cursor(); c.execute("DELETE FROM employees WHERE id=?",(id,)); c.execute("DELETE FROM attendance WHERE emp_id=?",(id,)); conn.commit(); conn.close(); return "ok"

@app.route('/attendance')
def attendance_page():
    if not session.get('admin'): return redirect('/')
    today=str(date.today())
    conn=db(); c=conn.cursor()
    c.execute("SELECT * FROM employees")
    emps=c.fetchall()
    # ensure today's attendance exists
    for e in emps:
        c.execute("SELECT * FROM attendance WHERE emp_id=? AND date=?",(e['id'],today))
        if not c.fetchone():
            c.execute("INSERT INTO attendance (emp_id,date,status) VALUES (?,?,?)",(e['id'],today,'Absent'))
    conn.commit()
    c.execute("SELECT e.name,a.* FROM attendance a JOIN employees e ON e.id=a.emp_id WHERE a.date=?",(today,)); atts=c.fetchall(); conn.close()
    rows=""
    for a in atts:
        rows+=f"<tr><td>{a['name']}</td><td><select onchange=\"fetch('/set_status/'+{a['id']}+'/'+this.value)\"><option>{a['status']}</option><option>Present</option><option>Absent</option><option>Leave</option><option>Remote</option></select></td><td><input type='time' value='{a['check_in'] or ''}' onchange=\"fetch('/set_in/'+{a['id']}+'/'+this.value)\"></td><td><input type='time' value='{a['check_out'] or ''}' onchange=\"fetch('/set_out/'+{a['id']}+'/'+this.value)\"></td><td>✅</td></tr>"
    content=f"""
    <h2>Attendance & Leave Management</h2>
    <div class="card"><table><tr><th>EMPLOYEE NAME</th><th>STATUS</th><th>CHECK IN TIME</th><th>CHECK OUT TIME</th><th>ACTIONS</th></tr>{rows}</table></div>
    """
    return BASE.replace("{{content}}",content).replace("{{d1}}","").replace("{{d2}}","").replace("{{d3}}","active").replace("{{d4}}","")

@app.route('/set_status/<int:id>/<status>')
def set_status(id,status):
    conn=db(); c=conn.cursor(); c.execute("UPDATE attendance SET status=? WHERE id=?",(status,id)); conn.commit(); conn.close(); return "ok"
@app.route('/set_in/<int:id>/<t>')
def set_in(id,t):
    conn=db(); c=conn.cursor(); c.execute("UPDATE attendance SET check_in=? WHERE id=?",(t,id)); conn.commit(); conn.close(); return "ok"
@app.route('/set_out/<int:id>/<t>')
def set_out(id,t):
    conn=db(); c=conn.cursor(); c.execute("UPDATE attendance SET check_out=? WHERE id=?",(t,id)); conn.commit(); conn.close(); return "ok"

@app.route('/payroll')
def payroll():
    if not session.get('admin'): return redirect('/')
    conn=db(); c=conn.cursor()
    c.execute("SELECT e.*, COUNT(a.id) as days, SUM(CASE WHEN a.status='Absent' THEN 1 ELSE 0 END) as abs FROM employees e LEFT JOIN attendance a ON e.id=a.emp_id GROUP BY e.id"); data=c.fetchall(); conn.close()
    rows=""
    for d in data:
        days=d['days'] or 0; absent=d['abs'] or 0; salary=d['salary']
        deduction= round(salary/30*absent,2) if days>0 else 0
        bonus=0
        net= round(salary - deduction + bonus,2)
        rows+=f"<tr><td>{d['name']}</td><td>${salary}</td><td>{days} Days</td><td>${deduction}</td><td>{bonus}</td><td>${net}</td><td><button class='btn blue' onclick=\"window.print()\">Slip</button></td></tr>"
    content=f"""<h2>Payroll Calculation & Payslips</h2><div class="card"><table><tr><th>EMPLOYEE NAME</th><th>BASE SALARY</th><th>ATTENDANCE DAYS</th><th>DEDUCTIONS</th><th>BONUS</th><th>NET PAYABLE</th><th>SLIP</th></tr>{rows}</table></div>"""
    return BASE.replace("{{content}}",content).replace("{{d1}}","").replace("{{d2}}","").replace("{{d3}}","").replace("{{d4}}","active")

if __name__=='__main__':
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0' , port=port)
