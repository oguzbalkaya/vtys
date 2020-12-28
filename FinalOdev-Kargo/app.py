from functools import wraps
from flask import Flask,render_template,flash,redirect,url_for,session,logging,request,send_file
from information import info
from db import *
db.create_all()
app.secret_key = "dbmscargo"

##### Decorators ##

def login_required(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if "logged_in" in session:
            return f(*args,**kwargs)
        else:
            return redirect(url_for("login"))
    return decorated_function
####################
#####  Pages  #####
@app.route("/",methods=["POST","GET"])
def index():
    if request.method=="POST":
        packageId = request.form.get("id")
        package = Packages.query.filter_by(id=packageId).all()
        if len(package)<1:
            flash(message="Yazdığınız teslimat numarasında bir kargo bulunamadı.",category="warning")
            return redirect(url_for("index"))
        return redirect("/detail/{}".format(packageId))
    return render_template("index.html",title="Ana Sayfa",info=info)

@app.route("/login",methods=["POST","GET"])
def login():
    if request.method=="POST":
        id = request.form.get("id")
        password = request.form.get("password")
        employee = Employee.query.filter_by(id=id,password=password).all()
        if(len(employee)==0):
            flash(message="Girdiğiniz bilgilere sahip bir çalışan bulunamadı.",category="warning")
        else:
            employeeinfo = employee[0]
            session["logged_in"] = True
            session["employee_id"] = employeeinfo.id
            session["employee_branch"] = employeeinfo.branch
            branch = Branch.query.filter_by(id=employeeinfo.branch).first()
            session["employee_manager"] = branch.manager
            return redirect(url_for("index"))
    return render_template("login.html",info=info,title="Çalışan Girişi")


@app.route("/detail/<int:id>")
def detail(id):
    packageinfo = Packages.query.filter_by(id=id).all()
    if len(packageinfo)<1:return redirect("/")
    employeeinfo = Employee.query.filter_by(id=packageinfo[0].employee).first()
    takenbranchinfo = Branch.query.filter_by(id=packageinfo[0].takenbranch).first()
    deliverybranchinfo = Branch.query.filter_by(id=packageinfo[0].deliveredbranch).first()
    details = Transportdetails.query.filter_by(package=id).all()
    details=reversed(details)
    return render_template("detail.html",title="Kargo takibi",info=info,package=packageinfo[0],employee=employeeinfo,takenbranch=takenbranchinfo,deliverybranch=deliverybranchinfo,details=details)


@app.route("/mypackages")
@login_required
def mypackages():
    employeeinfo = Employee.query.filter_by(id=session["employee_id"]).first()
    mypackages=Packages.query.filter(Packages.status!="Delivered",Packages.employee==session["employee_id"]).all()
    return render_template("mypackages.html",title="Atanmış paketlerim",info=info,employee=employeeinfo,packages=mypackages)

@app.route("/allpackages")
@login_required
def allpackages():
    if session["employee_id"] != session["employee_manager"]:
        flash(message="Bu kısmı görüntülemek için şube yetkilisi olmalısınız.",category="warning")
        return redirect(url_for("login"))
    else:
        packages = Packages.query.filter_by(status="On The Destination",deliveredbranch=session["employee_branch"]).all()
        brach = Branch.query.filter_by(id=session["employee_branch"]).first()
    return render_template("allpackages.html",title="Şubede atama bekleyen tüm paketler",info=info,packages=packages,branch=brach)
@app.route("/package/<int:id>",methods=["POST","GET"])
@login_required
def package(id):
    package = Packages.query.filter_by(id=id).all()
    if len(package)==0 or package[0].employee!=session["employee_id"] or package[0].status=="Delivered":
        return redirect("/mypackages")
    if request.method=="POST":
        statuspackage=package[0].status
        status = request.form.get("status")
        deliveredto = request.form.get("deliveredto")
        if status=="Delivered":
            flash(message="Paketin durumu güncellendi.",category="success")
            package[0].status="Delivered"
            db.session.add(Transportdetails(explanation="Paket {} adlı kişiye teslim edildi.".format(deliveredto),status="delivered",package=package[0].id))
            db.session.commit()
            return redirect(url_for("mypackages"))
        elif status=="On The Way" and statuspackage!="On The Way":
            flash(message="Paketin durumu güncellendi.",category="success")
            package[0].status="On The Way"
            db.session.add(Transportdetails(explanation="Paket yola çıkarıldı.",status=" ",package=package[0].id))
            db.session.commit()
        elif status=="On The Destination" and statuspackage!="On The Destination":
            flash(message="Paketin durumu güncellendi.",category="success")
            package[0].status="On The Destination"
            db.session.add(Transportdetails(explanation="Paket varış şubesine ulaştı.",status="ondestination",package=package[0].id))
            db.session.commit()

    return render_template("package.html",title="{} nolu paket için işlem yapılıyor.".format(id),info=info,package=package[0])

@app.route("/m_package/<int:id>",methods=["POST","GET"])
@login_required
def m_package(id):
    if session["employee_id"] != session["employee_manager"]:
        flash(message="Bu kısmı görüntülemek için şube yetkilisi olmalısınız.",category="warning")
        return redirect(url_for("login"))
    package = Packages.query.filter_by(id=id).all()
    employees = Employee.query.filter_by(branch=session["employee_branch"]).all()
    if len(package)==0:
        return redirect("/allpackages")
    if request.method=="POST":
        emp = request.form.get("employee")
        if package[0].employee != emp:
            package[0].employee=emp
            package[0].status="Distribution"
            db.session.add(Transportdetails(explanation="Paket dağıtıma çıktı.",status=" ",package=package[0].id))
            db.session.commit()
            flash(message="Çalışan ataması yapıldı.Paket dağıtıma gönderildi.",category="success")
            return redirect(url_for("allpackages"))

    return render_template("m_package.html",title="{} nolu paket için işlem yapılıyor.".format(id),info=info,package=package[0],employees=employees)

@app.route("/delete/<int:id>")
def delete(id):
    package = Packages.query.filter_by(id=id,employee=session["employee_id"]).first()
    if package != None:
        flash(message="Paket silindi.",category="success")
        db.session.delete(package)
        db.session.commit()
        return redirect(url_for("mypackages"))
    else:
        flash(message="Paket yok yada size zimmetli değil.",category="success")
        return redirect(url_for("mypackages"))

@app.route("/newpackage",methods=["POST","GET"])
@login_required
def newpackage():
    branches = Branch.query.filter(Branch.id != session["employee_branch"]).all()
    if request.method=="POST":
        name = request.form.get("customername")
        address = request.form.get("address")
        price = request.form.get("price")
        weight = request.form.get("weight")
        deliveredbranch = request.form.get("branch")
        pack = Packages(customername=name,address=address,price=price,weight=weight,deliveredbranch=deliveredbranch,status="Accepted",delivered_to=" ",delivered_date=" ",employee=1,takenbranch=session["employee_branch"])
        db.session.add(pack)
        db.session.commit()
        db.session.add(Transportdetails(explanation="Paket kabul edildi.", status=" ", package=pack.id))
        db.session.commit()
        flash(message="Paket kabul edildi.",category="success")


        redirect(url_for("newpackage"))
    return render_template("newpackage.html",title="Yeni paket kabulü",info=info,branches=branches)

@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("index"))

##################



if __name__ == '__main__':
    app.run()
