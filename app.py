from flask import Flask,request,render_template
import sqlite3
import datetime
import google.generativeai as genai
import os
import wikipedia
import time,requests

api = os.getenv("makersuite")
model = genai.GenerativeModel("gemini-1.5-flash")
genai.configure(api_key=api)

telegram_api= os.getenv("telegram")
url = f"https://api.telegram.org/bot{telegram_api}/"

app = Flask(__name__)

flag = 1


@app.route("/",methods=["POST","GET"])
def index():
    return(render_template("index.html"))

@app.route("/main",methods=["POST","GET"])
def main():
    global flag
    if flag == 1:
        t = datetime.datetime.now()
        user_name = request.form.get("q")
        conn = sqlite3.connect('user.db')
        c = conn.cursor()
        c.execute("insert into user (name, timestamp) values (?,?)", (user_name,t))
        conn.commit()
        c.close()
        conn.close
        flag = 0

    return(render_template("main.html"))

@app.route("/foodexp",methods=["POST","GET"])
def foodexp():
    return(render_template("foodexp.html"))

@app.route("/foodexp1",methods=["POST","GET"])
def foodexp1():
    return(render_template("foodexp1.html"))

@app.route("/foodexp2",methods=["POST","GET"])
def foodexp2():
    return(render_template("foodexp2.html"))

@app.route("/foodexp_pred",methods=["POST","GET"])
def foodexp_pred():
    q = float(request.form.get("q"))
    return(render_template("foodexp_pred.html",r=(q*0.4851)+147.4))

@app.route("/ethical_test",methods=["POST","GET"])
def ethical_test():
    return(render_template("ethical_test.html"))

@app.route("/test_result",methods=["POST","GET"])
def test_result():
    answer = request.form.get("answer")
    if answer=="false":
        return(render_template("pass.html"))
    if answer=="true":
        return(render_template("fail.html"))
    
@app.route("/FAQ",methods=["POST","GET"])
def FAQ():
    return(render_template("FAQ.html"))

@app.route("/FAQ1",methods=["POST","GET"])
def FAQ1():
    r = model.generate_content("Factors for Profit")
    return(render_template("FAQ1.html",r=r.candidates[0].content.parts[0]))

@app.route("/FAQinput",methods=["POST","GET"])
def FAQinput():
    q = request.form.get("q")
    r = wikipedia.summary(q)
    return(render_template("FAQinput.html",r=r))

@app.route("/Portfolio",methods=["POST","GET"])
def Portfolio():
    return(render_template("Portfolio.html"))

@app.route("/Portfolio_result",methods=["POST","GET"])
def Portfolio_result():
    q = request.form.get('question')
    print(q)
    r = model.generate_content(q)
    return(render_template("Portfolio_result.html",r=r.candidates[0].content.parts[0]))

@app.route("/telegram",methods=["POST","GET"])
def telegram():
    updates = url+"getUpdates"
    r = requests.get(updates)
    r = r.json()
    chat = r["result"][-1]["message"]["chat"]["id"]
    flag_2 = ""
    prompt = "Welcome to prediction, Please enter the inflation rate in %: (type exit to break)"
    err_msg = "Please enter a number"
    while True:
        msg = url + f"sendMessage?chat_id={chat}&text={prompt}"
        requests.get(msg)
        time.sleep(5)
        r = requests.get(updates)
        r = r.json()
        r = r["result"][-1]["message"]["text"]
        print(r)
        if flag_2 != r:
            flag_2 = r
            if r.isnumeric():
                r = "The predicted interest rate is " + str(float(r)+1.5)
                msg = url + f"sendMessage?chat_id={chat}&text={r}"
                requests.get(msg)
            else:
                if r == "exit":
                    break
                else:
                    msg = url + f"sendMessage?chat_id={chat}&text={err_msg}"
                    requests.get(msg)
        time.sleep(8)
    return(render_template("main.html"))
 
@app.route("/userLog",methods=["POST","GET"])
def userLog():
    conn = sqlite3.connect('user.db')
    c = conn.cursor()
    c.execute("select * from user")
    r = ""
    for row in c:
        r = r + str(row) + "\n"
    print(r)
    c.close()
    conn.close
    return(render_template("userLog.html",r=r))

@app.route("/deleteLog",methods=["POST","GET"])
def deleteLog():
    conn = sqlite3.connect('user.db')
    c = conn.cursor()
    c.execute("delete from user")
    conn.commit()
    c.close()
    conn.close
    return (render_template("deleteLog.html"))

if __name__ == "__main__":
    app.run()