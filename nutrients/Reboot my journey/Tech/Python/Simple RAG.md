1. Tạo python virtual environment
```bash
# Tạo virtual environment
python3 -m venv .venv

# Kích hoạt virtual environment
source .venv/bin/activate

# Cập nhật pip và cài đặt các gói cần thiết
pip install --upgrade pip

pip install langchain langchain-community fastapi uvicorn
```

2. Tạo tệp requirements.txt ghi lại các package đã dùng
```
pip freeze > requirements.txt
```

3. Update VS Code interpreter
- Press Cmd+Shift+P (Mac)
- Type "Python: Select Interpreter"
- Choose the interpreter from your new .venv directory = `which python` 
