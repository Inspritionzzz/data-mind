from flask import Flask
app = Flask(__name__)

# 路由装饰器
@app.route("/")
def f2():
    return "welcome to flask"

app.run(debug = True)