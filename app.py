from flask import Flask,request,render_template
import sqlite3
import datetime
import google.generativeai as genai
import os
import wikipedia
import time,requests
import re

#api = os.getenv("makersuite")
api = "AIzaSyADcro7sO2hb4GjMhEPKNtwQssUVvQOM0U"
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

@app.route("/smart_budget", methods=["GET", "POST"])
def smart_budget():
    ai_response = ""
    warning = ""
    chart_data = {}
    avg_saving_note = ""

    if request.method == "POST":
        income_raw = request.form.get("income", "")
        expenses_raw = request.form.get("expenses", "")
        savings = float(request.form.get("savings", 0))

        try:
            income_list = [float(x.strip()) for x in income_raw.split(",") if x.strip()]
            expenses = [float(x.strip()) for x in expenses_raw.split(",") if x.strip()]
        except ValueError:
            return "Please enter only numbers separated by commas."

        if len(income_list) != len(expenses):
            return "Please make sure income and expenses have the same number of months."

        if len(expenses) >= 2:
            expense_increase = expenses[-1] - expenses[0]
            income_increase = income_list[-1] - income_list[0]
            if expense_increase > income_increase * 1.2:
                warning = "⚠️ Your expenses are growing significantly faster than your income."

        actual_saving = [inc - exp for inc, exp in zip(income_list, expenses)]
        avg_actual = sum(actual_saving) / len(actual_saving)

        if avg_actual < savings:
            avg_saving_note = f"<span style='color:red;'>⚠️ Your average saving (${avg_actual:.2f}) is below your goal (${savings:.2f}).</span>"
        else:
            avg_saving_note = f"<span style='color:green;'>✅ Great! Your average saving (${avg_actual:.2f}) meets or exceeds your goal (${savings:.2f}).</span>"

        prompt = f"""
        Here is my financial summary over the past {len(expenses)} months:
        Monthly income: {income_list}
        Monthly expenses: {expenses}
        My monthly savings goal is ${savings}.

        Analyze my financial trends and give detailed advice on budgeting, saving, and avoiding financial risks.
        """

        response = model.generate_content(prompt)
        ai_response = response.text

        chart_data = {
            "income": income_list,
            "expenses": expenses,
            "target_saving": savings
        }

    return render_template("smart_budget.html", ai_response=ai_response,
                           warning=warning, chart_data=chart_data,
                           avg_saving_note=avg_saving_note)
 
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