import pyodbc
import joblib
import pandas as pd
import os
import datetime
from flask import Flask,jsonify, render_template, request, redirect, url_for, session, send_from_directory, make_response

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Key bí mật cho session

# Định nghĩa đường dẫn tĩnh
frontend_css = os.path.join(app.root_path, 'frontend', 'css')
frontend_js = os.path.join(app.root_path, 'frontend', 'js')
frontend_ui = os.path.join(app.root_path, 'frontend', 'ui')
frontend_uploads = os.path.join(app.root_path, 'frontend', 'uploads')
backend_uploads = os.path.join(app.root_path, 'backend', 'uploads')

# Cập nhật để phục vụ các tệp tĩnh từ frontend và backend
@app.route('/frontend/css/<path:filename>')
def serve_css(filename):
    return send_from_directory(frontend_css, filename)


@app.route('/frontend/js/<path:filename>')
def serve_js(filename):
    return send_from_directory(frontend_js, filename)


@app.route('/frontend/uploads/<path:filename>')
def serve_frontend_uploads(filename):
    return send_from_directory(frontend_uploads, filename)


@app.route('/backend/uploads/<path:filename>')
def serve_backend_uploads(filename):
    return send_from_directory(backend_uploads, filename)

@app.route('/frontend/ui/<path:filename>')
def serve_ui(filename):
    return send_from_directory(frontend_ui, filename)


app.template_folder = os.path.join(app.root_path, 'frontend', 'ui')


# Kết nối đến SQL Server
def connect_to_sql_server():
    server = r'MSI\SQLEXPRESS'  
    database = 'LoanPrediction'  
    username = ''  
    password = '' 

    try:
        conn = pyodbc.connect(
            f'DRIVER={{SQL Server}};'
            f'SERVER={server};'
            f'DATABASE={database};'
            f'UID={username};'
            f'PWD={password};'
        )
        print("Kết nối cơ sở dữ liệu thành công!")
        return conn
    except Exception as e:
        print(f"Error connecting to SQL Server: {e}")
        return None

# Route kiểm tra kết nối cơ sở dữ liệu
@app.route('/check-db-connection')
def check_db_connection():
    conn = connect_to_sql_server()
    if conn:
        # Nếu kết nối thành công
        return 'Kết nối cơ sở dữ liệu thành công!'
    else:
        # Nếu kết nối thất bại
        return 'Không thể kết nối cơ sở dữ liệu!'

# Kiểm tra đăng nhập của người dùng
def check_user_login(username, password):
    try:
        conn = connect_to_sql_server()
        if conn:
            cursor = conn.cursor()

            # Truy vấn cơ sở dữ liệu để kiểm tra tài khoản
            cursor.execute("SELECT iduser, username, password FROM UserBank WHERE username=? AND password=?", (username, password))
            user = cursor.fetchone()

            cursor.close()
            conn.close()

            # Nếu tìm thấy người dùng thì trả về thông tin người dùng
            if user:
                return user
            else:
                return None
        else:
            return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None


# Route đăng nhập
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Kiểm tra thông tin đăng nhập từ cơ sở dữ liệu
        user = check_user_login(username, password)

        if user:
            # Đăng nhập thành công, lưu thông tin vào session
            session['user_id'] = user[0]  # Lưu ID người dùng vào session
            session['username'] = user[1]  # Lưu username vào session
            return redirect(url_for('loan_prediction'))  # Chuyển hướng đến trang dự đoán
        else:
            # Nếu thông tin đăng nhập sai
            return render_template('login.html', error="Invalid username or password")

    return render_template('login.html')

