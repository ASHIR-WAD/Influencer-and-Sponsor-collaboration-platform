from flask import Flask ,render_template, redirect,request,session,abort ,jsonify,url_for
from models import *
import matplotlib.pyplot as plt
from flask import send_file
import matplotlib
import base64
from io import BytesIO
matplotlib.use('Agg')

app = Flask(__name__)

app.secret_key='login'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'

db.init_app(app)
app.app_context().push()

#-------------home page----------------------

@app.route('/')
def home():
    return render_template("index.html")

#-----------registraion----------------

@app.route('/influencer_regis')
def i_regis():
    return render_template("influencer_regis.html")

@app.route('/sponsor_regis')
def s_regis():
    return render_template("sponsor_regis.html")


@app.route('/i_regis',methods=['POST','GET'])       #influencer data to database
def influ_regis():
    if (request.form['psw']==request.form['repsw']):
        name=request.form['namee']
        username=request.form['username']
        email=request.form['email']
        psw=request.form['psw']
        number=request.form['number']
        social=request.form['social']
        followers=request.form['followers']
        i1=Influencer(iname=name,usename=username,email=email,password=psw,platform=social,number=number,reach=followers,flag=False)
        db.session.add(i1)
        db.session.commit()
        #print('success')
        return redirect('login')
    else:
        return 'confirmation passwords does not match'

@app.route('/s_regis',methods=['POST','GET'])       #sponsor data to database
def spnsr_regis():
    if (request.form['psw']==request.form['repsw']):
        name=request.form['namee']
        username=request.form['uname']
        email=request.form['email']
        psw=request.form['psw']
        number=request.form['number']
        industry=request.form['industry']
        s1=Sponsor(sname =name,usename =username,email =email,password =psw,industry =industry,number =number,flag =False)
        db.session.add(s1)
        db.session.commit()
        print('success')
        return redirect("login")
    else:
        return 'confirmation passwords does not match'

#-------------------general login------------


@app.route('/login')
def genlogin():
    return render_template("general_login.html")


@app.route('/log',methods=['GET','POST'])       #login data
def logdata():
    uname=request.form['uname']
    psw=request.form['psw']
    print(uname,psw)
    
    if Influencer.query.filter_by(usename=uname,password=psw).first():
        session['username']=uname
        return redirect('imain')
    elif Sponsor.query.filter_by(usename=uname,password=psw).first():
        session['username']=uname
        return redirect('smain')
    else:
        return abort(401)
    #return "<0 0> i have to work here"


#----------------------influencer------------

@app.route('/imain')
def imain():
    if 'username' in session:
        data=Influencer.query.filter_by(usename=session['username']).first()
        print(data,data.usename )
        uname=session['username']
        req=Requests.query.filter_by(icheck='requested',iname=data.iname)
        camp=Campaign.query.filter_by(iname=data.iname)
        requested = Requests.query.filter_by(icheck='negotiated',iname=data.iname).all()
        print(requested )
        request_campaigns = []
        for r in req:
            campaign = Campaign.query.get(r.campaign_id)
            request_campaigns.append({
                'request': r,
                'campaign': campaign
            })
        return render_template('influencer_main.html',user=data,camp=camp,request=req,requested=requested,request_campaigns=request_campaigns)
    else :
        return redirect('login')

@app.route('/ifind')
def ifind():
    if 'username' in session:
        user=Influencer.query.filter_by(usename=session['username']).first()
        camp=Campaign.query.filter_by(public=1,flag=0)
        return  render_template("influencer_find.html",user=user,camp=camp)
    else:
        return redirect('/')
    
@app.route('/iupdate')
def iupdate():
    if 'username' in session:
        user=Influencer.query.filter_by(usename=session['username']).first()
        return  render_template("iupdate.html",user=user)
    else:
        return redirect('/')


