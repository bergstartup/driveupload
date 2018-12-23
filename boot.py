from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import random
from werkzeug import secure_filename
import os
import main


app=Flask(__name__)
@app.route("/")
def start():
     return redirect(url_for('login',msg=" "))

@app.route("/login/<msg>")
def login(msg=" "):
     global lcode
     lcode=str(random.randint(1,1000))
     return render_template("login.html",msg=msg)

@app.route('/log',methods=['POST'])
def log():
     if request.form['user']=="admin" and request.form["pas"]=="1234":
          global lcode
          lcode=str(random.randint(1,1000))
          return redirect(url_for('home',msg=" ",lc=lcode))
     elif request.form['user']=="root" and request.form["pas"]=="9842":
          global lcode
          lcode=str(random.randint(1,1000))
          return redirect(url_for('sqlpg',lc=lcode))
     else:
          return redirect(url_for('login',msg="Username and password mismatch"))


@app.route("/<name>")
def page(name):
     try :
          return render_template(name)
     except:
          return render_template("404.html")
@app.route("/ledger/<msg>/<lc>")
def home(msg,lc):
     if(lc==lcode):
          with sqlite3.connect("ledger.db") as con:
               cur1=con.cursor()
               cur1.execute("SELECT * from files")
               cur2=con.cursor()
               cur2.execute("SELECT max(date) from files")
               for i in cur2:
                    dt=i[0]
               if msg==" ":
                    msg="last update : {}".format(dt)
          return render_template("ledger.html",msg=msg,data=cur1)
     else:
          return redirect(url_for('login',msg="Access Denied"))

@app.route("/logout",methods=['POST','GET'])
def logout():
     return redirect(url_for('login',msg="LOGOUT SUCCESSFULLY"))
     
@app.route('/search',methods = ['POST', 'GET'])
def search():
     tag=request.form['tag']
     with sqlite3.connect("ledger.db") as con:
          cur = con.cursor()
          code="SELECT * from files WHERE tag LIKE '{}'".format(tag)
          cur.execute(code)
          k=cur
          c=0
          data=list()
          for i in k:
             c+=1
             data.append(i)
          msg="{} Record are found".format(c)
          return render_template("ledger.html",msg=msg,data=data,lcode=lcode)
     return redirect(url_for('login',msg="Can't connenct server"))
          
@app.route('/addrec',methods = ['POST', 'GET'])
def addrec():
   msg=" "
   if request.method == 'POST':
     #sno = int(request.form['sno'])
     tag = request.form['tag']
     f = request.files['file']
     f.save(secure_filename(f.filename))
     tpe=str()
     ext=f.filename.split('.')[1]
     if ext in ["csv"]:
          tpe="text/{}".format(ext)
     elif ext in ["docs","docx","doc","pdf"]:
          tpe="text/docs"
     elif ext in ["jpg","jpeg","png"]:
          tpe="image/{}".format(ext)
     main.uploadFile(f.filename,f.filename,tpe)
     with sqlite3.connect("ledger.db") as con:
          cur = con.cursor()
          try:
               cur.execute("INSERT INTO files (tag,date,file) VALUES (?,date('now'),?)",(tag,f.filename) )
               con.commit()
               msg = "RECORD ADDED"
          except:
               msg="NOT ADDED"
     os.remove(f.filename)
   return redirect(url_for('home',msg=msg,lc=lcode))


@app.route("/sqlpg.html/<lc>")
def sqlpg(lc):
     if lc==lcode:
          return render_template("sqlpg.html",msg="Enter command to execute",data=" ")
     else:
          return redirect(url_for('login',msg="Access Denied"))
@app.route('/sqlcmd',methods = ['POST', 'GET'])
def sqlcmd():
     cmd=request.form['cmd']
     with sqlite3.connect("ledger.db") as con:
          cur = con.cursor()
          try:
               cur.execute(cmd)
               con.commit()
               msg="Cmd executed"
          except:
               msg="Error in cmd"
          return render_template("sqlpg.html",msg=msg,data=cur) 

if __name__=='__main__':
     app.run(debug=True)