#route đăng ký

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        gmail = request.form['gmail']
        address = request.form['address']
        phonenumber = request.form['phonenumber']

        # Kiểm tra nếu mật khẩu và xác nhận mật khẩu khớp
        if password != confirm_password:
            return render_template('register.html', error="Mật khẩu không khớp.")

        # Kiểm tra xem tên người dùng đã tồn tại trong cơ sở dữ liệu chưa
        try:
            conn = connect_to_sql_server()
            if conn:
                cursor = conn.cursor()

                cursor.execute("SELECT iduser FROM UserBank WHERE username=?", (username,))
                existing_user = cursor.fetchone()

                if existing_user:
                    return render_template('register.html', error="Tên người dùng đã tồn tại.")

                # Tạo ID người dùng tự sinh (bằng cách lấy id lớn nhất hiện tại và cộng thêm 1)
                cursor.execute("SELECT MAX(iduser) FROM UserBank")
                max_id = cursor.fetchone()[0]
                if max_id is None:  # Nếu bảng rỗng, bắt đầu từ 1
                    new_id = 1
                else:
                    new_id = max_id + 1  # Tăng giá trị ID lên 1

                # Lưu thông tin người dùng vào cơ sở dữ liệu
                cursor.execute("""
                    INSERT INTO UserBank (iduser, username, password, address, phonenumber, gmail)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (new_id, username, password, address, phonenumber, gmail))
                conn.commit()

                cursor.close()
                conn.close()

                return redirect(url_for('login'))  # Chuyển hướng về trang đăng nhập

            else:
                return render_template('register.html', error="Không thể kết nối cơ sở dữ liệu.")
        
        except Exception as e:
            print(f"Error: {str(e)}")
            return render_template('register.html', error="Đã xảy ra lỗi trong quá trình đăng ký.")
        
    return render_template('register.html')

    


# Route đăng xuất
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()  # Xóa session khi người dùng đăng xuất
    return redirect(url_for('login'))  # Chuyển hướng về trang login



# Hàm dùng để tính toán rickcore
def load_and_predict(**inputs):
    try:
     
        model = joblib.load("risk_score_model.pkl") 
        weights = model["weights"]
        intercept = model["intercept"]
        threshold = model["threshold"]


        missing_features = [feature for feature in weights.keys() if feature not in inputs]
        if missing_features:
            raise ValueError(f"Missing features in inputs: {missing_features}")

       
        risk_score = sum(inputs[feature] * weights[feature] for feature in weights.keys()) + intercept

  
        prediction = "Không có khả năng thanh toán" if risk_score >= threshold else "Có khả năng thanh toán"

        return risk_score, prediction

    except FileNotFoundError:
        raise ValueError("Model file not found. Please ensure 'risk_score_model.pkl' exists.")
    except KeyError as e:
        raise ValueError(f"Model is missing expected keys: {e}")
    except Exception as e:
        raise ValueError(f"Error in prediction logic: {e}")


# hàm lấy dữ liệu kết quả sao khi kiểm tra từ database
def store_prediction_in_db(risk_score, prediction, inputs):
    conn = connect_to_sql_server()
    if conn:
        cursor = conn.cursor()
   
        try:
            cursor.execute(""" 
                INSERT INTO predictions (
                    UserName, Email, PhoneNumber, RegistrationDate, AccountStatus,
                    TotalDebtToIncomeRatio, BankruptcyHistory, DebtToIncomeRatio, 
                    NetWorth, MonthlyIncome, InterestRate, PreviousLoanDefaults, 
                    AnnualIncome, CreditScore, LengthOfCreditHistory, RiskScore, Prediction
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                inputs["UserName"], inputs["Email"], inputs["PhoneNumber"], inputs["RegistrationDate"], inputs["AccountStatus"],
                inputs["TotalDebtToIncomeRatio"], inputs["BankruptcyHistory"], inputs["DebtToIncomeRatio"],
                inputs["NetWorth"], inputs["MonthlyIncome"], inputs["InterestRate"], inputs["PreviousLoanDefaults"],
                inputs["AnnualIncome"], inputs["CreditScore"], inputs["LengthOfCreditHistory"],
                risk_score, prediction
            ))
            conn.commit()
            print("Prediction stored in database successfully.")
        except Exception as e:
            print(f"Error storing prediction: {e}")
        finally:
            cursor.close()
            conn.close()

            
# Route để lấy dữ liệu từ cơ sở dữ liệu và hiển thị trên result_data.html
@app.route('/result-data')
def result_data():
    try:
        conn = connect_to_sql_server()
        if conn:
            cursor = conn.cursor()

       
            cursor.execute("SELECT UserName, Email, PhoneNumber, RegistrationDate, AccountStatus, RiskScore, Prediction FROM predictions")
            rows = cursor.fetchall()

            cursor.close()
            conn.close()

            
            return render_template('result_data.html', predictions=rows)

        else:
            return render_template('result_data.html', error="Không thể kết nối cơ sở dữ liệu!")

    except Exception as e:
        return render_template('result_data.html', error=f"Đã xảy ra lỗi: {e}")