@app.route('/updateprofile',methods=['POST','GET'])
def updateprofile():
    if 'username' in session:
        user=Influencer.query.filter_by(usename=session['username']).first()
        if request.form['namee']:
            user.iname = request.form['namee']
        if request.form['email']:
            user.email = request.form['email']
        if request.form['number']:
            user.number = request.form['number']
        if request.form['social']:
            user.platform = request.form['social']
        if request.form['followers']:
            user.reach = request.form['followers']
        psw = request.form['psw']
        repsw = request.form['repsw']
        if psw and repsw:
            if psw == repsw:
                user.password = psw
        db.session.add(user)
        db.session.commit()
        return  redirect('/imain')
    else:
        return redirect('/')
    
    
@app.route('/negotiate',methods=['GET','POST'])
def negotiate():
    if 'username' in session:
        user=Influencer.query.filter_by(usename=session['username']).first()
        msg=request.form['message']
        rid=request.form['request_id']
        req=Requests.query.filter_by(reqid=rid).first()
        req.msg=msg
        req.icheck='negotiaton'
        db.session.add(req)
        db.session.commit()
        return  redirect('/imain')
    else:
        return redirect('/')

#-------------------sponsor---------------
@app.route('/smain')
def smain():
    if 'username' in session:
        name=session['username']
        user=Sponsor.query.filter_by(usename=name).first()
        activecamp = Campaign.query.filter_by(sname=user.usename).filter(Campaign.iname != '').all()
        value='requested'
        requ=Requests.query.filter_by(scheck=value,sname=user.usename).all()
        requested = Requests.query.filter_by(icheck='negotiaton',sname=user.usename).all()
        request_data = []
        for req in requ:
            influencer = Influencer.query.filter_by(iname=req.iname).first()
            camp=Campaign.query.filter_by(campaignid=req.campaign_id).first()
            print(influencer,camp)
            request_data.append({
                'reqid': req.reqid,
                'iname': influencer.iname,
                'cname': camp.cname,
                'campaign_id': req.campaign_id,
                'budget': camp.budget,
                'desc': camp.desc,
                'startdate': camp.startdate,
                'enddate': camp.enddate,
                'job': camp.job
            })
        return render_template('sponsor_main.html',user=user,activecamp=activecamp,requested=requested,request=request_data)
    else : 
        return redirect('/')
    
    
@app.route('/sfind')
def sfind():
    if 'username' in session:
        influ=Influencer.query.filter_by(flag=0).all()
        user=Sponsor.query.filter_by(usename=session['username']).first()
        return  render_template("sponsor_find.html",influ=influ,user=user)
    else:
        return redirect('/')


@app.route('/sfind2')
def sfind2():
    if 'username' in session:
        influ=Influencer.query.filter_by(flag=0).all()
        user=Sponsor.query.filter_by(usename=session['username']).first()
        return  render_template("campaignfind.html",influ=influ,user=user)
    else:
        return redirect('/')


@app.route('/delreq', methods=['POST'])
def delreq():
    if 'username' in session:
        reqid = request.form['delete']
        r = Requests.query.filter_by(reqid=reqid).first()
        if r:
            db.session.delete(r)
            db.session.commit()
        return redirect('/smain')
    else:
        return redirect('/')
    

@app.route('/modrequest', methods=['POST'])
def modifyrequest():
    if 'username' in session:
        desc = request.form['desc']
        budget = request.form['budget']
        reqid = request.form['reqid']
        r = Requests.query.filter_by(reqid=reqid).first()
        print(desc)
        if r:
            camp=Campaign.query.filter_by(campaignid=r.campaign_id).first()
            if desc:
                camp.desc=desc
                db.session.add(camp)
                db.session.commit()
                r.icheck='negotiated'
                db.session.add(r)
                db.session.commit()
            if budget:
                camp.budget=budget
                db.session.add(camp)
                db.session.commit()
                r.amount=budget
                r.icheck='negotiated'
                db.session.add(r)
                db.session.commit()
        return redirect('/smain')
    else:
        return redirect('/')


