import oracledb
import os
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Cần thiết cho flash messages

# Cấu hình Oracle
oracle_path = r"D:\UNGDUNG\instantclient-basic-windows.x64-19.26.0.0.0dbru\instantclient_19_26" 
if oracle_path not in os.environ["PATH"]:
    os.environ["PATH"] = oracle_path + os.pathsep + os.environ["PATH"]
oracledb.init_oracle_client(lib_dir=oracle_path)

def get_db_connection():
    return oracledb.connect(
        user="quyetnv",
        password="123456",
        dsn="//localhost:1521/ORCL21PDB1"
    )

@app.route('/')
def index():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Thực thi truy vấn
        cursor.execute("""
            SELECT 
                CustomerID,
                FullName,
                Email,
                UserName,
                Phone,
                Address
            FROM Customers
            ORDER BY CustomerID
        """)
        
        # Lấy tên cột
        columns = [col[0] for col in cursor.description]
        # Chuyển đổi kết quả thành list of dictionaries
        customers = []
        for row in cursor:
            customers.append(dict(zip(columns, row)))
        
        cursor.close()
        conn.close()
        
        return render_template('index.html', customers=customers)
    except Exception as e:
        flash(f"Lỗi kết nối database: {str(e)}", "error")
        return render_template('index.html', customers=[])

@app.route('/add', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Lấy dữ liệu từ form
            fullname = request.form['fullname']
            email = request.form['email']
            username = request.form['username']
            phone = request.form['phone']
            address = request.form['address']
            
            # Thêm khách hàng mới
            cursor.execute("""
                INSERT INTO Customers (FullName, Email, UserName, Phone, Address, Password)
                VALUES (:1, :2, :3, :4, :5, :6)
            """, (fullname, email, username, phone, address, '123456'))  # Mật khẩu mặc định là 123456
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('Thêm khách hàng thành công!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Lỗi khi thêm khách hàng: {str(e)}', 'error')
            return redirect(url_for('add_customer'))
    
    return render_template('add_customer.html')

@app.route('/edit/<int:customer_id>', methods=['GET', 'POST'])
def edit_customer(customer_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if request.method == 'POST':
            # Lấy dữ liệu từ form
            fullname = request.form['fullname']
            email = request.form['email']
            username = request.form['username']
            phone = request.form['phone']
            address = request.form['address']
            
            # Cập nhật thông tin khách hàng
            cursor.execute("""
                UPDATE Customers 
                SET FullName = :1, Email = :2, UserName = :3, Phone = :4, Address = :5
                WHERE CustomerID = :6
            """, (fullname, email, username, phone, address, customer_id))
            
            conn.commit()
            flash('Cập nhật thông tin thành công!', 'success')
            return redirect(url_for('index'))
        
        # Lấy thông tin khách hàng hiện tại
        cursor.execute("""
            SELECT CustomerID, FullName, Email, UserName, Phone, Address
            FROM Customers
            WHERE CustomerID = :1
        """, (customer_id,))
        
        customer = cursor.fetchone()
        if customer:
            columns = [col[0] for col in cursor.description]
            customer_dict = dict(zip(columns, customer))
            cursor.close()
            conn.close()
            return render_template('edit_customer.html', customer=customer_dict)
        else:
            flash('Không tìm thấy khách hàng!', 'error')
            return redirect(url_for('index'))
            
    except Exception as e:
        flash(f'Lỗi: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/delete/<int:customer_id>', methods=['POST'])
def delete_customer(customer_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Xóa khách hàng
        cursor.execute("DELETE FROM Customers WHERE CustomerID = :1", (customer_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        flash('Xóa khách hàng thành công!', 'success')
    except Exception as e:
        flash(f'Lỗi khi xóa khách hàng: {str(e)}', 'error')
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)