# hàm xử lý dự đoán 
@app.route('/', methods=['GET', 'POST'])
def loan_prediction():
    if 'username' not in session:
        return redirect(url_for('login'))  # Nếu người dùng chưa đăng nhập, chuyển hướng về trang đăng nhập.

    if request.method == 'POST':
        # Các tính năng mà bạn muốn tính toán
        features = [
            "TotalDebtToIncomeRatio", "BankruptcyHistory", "DebtToIncomeRatio", "NetWorth",
            "MonthlyIncome", "InterestRate", "PreviousLoanDefaults", "AnnualIncome",
            "CreditScore", "LengthOfCreditHistory"
        ]

        # Tạo từ điển để lưu trữ giá trị đầu vào
        inputs = {}
        try:
            # Lấy dữ liệu từ form và chuyển đổi chúng thành float
            for feature in features:
                value = request.form.get(feature)
                if value is None:
                    return render_template('index.html', error=f"Missing field: {feature}")
                try:
                    inputs[feature] = float(value)
                except ValueError:
                    return render_template('index.html', error=f"Invalid value for {feature}")

            # Lấy thêm dữ liệu từ form
            inputs["UserName"] = request.form.get("UserName")
            inputs["Email"] = request.form.get("Email")
            inputs["PhoneNumber"] = request.form.get("PhoneNumber")
            inputs["RegistrationDate"] = request.form.get("RegistrationDate")
            inputs["AccountStatus"] = request.form.get("AccountStatus")

            # Tính toán điểm rủi ro và dự đoán
            risk_score, prediction = load_and_predict(**inputs)

            # Lưu kết quả vào cơ sở dữ liệu
            store_prediction_in_db(risk_score, prediction, inputs)

            # Trả về kết quả cho người dùng
            return render_template('index.html', risk_score=risk_score, prediction=prediction, error=None)

        except ValueError as e:
            return render_template('index.html', error=str(e))

    return render_template('index.html', risk_score=None, prediction=None, error=None)


# Route để đếm số lượng "Không có khả năng thanh toán" và "Có khả năng thanh toán"
@app.route('/prediction-counts', methods=['GET'])
def prediction_counts():
    try:
        # Lấy ngày được chọn từ request
        selected_date = request.args.get('selected_date')

        # Kết nối SQL Server
        conn = connect_to_sql_server()
        if conn:
            cursor = conn.cursor()

            # Nếu người dùng chọn ngày, lọc dữ liệu theo ngày
            if selected_date:
                query = """
                    SELECT Prediction, COUNT(*) 
                    FROM predictions 
                    WHERE CAST(RegistrationDate AS DATE) = ?
                    GROUP BY Prediction
                """
                cursor.execute(query, (selected_date,))
            else:
                # Nếu không có ngày, lấy toàn bộ dữ liệu
                query = """
                    SELECT Prediction, COUNT(*)
                    FROM predictions
                    GROUP BY Prediction
                """
                cursor.execute(query)

            counts = cursor.fetchall()

            # Chuẩn bị dữ liệu
            prediction_data = {
                "Có khả năng thanh toán": 0,
                "Không có khả năng thanh toán": 0
            }

            for prediction, count in counts:
                if prediction == "Có khả năng thanh toán":
                    prediction_data["Có khả năng thanh toán"] = count
                elif prediction == "Không có khả năng thanh toán":
                    prediction_data["Không có khả năng thanh toán"] = count

            cursor.close()
            conn.close()

            return render_template(
                'prediction_counts.html',
                success_count=prediction_data["Có khả năng thanh toán"],
                failure_count=prediction_data["Không có khả năng thanh toán"],
                selected_date=selected_date  # Truyền ngày đã chọn
            )
        else:
            return render_template('prediction_counts.html', error="Không thể kết nối cơ sở dữ liệu!")

    except Exception as e:
        return render_template('prediction_counts.html', error=f"Đã xảy ra lỗi: {e}")

# Route tải lên AWS
@app.route('/upload-to-aws', methods=['POST'])
def upload_to_aws():
    try:
        # AWS S3 client
        s3 = boto3.client('s3', aws_access_key_id='AWS_ACCESS_KEY', aws_secret_access_key='AWS_SECRET_KEY')
        bucket_name = 'your-bucket-name'
        file_name = 'sample_data.csv'

        # Tạo file giả lập
        df = pd.DataFrame({
            "Name": ["Alice", "Bob", "Charlie"],
            "Score": [95, 80, 85]
        })
        file_path = os.path.join(app.root_path, file_name)
        df.to_csv(file_path, index=False)

        # Tải lên S3
        s3.upload_file(file_path, bucket_name, file_name)

        # Xóa file sau khi tải lên
        os.remove(file_path)

        return jsonify({"message": "Dữ liệu đã được tải lên AWS thành công."})
    except Exception as e:
        return jsonify({"message": f"Đã xảy ra lỗi: {str(e)}"}), 500

# Route xuất ra Excel
@app.route('/export-to-excel', methods=['GET'])
def export_to_excel():
    try:
        # Truy xuất dữ liệu từ database
        conn = connect_to_sql_server()
        if conn:
            query = "SELECT * FROM predictions"
            df = pd.read_sql(query, conn)
            conn.close()

            # Tạo file Excel
            file_path = os.path.join(app.root_path, 'predictions.xlsx')
            df.to_excel(file_path, index=False)

            # Trả về file Excel
            return send_from_directory(directory=app.root_path, filename='predictions.xlsx', as_attachment=True)
        else:
            return "Không thể kết nối cơ sở dữ liệu.", 500
    except Exception as e:
        return str(e), 500




if __name__ == '__main__':
    app.run(debug=True)