#-----------logout---------------

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


#--------------admin---------------

@app.route('/admin')
def admin():
    return render_template("admin_login.html")


@app.route('/adminlog',methods=['GET','POST'])
def adminlogin():
    uname=request.form['uname']
    psw=request.form['psw']
    print(uname,psw)
    if (uname=='ashirwad' and psw=='9430855605'):
        session['username']=uname
        return redirect('adminhome')
    else:
        # '''You are not admin.Please login into influencer or sponsor page'''
        #401- is for unauth access
        return abort(401)

@app.route('/adminhome')
def adminhome():
    if 'username' in session:
        camp=Campaign.query.all()
        iflag=Influencer.query.filter_by(flag=1)
        sflag=Sponsor.query.filter_by(flag=1)
        cflag=Campaign.query.filter_by(flag=1)
        return render_template("admin_main.html",camp=camp,iflag=iflag,sflag=sflag,cflag=cflag)
    else:
        return redirect('/admin')


@app.route('/adminfind')
def adminfind():
    if 'username' in session:
        spon=Sponsor.query.all()
        influ=Influencer.query.all()
        camp=Campaign.query.all()
        return  render_template("admin_find.html",influ=influ,camp=camp,spon=spon)
    else:
        return redirect('/admin')


#-------------------------flag------------------------------
@app.route('/flag',methods=['GET','POST'])
def flag():
    if 'username' in session:
        data=list(request.form['flagvalue'].split(','))
        flagvalue=data[0]
        uname=data[1]
        if Influencer.query.filter_by(usename=uname).first():
            i=Influencer.query.filter_by(usename=uname).first()
            i.flag=flagvalue
            db.session.commit()
            print('success')
        elif Sponsor.query.filter_by(usename=uname).first():
            s=Sponsor.query.filter_by(usename=uname).first()
            s.flag=flagvalue
            db.session.commit()
            print('success')
        else :
            c=Campaign.query.filter_by(campaignid=uname).first()
            c.flag=flagvalue
            db.session.commit()
            print('success')
        
        
        return redirect('/adminhome')
    else:
        return redirect('/admin')
    
@app.route('/flagfind',methods=['GET','POST'])
def flagfind():
    if 'username' in session:
        data=list(request.form['flagvalue'].split(','))
        flagvalue=data[0]
        uname=data[1]
        if Influencer.query.filter_by(usename=uname).first():
            i=Influencer.query.filter_by(usename=uname).first()
            i.flag=flagvalue
            db.session.commit()
            print('success')
        elif Sponsor.query.filter_by(usename=uname).first():
            s=Sponsor.query.filter_by(usename=uname).first()
            s.flag=flagvalue
            db.session.commit()
            print('success')
        else :
            c=Campaign.query.filter_by(campaignid=uname).first()
            c.flag=flagvalue
            db.session.commit()
            print('success')
        
        #print(flagvalue,data)
        
        return redirect('/adminfind')
    else:
        return redirect('/admin')

#--------------------campaign------------------------
@app.route('/addcampaign')
def addcamp():
    return render_template("campaign_form.html")

@app.route('/campaign')
def camp():
    if 'username' in session:
        name=session['username']
        user=Sponsor.query.filter_by(usename=name).first()
        camp=Campaign.query.filter_by(sname=user.usename)
        print(session['username'])
        print(user.usename,camp)
        return render_template("campaign.html",user=user,camp=camp)
    else:
        return redirect('/')


@app.route('/campdata',methods=['POST','GET'])       #influencer data to database
def camp_data():
    if 'username' in session:
        if session['username']==request.form['sname']:
            cname=request.form['cname']
            budget=request.form['budget']
            desc=request.form['desc']
            job=request.form['job']
            sname=request.form['sname']
            startdate=request.form['startdate']
            enddate=request.form['enddate']
            public=request.form['state']
            c1=Campaign(sname=sname,cname=cname,budget=budget,desc=desc,startdate=startdate,enddate=enddate,public=public,job=job,flag=False)
            db.session.add(c1)
            db.session.commit()
            #print(cname,budget,desc,job,sname,startdate,enddate,public)
            print('success')
            return redirect('/campaign')
        else:
            return "Enter correct sponsor name"
    else:
        return redirect('/')

