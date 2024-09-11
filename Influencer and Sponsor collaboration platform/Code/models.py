from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Influencer(db.Model):
    __tablename__ = 'influencer'
    inid=db.Column(db.Integer,primary_key=True)
    iname = db.Column(db.String, nullable=False)
    usename = db.Column(db.String, unique=True)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    platform = db.Column(db.String, nullable=False)
    number = db.Column(db.Integer, nullable=False)
    reach = db.Column(db.Integer, nullable=False)
    flag = db.Column(db.Integer, nullable=False, default=0)

class Sponsor(db.Model):
    __tablename__ = 'sponsor'
    sid=db.Column(db.Integer,primary_key=True)
    sname = db.Column(db.String, nullable=False)
    usename = db.Column(db.String, unique=True)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    industry = db.Column(db.String, nullable=False)
    number = db.Column(db.Integer, nullable=False)
    flag = db.Column(db.Integer, nullable=False, default=0)

class Campaign(db.Model):
    __tablename__ = 'campaign'
    campaignid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sname = db.Column(db.String, db.ForeignKey('sponsor.usename'), nullable=False)
    iname = db.Column(db.String, db.ForeignKey('influencer.usename'))
    cname = db.Column(db.String, nullable=False)
    budget = db.Column(db.Integer, nullable=False)
    desc = db.Column(db.String, nullable=False)
    startdate = db.Column(db.Integer, nullable=False)
    enddate = db.Column(db.Integer, nullable=False)
    public = db.Column(db.Integer, nullable=False)
    job = db.Column(db.String, nullable=False)
    flag = db.Column(db.Integer, nullable=False, default=0 )

class Requests(db.Model):
    __tablename__ = 'requests'
    reqid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sname = db.Column(db.String, db.ForeignKey('sponsor.sid') )
    iname = db.Column(db.String, db.ForeignKey('influencer.inid'))
    campaign_id = db.Column(db.String, db.ForeignKey('campaign.campaignid'))
    icheck = db.Column(db.String)
    scheck = db.Column(db.String)
    msg= db.Column(db.String)
    amount=db.Column(db.String, db.ForeignKey('campaign.budget') )
    cname=db.Column(db.String, db.ForeignKey('campaign.cname') )

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  

    