@app.route('/cupdate',methods=['POST','GET'])
def cupdate():
    if 'username' in session:
        cid=request.form['update']
        #user=Sponsor.query.filter_by(usename=session['username']).first()
        return  render_template("campupdate.html",cid=cid)
    else:
        return redirect('/')

@app.route('/updatecampaign',methods=['POST','GET'])
def updatecampaign():
    if 'username' in session:
        if request.form['cdata']:
            cid=request.form['cdata']
            #user=Sponsor.query.filter_by(usename=session['username']).first()
            camp=Campaign.query.filter_by(campaignid=cid).first()
            
            if request.form['cname']:
                camp.cname = request.form['cname']
            if request.form['budget']:
                camp.budget = request.form['budget']
            if request.form['desc']:
                camp.desc = request.form['desc']
            if request.form['job']:
                camp.job = request.form['job']
            if request.form['startdate']:
                camp.startdate = request.form['startdate']
            if request.form['enddate']:
                camp.enddate = request.form['enddate']    
            if request.form['state']:
                camp.public = request.form['state']
            db.session.add(camp)
            db.session.commit()
        return  redirect('/campaign')
    else:
        return redirect('/')

@app.route('/campdelete',methods=['POST','GET'])
def campdelete():
    if 'username' in session:
        cid=request.form['delete']
        camp=Campaign.query.filter_by(campaignid=cid).first()
        db.session.delete(camp)
        db.session.commit()
        return  redirect('/campaign')
    else:
        return redirect('/')


#............................requests............................

@app.route('/request',methods=['GET','POST'])
def requests():
    if 'username' in session:
        data=list(request.form['status'].split(','))
        value=data[0]
        userid=data[1]
        cid=data[2]
        who=data[3]
        if who=='i':
            iname=Influencer.query.filter_by(inid=userid).first()
            cdata=Campaign.query.filter_by(campaignid=cid).first()
            r=Requests(sname=cdata.sname,iname=iname.iname,campaign_id=cid,cname=cdata.cname,scheck=value,amount=cdata.budget)
            db.session.add(r)
            db.session.commit()
            print("success",r)        
        return redirect('/ifind')
    else:
        return redirect('/')

#======================req updates==========================

@app.route('/requestupdate',methods=['GET','POST'])
def requestupdate():
    if 'username' in session:
        data=list(request.form['status'].split(','))
        value=data[0]
        userid=data[1]
        rid=data[2]
        who=data[3]
        print(data,'success')
        if who=='i':
            i=Influencer.query.filter_by(inid=userid).first()
            r=Requests.query.filter_by(reqid=rid).first()
            print(r)
            r.icheck=value
            r.scheck=value
            r.msg=value
            db.session.add(r)
            db.session.commit()
            print("success",r)
            if value=='accepted':
                camp=Campaign.query.filter_by(campaignid=r.campaign_id).first()
                camp.iname=i.iname
                db.session.add(camp)
                db.session.commit()
            return redirect('/imain')
        elif who=='s':
            r=Requests.query.filter_by(reqid=rid).first()
            print(r)
            r.icheck=value
            r.scheck=value
            r.msg=value
            db.session.add(r)
            db.session.commit()
            print("success",r)
            if value=='accepted':   
                camp=Campaign.query.filter_by(campaignid=r.campaign_id).first()
                camp.iname=r.iname
                db.session.add(camp)
                db.session.commit()
            return redirect('/smain')
        else:
            return "some error occoured"
    else:
        return redirect('/')

#-----------------sponsor requests------------------

@app.route('/request_influencer', methods=['POST'])
def request_influencer():
    data = request.get_json()
    if not data:
        return abort(400, 'Invalid input')

    inid = data.get('inid')
    sid = data.get('sid')
    
    if not inid or not sid:
        return abort(400, 'Missing inid or sid')

    session["inid"] = inid
    session["sid"] = sid
    print("success", session["inid"], session["sid"])
    
    return redirect('/requestsponsor')

@app.route('/add_campaign', methods=['POST'])
def add_campaign():
    data = request.get_json()
    if not data:
        return abort(400, 'Invalid input')
    
    cid = data.get('cid')
    sid = data.get('sid')
    
    if not cid or not sid:
        return abort(400, 'Missing inid or sid')
    session["cid"] = cid
    session["sid"] = sid
    
    if "sid" in session :
        print("success", session["cid"], session["sid"])
        return jsonify({"status": "success"}), 200
    else:
        return abort(400, 'Session does not have sid')

@app.route('/requestsponsor')
def requestsponsor():
    if "inid" not in session or "cid" not in session:
        return abort(400, 'Missing session data')

    i = Influencer.query.filter_by(inid=session['inid']).first()
    c = Campaign.query.filter_by(campaignid=session['cid']).first()

    if not i or not c:
        return abort(404, 'Influencer or Campaign not found')

    r = Requests(sname=c.sname, iname=i.iname, campaign_id=c.campaignid, icheck='requested', amount=c.budget, cname=c.cname)
    db.session.add(r)
    db.session.commit()
    print('success')
    return jsonify({"status": "success"}), 200 


#--------------------search bar --------------- ----------------------------------
@app.route('/search_influencer', methods=['GET'])
def search_influencer():
    if 'username' in session:
        user=Sponsor.query.filter_by(usename=session['username']).first()
        query = request.args.get('query')
        if query:
            influencer=[]
            influencer += Influencer.query.filter(Influencer.iname.contains(query)).all()
            influencer += Influencer.query.filter(Influencer.platform.contains(query)).all()
            influencer += Influencer.query.filter(Influencer.reach.contains(query)).all()
        else:
            influencer = []

        return render_template('sponsorsearch.html', influencers=influencer,user=user)
    else:
        return redirect('/')
    
@app.route('/search_sponsor', methods=['GET'])
def search_sponsor():
    if 'username' in session:
        user=Influencer.query.filter_by(usename=session['username']).first()
        query = request.args.get('query')
        if query:
            sponsor=[]
            sponsor += Sponsor.query.filter(Sponsor.sname.contains(query)).all()
            sponsor += Sponsor.query.filter(Sponsor.industry.contains(query)).all()
            campaign=[]
            campaign+=Campaign.query.filter(Campaign.cname.contains(query)).all()
            campaign+=Campaign.query.filter(Campaign.sname.contains(query)).all()
            campaign+=Campaign.query.filter(Campaign.budget.contains(query)).all()
            campaign+=Campaign.query.filter(Campaign.job.contains(query)).all()
        else:
            sponsor = []
            campaign=[]

        return render_template('influencersearch.html', sponsors=sponsor,user=user,campaigns=campaign)
    else:
        return redirect('/')


@app.route('/search_admin', methods=['GET'])
def search_admin():
    if 'username' in session:
        query = request.args.get('query')
        if query:
            sponsor=[]
            sponsor += Sponsor.query.filter(Sponsor.sname.contains(query)).all()
            sponsor += Sponsor.query.filter(Sponsor.industry.contains(query)).all()
            campaign=[]
            campaign+=Campaign.query.filter(Campaign.cname.contains(query)).all()
            campaign+=Campaign.query.filter(Campaign.sname.contains(query)).all()
            campaign+=Campaign.query.filter(Campaign.budget.contains(query)).all()
            campaign+=Campaign.query.filter(Campaign.job.contains(query)).all()
            influencer=[]
            influencer += Influencer.query.filter(Influencer.iname.contains(query)).all()
            influencer += Influencer.query.filter(Influencer.platform.contains(query)).all()
            influencer += Influencer.query.filter(Influencer.reach.contains(query)).all()
        else:
            sponsor = []
            campaign=[]
            influencer=[]


        return render_template('adminsearch.html', sponsors=sponsor,influencers=influencer,campaigns=campaign)
    else:
        return redirect('/')

#----------------------------stats----------------------------------------------


def create_histogram(data, title, xlabel, ylabel, color):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.hist(data, bins=20, color=color, edgecolor='black', rwidth=0.4)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close(fig)
    return img

def create_bar_plot(categories, values, title, ylabel, colors):
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar(categories, values, color=colors, width=0.4)
    ax.set_title(title)
    ax.set_ylabel(ylabel)

    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close(fig)
    return img

def create_bar_plot_rotated(categories, values, title, ylabel, colors):
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.bar(categories, values, color=colors)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xticklabels(categories, rotation=15, ha='right')

    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close(fig)
    return img

@app.route('/adminstatistics', methods=['GET', 'POST'])
def adminstats():
    if 'username' in session:
        platforms = db.session.query(Influencer.platform, db.func.count(Influencer.inid)).group_by(Influencer.platform).all()
        flagged_influencers = Influencer.query.filter_by(flag=1).count()
        unflagged_influencers = Influencer.query.filter_by(flag=0).count()
        flagged_sponsors = Sponsor.query.filter_by(flag=1).count()
        unflagged_sponsors = Sponsor.query.filter_by(flag=0).count()
        flagged_campaigns = Campaign.query.filter_by(flag=1).count()
        unflagged_campaigns = Campaign.query.filter_by(flag=0).count()
        total_campaigns = Campaign.query.count()
        total_sponsors = Sponsor.query.count()
        total_influencers = Influencer.query.count()
        campaigns = Campaign.query.all()
        budget_data = [c.budget for c in campaigns]
        influencers = Influencer.query.all()
        reach_data = [i.reach for i in influencers]

        img1 = create_bar_plot([p[0] for p in platforms], [p[1] for p in platforms], 'Number of Influencers by Platform', 'Count', ['purple', 'blue', 'red'])
        img2 = create_bar_plot_rotated(
            ['Flagged Influencers', 'Unflagged Influencers', 'Flagged Sponsors', 'Unflagged Sponsors', 'Flagged Campaigns', 'Unflagged Campaigns'],
            [flagged_influencers, unflagged_influencers, flagged_sponsors, unflagged_sponsors, flagged_campaigns, unflagged_campaigns],
            'Flagged & Unflagged: Users and Campaigns', 'Count', ['red', 'blue', 'orange', 'green', 'purple', 'cyan'])
        img3 = create_bar_plot(
            ['Total Campaigns', 'Total Sponsors', 'Total Influencers'], 
            [total_campaigns, total_sponsors, total_influencers], 
            'Total Campaigns, Sponsors, and Influencers', 'Count', ['blue', 'green', 'orange'])
        img4 = create_histogram(budget_data, 'Histogram of Budget', 'Budget', 'Frequency', 'green')
        img5 = create_histogram(reach_data, 'Histogram of Reach', 'Reach', 'Frequency', 'blue')

        img1_b64 = base64.b64encode(img1.getvalue()).decode('utf-8')
        img2_b64 = base64.b64encode(img2.getvalue()).decode('utf-8')
        img3_b64 = base64.b64encode(img3.getvalue()).decode('utf-8')
        img4_b64 = base64.b64encode(img4.getvalue()).decode('utf-8')
        img5_b64 = base64.b64encode(img5.getvalue()).decode('utf-8')

        return render_template('admin_stats.html', img1=img1_b64, img2=img2_b64, img3=img3_b64, img4=img4_b64, img5=img5_b64)
    else:
        return redirect('/')



#--------------------------------------------------------------------------


if __name__=="__main__":
    app.run(debug=True ,port=8000)