
# TRADING APP FOR BYBIT V2 


# IMPORTS
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

from contextlib import closing
import json
from configs import FTXConfig, BYBITConfig
from datetime import datetime
import pytz
import Forms
from Testing import *
import pandas as pd 
import os
from clients.FTXClient import FTXClient
from clients.BYBITClient import BBClient
from time import sleep
import sqlite3


# ORDER METHODS
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Create a method for limit order FTX
def FTXorder(market,side,price,size,postOnly=True,type='limit'):
    try:
        print(f"Sending order {type}- {side} - {price} - {size} - {market} ")
        order = FTXClient.place_order(market=market,side=side,price=price,size=size,type=type,post_only=postOnly)
    except Exception as e:
        print("An exception occured {}".format(e))
        return False
    return order

# Create a method for market order FTX
def FTXmarketOrder(market,side,size,price=0,type='market'):
    try:
        print(f"Sending order {type}- {side} - {size} - {market}")
        market_order = FTXClient.place_order(market=market,side=side,size=size,price=price,type=type)
    except Exception as e:
        print("An exception occured {}".format(e))
        return False
    return market_order

# Create a method for trigger order FTX
def FTXtriggerOrder(market,side,size,triggerPrice):
    try:
        print(f"Sending trigger order stop loss {side} - {size} - {market} - {triggerPrice} ")
        triggerOrder = FTXClient.place_conditional_order(market=market,side=side,size=size,trigger_price=triggerPrice)
    except Exception as e:
        print(f"An exception occured {e}")
        return False
    return triggerOrder

# Create a method for limit order BYBIT
def BBorder(symbol,side,quantity,price,tif="PostOnly",order_type="Limit"):
    try:
        print(f"Sending order {order_type}- {side} - {price} - {quantity} - {symbol} ")
        order = BBClient.Order.Order_new(symbol=symbol,side=side,qty=quantity,price=price,time_in_force=tif,order_type=order_type)
    except Exception as e:
        print("An exception occured {}".format(e))
        return False
    return order


# Create a method for order market BYBIT
def BBmarketOrder(symbol,side,quantity,tif="GoodTillCancel",order_type="Market"):
    try:
        print(f"Sending order Market for rebalance {order_type}- {side} - {quantity} - {symbol} ")
        orderMarket = BBClient.Order.Order_new(symbol=symbol,side=side,qty=quantity,order_type=order_type,time_in_force=tif)
    except Exception as e:
        print("An exception occured {}".format(e))
        return False
    
    return orderMarket

def BBtriggerOrder(symbol,side,quantity,stop_px,base_price,order_type="Market",tif="GoodTillCancel"):
    try:
        print(f"Sending trigger order stop loss {order_type} - {side} - {quantity} - {symbol} ")
        triggerOrder = BBClient.Conditional.Conditional_new(symbol=symbol,side=side,qty=quantity,stop_px=stop_px,
                            base_price=base_price,order_type=order_type,time_in_force=tif)
    except Exception as e:
        print("An exception occured {}".format(e))
        return False 

    return triggerOrder


def trackOrders():
    print("Cancel Percentage Stop Loss")
    if BYBITConfig.arrID == []:
        return
    else:
        for orderID in BYBITConfig.arrID:
            orderStatus = BBClient.Order.Order_query(symbol="BTCUSD", order_id=orderID[0]).result()[0]['result']['order_status']
            triggerStatus = BBClient.Order.Order_query(symbol="BTCUSD", order_id=orderID[1]).result()[0]['result']['order_status']
            print("Order status ==>", orderStatus)
            print("Conditional order status ==>", triggerStatus)
            if orderStatus == "New" and triggerStatus == "Triggered":
                #If conditionnal order hits, unfilled order cancelled
                cancelOrder=BBClient.Order.Order_cancel(symbol="BTCUSD",order_id=orderID[0]).result()
                BYBITConfig.arrID.pop(BYBITConfig.arrID.index(orderID))
                print("Array IDs ==>", BYBITConfig.arrID)
            elif orderStatus == "Filled" and triggerStatus == "Untriggered":
                #If order filled, conditional order cancelled
                cancelOrder=BBClient.Order.Order_cancel(symbol="BTCUSD",order_id=orderID[1]).result()
                BYBITConfig.arrID.pop(BYBITConfig.arrID.index(orderID))
                print("Array IDs ==>", BYBITConfig.arrID)
            else:
                print("Waiting for action.")




def FTXQuery():
    connection = sqlite3.connect("Database.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM ftx_input")
    rows = cursor.fetchall()

    LastRowData = rows[-1]
    return LastRowData



# GET PERPS ONLY
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def get_perps():
    SYMBOLS = FTXClient.get_futures()
    OnlyPerps = []
    for PerpMarkets in SYMBOLS:
    #print(markets["name"])
        if "perp" in PerpMarkets["name"].lower():
            OnlyPerps.append(PerpMarkets["name"])
    return OnlyPerps


# FLASK SERVER
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Config flask app for local server
from flask import Flask, render_template, url_for, request, flash, session, redirect, g, abort
import requests 
from flask_sqlalchemy import SQLAlchemy  
from sqlalchemy.dialects.postgresql import ARRAY
app = Flask(__name__)

db = SQLAlchemy(app) 
app.config['SECRET_KEY'] = '5fddd6c2492558694d66c165'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# All classes for database
class User:
    def __init__(self,id,username,password):
        self.id = id
        self.username = username
        self.password = password

users = []
users.append(User(id=1,username='Karl',password='AdminKarl01'))
users.append(User(id=2,username='Zac',password='Zac123'))

class FTXInput(db.Model):
    id = db.Column("id",db.Integer, primary_key=True)
    symbol = db.Column("symbol",db.String(20),default="")
    qty = db.Column(db.Integer,default=0)
    pips_buy = db.Column(db.Integer,default=0)
    pips_sell = db.Column(db.Integer,default=0)
    capital = db.Column(db.Integer,default=0)
    max_pos_buy = db.Column(db.Integer,default=0)
    max_pos_sell = db.Column(db.Integer,default=0)
    options = db.Column(db.String(50),default='')
    pl_long = db.Column(db.Integer,default=0)
    pl_short = db.Column(db.Integer,default=0)
    timer = db.Column(db.Integer,default=0)
    recursive_timer = db.Column(db.Integer,default=0)
    order_type = db.Column(db.String(50),default='')
    activated = db.Column(db.Boolean,default=False)
    

    def __init__(self,symbol,qty,max_pos_buy,max_pos_sell,pips_buy,
                 pips_sell,timer,order_type,recursive_timer,options,pl_long,pl_short,activated):
        self.symbol = symbol # added new
        self.qty = qty
        self.pips_buy = pips_buy
        self.pips_sell = pips_sell
        #self.capital = capital
        self.max_pos_buy = max_pos_buy
        self.max_pos_sell = max_pos_sell
        self.options = options
        self.timer = timer
        self.recursive_timer = recursive_timer
        self.pl_long = pl_long
        self.pl_short = pl_short
        self.order_type = order_type
        self.activated = activated
        
        

class BYBITInput(db.Model):
    id = db.Column("id",db.Integer, primary_key=True)
    qty = db.Column(db.Integer,default=0)
    pips_buy = db.Column(db.Integer,default=0)
    pips_sell = db.Column(db.Integer,default=0)
    capital = db.Column(db.Integer,default=0)
    max_pos_buy = db.Column(db.Integer,default=0)
    max_pos_sell = db.Column(db.Integer,default=0)
    options = db.Column(db.String(50),default='')
    pl_long = db.Column(db.Integer,default=0)
    pl_short = db.Column(db.Integer,default=0)
    timer = db.Column(db.Integer,default=0)
    recursive_timer = db.Column(db.Integer,default=0)
    order_type = db.Column(db.String(50),default='')
    activated = db.Column(db.Boolean,default=False)

    def __init__(self,qty,capital,max_pos_buy,max_pos_sell,pl_long,pl_short,pips_buy,pips_sell,
                 timer,order_type,recursive_timer,options,activated):
        self.qty = qty
        self.pips_buy = pips_buy
        self.pips_sell = pips_sell
        self.capital = capital
        self.max_pos_buy = max_pos_buy
        self.max_pos_sell = max_pos_sell
        self.options = options
        self.pl_long = pl_long
        self.pl_short = pl_short
        self.timer = timer
        self.order_type = order_type
        self.recursive_timer = recursive_timer
        self.activated = activated

class BBStrategy(db.Model):
    id = db.Column("id",db.Integer, primary_key=True)
    qty = db.Column(db.Integer,default=0,nullable=True)
    pips_buy = db.Column(db.Integer,default=0,nullable=True)
    pips_sell = db.Column(db.Integer,default=0,nullable=True)
    timer = db.Column(db.Integer,default=0,nullable=True)
    recursive_timer = db.Column(db.Integer,default=0,nullable=True)
    order_type = db.Column(db.String(50),default='',nullable=True)
    cancel_orders = db.Column(db.Integer,default=0,nullable=True)
    activated = db.Column(db.Boolean,default=False)

    def __init__(self,qty,pips_buy,pips_sell,timer,recursive_timer,
                order_type,cancel_orders,reopening,activated):
        self.qty = qty
        self.pips_buy = pips_buy
        self.pips_sell = pips_sell
        self.timer = timer
        self.recursive_timer = recursive_timer
        self.order_type = order_type
        self.cancel_orders = cancel_orders
        self.activated = activated
        

class FTXStrategy(db.Model):
    id = db.Column("id",db.Integer, primary_key=True)
    symbol = db.Column("symbol",db.String(20),default="")
    qty = db.Column(db.Integer,default=0,nullable=True)
    pips_buy = db.Column(db.Integer,default=0,nullable=True)
    pips_sell = db.Column(db.Integer,default=0,nullable=True)
    timer = db.Column(db.Integer,default=0,nullable=True)
    recursive_timer = db.Column(db.Integer,default=0,nullable=True)
    order_type = db.Column(db.String(50),default='',nullable=True)
    cancel_orders = db.Column(db.Integer,default=0,nullable=True)
    reopening = db.Column(db.Boolean,default=False)
    activated = db.Column(db.Boolean,default=False)

    def __init__(self,symbol,qty,pips_buy,pips_sell,timer,recursive_timer,
                order_type,cancel_orders,reopening,activated):
        self.qty = qty
        self.symbol = symbol
        self.pips_buy = pips_buy
        self.pips_sell = pips_sell
        self.timer = timer
        self.recursive_timer = recursive_timer
        self.order_type = order_type
        self.cancel_orders = cancel_orders
        self.reopening = reopening
        self.activated = activated

class Counter(db.Model):
    id = db.Column("id",db.Integer, primary_key=True)
    count_orders = db.Column(db.Integer, default=0)
    count_sell = db.Column(db.Integer, default=0)
    count_buy = db.Column(db.Integer, default=0)
    count_cancelled = db.Column(db.Integer, default=0)
    count_exits = db.Column(db.Integer,default=0)
   
    def __init__(self):
        self.count_orders = 0
        self.count_buy= 0
        self.count_cancelled= 0
        self.count_sell= 0
        self.count_exits = 0
         
class Profit(db.Model):
    id = db.Column("id",db.Integer, primary_key=True)
    profit = db.Column(db.Float, nullable=False)
    gross_lose = db.Column(db.Float, nullable=False,default=0)
    gross_prof = db.Column(db.Float, nullable=False,default=0)

    def __init__(self):
        self.profit = 0 
        self.gross_lose = 0
        self.gross_prof = 0


# MUST CREATE THE AUTO CREATE FILE ALGO FOR DATABASE FILE
db_filename = "Database.db"
db_file_exits = os.path.isdir(db_filename)
if not db_file_exits:
    db.create_all()

   


#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------




# QUERY FTX_INPUT
def FTXQueryLastSymbol():
    connection = sqlite3.connect("Database.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM ftx_input")
    rows = cursor.fetchall()

    LastSymbol = rows[-1]
    return LastSymbol


# ROUTES AND METHODS FOR TRADES
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@app.before_request
def before_request():
    g.user = None
    # g.apiKeyFTX = None
    # g.apiSecretFTX = None
    # g.apiKeyBB = None
    # g.apiSecretBB = None
    if 'user_id' in session:
        user = [x for x in users if x.id == session['user_id']][0]
        g.user = user
    # if 'api_key_ftx' in session:
    #     g.apiKeyFTX = session['api_key_ftx']
    #     g.apiSecretFTX = session['api_secret_ftx']
    #     FTXConfig.api_keyFTX = session['api_key_ftx']
    #     FTXConfig.api_secretFTX = session['api_secret_ftx']
    # if 'api_key_bybit' in session:
    #     g.apiKeyBB = session['api_key_bybit']
    #     g.apiSecretBB = session['api_secret_bybit']
    #     BYBITConfig.api_key = session['api_key_bybit']
    #     BYBITConfig.api_secret = session['api_secret_bybit']

@app.route('/Login',methods=['GET','POST'])
def login():
    form=Forms.LoginForm()
    if form.submit.data:
        session.pop('user_id', None)
        username = form.username.data
        password = form.password.data
        try:
            user = [x for x in users if x.username == username][0]
            if user and user.password == password:
                session['user_id'] = user.id
                return redirect(url_for('ftxWelcome'))
            else:
                return redirect(url_for('login'))
        except:
            return redirect(url_for('login'))
    return render_template('login.html', form=form)


#Set API Key and secret
@app.route('/API',methods=['GET',"POST"])
def api():
    form=Forms.APIKEY()
    if form.validate_on_submit():
        try:
            session.pop('api_key_ftx',None)
            session.pop('api_secret_ftx',None)
            session.pop('api_key_bybit',None)
            session.pop('api_secret_bybit',None)
            apiKeyFTX = form.apiKeyFTX.data
            apiSecretFTX = form.apiSecretFTX.data
            apiKeyBB = form.apiKeyBB.data
            apiSecretBB = form.apiSecretBB.data
            if apiKeyFTX != '' and apiKeyBB == '':
                if apiSecretFTX == '':
                    flash('API Secret needs to be enter.','warning')
                else:
                    session['api_key_ftx'] = apiKeyFTX
                    session['api_secret_ftx'] = apiSecretFTX
                    flash("API Key and Secret for FTX is saved.",'success')
            if apiKeyBB != '' and apiKeyFTX == '':
                if apiSecretBB == '':
                    flash('API Secret needs to be enter.','warning')
                else:
                    session['api_key_bybit'] = apiKeyBB
                    session['api_secret_bybit'] = apiSecretBB
                    flash("API Key and Secret for Bybit is saved.",'success')

            if apiKeyFTX != '' and apiKeyBB != '':
                if apiSecretBB == '' or apiSecretFTX == '':
                    flash("API Secret need to be enter for both.",'warning')
                else:
                    session['api_key_ftx'] = apiKeyFTX
                    session['api_secret_ftx'] = apiSecretFTX
                    session['api_key_bybit'] = apiKeyBB
                    session['api_secret_bybit'] = apiSecretBB
                    flash("API Key and Secret for FTX and Bybit is saved.",'success')
        except:
            flash("Sorry something went wrong. Please try again!",'danger')
    return render_template('api.html', form=form)


# Principal route
@app.route('/')
def ftxWelcome():
    return render_template("ftx/welcome.html",title="Home")


@app.route('/Test')
def crashTest():
    lp = FTXClient.get_market('SOL-PERP')['last']
    order = FTXorder('SOL-PERP','buy',lp,0.01)
    orderID = order['id']
    sleep(5)
    status = FTXClient.get_order_status(orderID)['status']
    filleSize = FTXClient.get_order_status(orderID)['filledSize']
    print(status)
    print(filleSize)

   
    # found_inputs = FTXStrategy.query.all()
    # for item in found_inputs:
    #     qty = item.qty
    # print(qty)
    # if g.apiKeyFTX is None:
    #     print('No API KEY FTX')
    # else:
    #     print(g.apiKeyFTX)

    # if g.apiKeyBB is None:
    #     print('No API KEY BYBIT')
    # else:
    #     print(g.apiKeyBB)

    # print(BYBITConfig.api_key)
    # print(FTXConfig.api_keyFTX)

    # foundA = BYBITInput.query.all()
    # foundB = BBStrategy.query.all()
    # foundA = FTXInput.query.all()
    # foundB = FTXStrategy.query.all()
    # for items in foundA:
    #     activatedA = items.activated
    # if foundB:
    #     for item in foundB:
    #         activatedB = item.activated
    # print(f"Form B: {activatedB}")
    # print(f"Form A: {activatedA}")
    # order = FTXorder('SOL-PERP','buy', 200,0.04,'gfhdftghdfgh')
    # ID = order['id']
    # clientID = order['clientId']
    # print(order['clientId'])
    # sleep(5)
    # FTXClient.modify_order(existing_client_order_id=clientID,price=195.0,size=0.04)
    # print("Modify order")
    return
 

# Page for enter inputs
@app.route("/Inputs", methods=['GET','POST'])  
def ftxInputs():
    if not g.user:
        return redirect(url_for('login')) 
    stickValues = []
    sndTimer = 0
    pl_long = 0
    pl_short = 0
    timer = 0
    type = ''
    options = ''
    form = Forms.FTXInputsForms()
    orderForm = Forms.FTXOrdersForms()
    stratForm = Forms.FTXStrat()
    if form.validate.data:
        if int(request.form['Options']) == 1:
            try:
                if request.form['typeTimer'] == 'True':
                    type = 'Market'
                else:
                    type = 'Limit'
                    sndTimer = int(request.form['SndTimer'])
                timer = int(request.form['timer'])
                options = 'Timer Stop Loss'
                flash('Validation correct. Update done!', 'success')
            except:
                flash('Validation incorrect. Please fill all inputs!','danger')
        elif int(request.form['Options']) == 2:
            try:
                pl_long = form.percentage_long.data
                pl_short = form.percentage_short.data
                if request.form['typePercentage'] == 'True':
                    type = 'Market'
                else:
                    type = 'Limit'
                options = 'Percentage Stop Loss'
                flash('Validation correct. Update done!', 'success')
            except:
                flash('Validation incorrect. Please fill all inputs!','danger')
        else:
            flash('Validation correct. Update done!', 'success')
        inputs = FTXInput(symbol=form.symbols.data,qty=form.quantity.data,pips_buy=form.pips_buy.data,pips_sell=form.pips_sell.data,max_pos_sell=form.max_pos_sell.data,
                            max_pos_buy=form.max_pos_buy.data,timer=timer,recursive_timer=sndTimer,order_type=type,options=options,pl_long=pl_long,pl_short=pl_short,activated=True)
        db.session.add(inputs)
        db.session.commit()
        activatedB = FTXStrategy.query.all()
        if activatedB:
            activatedB[-1].activated = False
            db.session.commit()
        else:
            ActivatedB = FTXStrategy(0,0,0,0,0,'',0,False,False)
            db.session.add(ActivatedB)
            db.session.commit()
    if orderForm.validate_on_submit():
        try:
            url = "https://test-webhook-app-v1.herokuapp.com/webhook"
            orderType = request.form['orderType']
            symbol = orderForm.symbols.data
            symbolOrder = symbol[:-4] + "-" + symbol[-4:]
            price = orderForm.limit_price.data
            qty = orderForm.qty.data
            lp = FTXClient.get_market(symbolOrder)['last']
            qty = qty / lp
            if 'Buy' in request.form:
                if orderType == 'market':
                    order= FTXmarketOrder(symbolOrder,'buy',qty)
                else:
                    requestOrder = {'passphrase':'TERMINAL','ticker':symbol, 'exchange':'FTX',
                    'strategy':{'order_action':'buy','order_price':price}}
                    r = requests.post(url,json=requestOrder)
                    print(f"Statut code: {r.status_code}")
            elif "Sell" in request.form:
                if orderType == 'market':
                    order= FTXmarketOrder(symbolOrder,'sell',qty)
                else:
                    requestOrder = {'passphrase':'TERMINAL','ticker':symbol,'exchange':'FTX',
                    'strategy':{'order_action':'sell','order_price':price}}
                    r = requests.post(url,json=requestOrder)
                    print(f"Statut code: {r.status_code}")
            if order or r.status_code == '200':
                flash("Order went through.","success")
            else:
                flash("Order failed. Please try again!","danger")
        except Exception as e:
            print(f"Problem occured: {e}")
            return redirect(url_for('ftxInputs'))
    if stratForm.submit.data:
        try:
            recursive_timer = 0
            reopening = stratForm.reopening.data
            orderType = request.form['typeStrat']
            recursive_timer = request.form['recursive_timer']
            inputs = FTXStrategy(stratForm.symbols.data,stratForm.qty.data,stratForm.pips_buy.data,stratForm.pips_sell.data,stratForm.timer.data,
            recursive_timer,orderType,stratForm.cancel_order.data,reopening,True)
            db.session.add(inputs)
            db.session.commit()
            activatedA = FTXInput.query.all()
            if activatedA:
                activatedA[-1].activated = False
                db.session.commit()
            else:
                ActivatedA = FTXInput(0,0,0,0,0,0,0,0,0,'',0,'',False)
                db.session.add(ActivatedA)
                db.session.commit()
            flash("Validation correct. Update done!","success")
        except Exception as e:
            print(e)
            flash("Inputs invalid. Please try again!","danger")
        
    return render_template('ftx/inputs.html', title="Inputs", form=form,Candles=stickValues,orderForm=orderForm,stratForm=stratForm)

   
# Page for see inputs updated
@app.route("/View")
def ftxView():
    if not g.user:
        return redirect(url_for('login'))
    return render_template("ftx/view.html", values=FTXInput.query.all(), valide=FTXInput.query.first(),title="View")

# Journal Page
@app.route("/Journal")
def ftxJournal():
    if not g.user:
        return redirect(url_for('login'))
    return render_template("ftx/journal.html", counter=Counter.query.all(), valide=Counter.query.first(), profit=Profit.query.all(), prof_val=Profit.query.first(), perc_prof=FTXConfig.percentage_prof,title="Journal")

@app.route("/Testing", methods=['GET','POST'])
def ftxTesting():
    if not g.user:
        return redirect(url_for('login'))
    markers = []
    totalTrade = 0
    values = [{'time':0,'value':0}]
    data_date = []
    data_prof = []
    data_sum = 0
    data_gross_prof = 0
    data_gross_lose = 0
    Wins = 0
    Loses = 0
    wins_doll = 0
    loses_doll = 0
    sum_doll = 0
    rsi = [{'time':0,'value':0}]
    form = Forms.TestingForm()
    if form.validate_on_submit():
        date_start = request.form['datestart']
        date_end = request.form['datend']
        value_options = int(request.form['Options'])
        value_rsi = int(request.form['TimeFrame'])
        capital = form.Capital.data
        size = form.Size.data
        sl = form.Sl.data
        tp = form.Tp.data
        if value_rsi != 0:
            data_chart = RSIStrat(form.RsiBuy.data,form.RsiSell.data,form.Length.data,date_start,date_end,sl,tp,capital,size) 
            values = data_chart[0]
            markers = data_chart[1]
            data_sum = data_chart[2]
            data_gross_prof = data_chart[3]
            data_gross_lose = data_chart[4]
            Wins = data_chart[5]
            Loses = data_chart[6]  
            rsi = data_chart[7]
        elif value_options != 0:
            data_chart = FundingStrat(request.form['Options'],date_start,date_end,sl,tp)
            values = data_chart[0]
            data_sum = data_chart[1]
            data_gross_lose = data_chart[2]
            data_gross_prof = data_chart[3]
            Loses = data_chart[4]
            Wins = data_chart[5]
            sum_doll = data_chart[6]
            wins_doll = data_chart[7]
            loses_doll = data_chart[8]
        else:
            data_chart = SimpleStrat(form.Time_to_buy.data,form.Time_to_sell.data,date_start,date_end,sl,tp,capital,size)    
            values = data_chart[0]
            data_sum = data_chart[1]
            totalTrade = data_chart[2]
            data_gross_lose = data_chart[3]
            data_gross_prof = data_chart[4]
            Loses = data_chart[5]
            Wins = data_chart[6]
            sum_doll = data_chart[7]
            wins_doll = data_chart[8]
            loses_doll = data_chart[9]
  
    return render_template("ftx/testing.html",form=form,times=data_date, profits=data_prof,sum=data_sum,totalTrades=totalTrade,gross_lose=data_gross_lose,gross_prof=data_gross_prof,wins=Wins,loses=Loses,dollarSum=sum_doll,dollarWins=wins_doll,dollarLoses=loses_doll,values=values,markers=markers,rsi=rsi,title="Testing")


# Create a route for webhook POST request 
@app.route('/webhook', methods=['POST'])
def ftxwebhook():
    order_response = False

    data = json.loads(request.data)
    
    # CHECKING PASSWORD ALERT
    #----------------------------------------------------------------------------------------------------------

    # if g.apiKeyFTX is None:
    #     print("The API key is not set.")
    #     return{
    #         'code':'Stop',
    #         'message':'API key'
    #     }

    # Set if condition for passwrod webhook 
    if data["passphrase"] != FTXConfig.webhook_password:
        print("Invalid password! Please checks logs.")
        
        return {
            'code':'Error Login',
            'message':'Password Invalid'
            }
    
   
    # VALIDATION AND CREATION INPUTS
    #----------------------------------------------------------------------------------------------------------
   
    # Check if inputs are correctly entered
    found_inputs = FTXInput.query.all()
    found_inputs_strat = FTXStrategy.query.all()

    if not found_inputs and not found_inputs_strat:
        print("Inputs are not defined. Please enter inputs!")
        return{
            'code':'Error Inputs.',
            'message':'Inputs are not defined.'
            }

    # Get the last values into the table and put it into variables for create orders
    for item in found_inputs:
        qty = item.qty
        pips_data_b = item.pips_buy
        pips_data_s = item.pips_sell
        capital_data = item.capital
        max_pos_buy = item.max_pos_buy
        max_pos_sell = item.max_pos_sell
        pl_long_data = item.pl_long
        pl_short_data = item.pl_short
        options = item.options
        timer = item.timer
        recursive_timer = item.recursive_timer
        type = item.order_type
        activatedA = item.activated

    for items in found_inputs_strat:
        qty_b = items.qty
        pips_data_b_B = items.pips_buy
        pips_data_s_B = items.pips_sell
        timer_B = items.timer
        order_type_B = items.order_type
        cancel_orders = items.cancel_orders
        recursive_timer_B = items.recursive_timer
        reopening = items.reopening
        activatedB = items.activated



    bybitSymbol = {
        'BTCUSD':'BTC-PERP',
        'SOLUSDT':'SOL-PERP',        
    }

    #Get the exchange from the alert
    exchange = data['exchange']
    #Get side order
    side_data = data['strategy']['order_action']
    if exchange == 'FTX':
        # Symbol: BTCUSD
        #symbol = data["ticker"]
        #symbol_data = symbol[:-4] + "-" + symbol[-4:]
        symbol = FTXQueryLastSymbol()[-1]
        symbol_data = symbol
        # Price close FTX
        price = data["strategy"]["order_price"]
    else:
        #Bybit signal from trading view
        symbol = data["ticker"]
        #Convert symbol from bybit to FTX symbol
        symbol_data = bybitSymbol.get(symbol)
        #Last price FTX
        last_price = FTXClient.get_market(symbol_data)['last']
        #Last price FTX
        price = last_price

    #Convert qty dollars to currency amount
    qty_data = qty / price
    #Convert qty dollars for parameter B
    qty_data_b = qty_b / price
    
    #Adding pips for parameter A and B using 
    if activatedA:
        if side_data == 'sell':
            price_data = price + ((price/10000) * pips_data_s)
            price_data = price_data.__round__(3)
        elif side_data == 'buy':
            price_data = price - ((price/10000) * pips_data_b)
            price_data = price_data.__round__(3)
    if activatedB:
        if side_data == 'sell':
            price_data_b = price + ((price/10000) * pips_data_s_B)
            price_data_b = price_data_b.__round__(3)
        elif side_data == 'buy':
            price_data_b = price - ((price/10000) * pips_data_b_B)
            price_data_b = price_data_b.__round__(3)



    # Get size and side position 
    size = FTXQueryLastSymbol()[1]
    sizeDollars = size * price 
    side = side_data
    
    print(f"Current size ===> {sizeDollars}, side ==> {side}")
    
    # DEFINE RISK MANAGEMENTS
    #----------------------------------------------------------------------------------------------------------

    # Define the max position for short and long sides
    countBuy = 0
    countSell = 0 
    Orders = FTXClient.get_open_orders(symbol_data)
    for actives in Orders:
        if actives['side'] == "buy":
            countBuy += 1
        elif actives['side'] == "sell":
            countSell += 1
        
    if countSell >= max_pos_sell and max_pos_sell != 0:
        print("Max position (Short) reached.")
        return{
            'code':'Stop server.',
            'message':'Max pos reached'
        }
    elif countBuy >= max_pos_buy and max_pos_buy != 0:
        print("Max position (Long) reached.")
        return{
            'code':'Stop server.',
            'message':'Max pos reached'
        } 
    
    
    # ORDERS AND METHODS
    #----------------------------------------------------------------------------------------------------------

    # Create an instance of Counter class
    c = Counter.query.first()
    count = 0
    cancelled = False

    if activatedA:
        order_response = FTXorder(symbol_data,side_data,price_data,qty_data)
        if options == "Timer Stop Loss":
            while True:
                count += 1
                ID = order_response['id']
                if count == 1:
                    sleep(timer)
                    print("Timer" + str(timer))
                else:
                    sleep(recursive_timer)
                    print(f"Recursive timer is activated:{recursive_timer}")
                fillSize = FTXClient.get_order_history(symbol_data,side_data,'limit')[0]['filledSize']
                try:
                    if fillSize == 0:
                        FTXClient.cancel_order(ID)
                        LP = FTXClient.get_market(symbol_data)['last']
                        print("The order have not been filled yet")
                        if type == 'Limit':
                            order_response = FTXorder(symbol_data,side_data,LP,qty_data)
                        else:
                            order_response = FTXmarketOrder(symbol_data,side_data,qty_data)
                            break
                    else:
                        FTXConfig.sizeRebalanced = False
                        break
                except Exception as e:
                    print(f'Problem occured: {e}')
                    cancelled = True
                    LP = FTXClient.get_market(symbol_data)['last']
                    print("The order has been cancelled.")
                    if type == 'Limit':
                        order_response = FTXorder(symbol_data,side_data,LP,qty_data)
                    else:
                        order_response = FTXmarketOrder(symbol_data,side_data,qty_data)
                        break
        elif options == "Percentage Stop Loss":
            while True:
                count += 1
                ID = order_response['id'] 
                sleep(1)
                fillSize = FTXClient.get_order_history(symbol_data,side_data,'limit')[0]['filledSize']
                try:
                    if fillSize == 0:
                        if side_data == "sell":
                            slPrice = price_data - (price_data * (pl_short_data/100))
                        else:
                            slPrice = price_data + (price_data * (pl_long_data/100))
                        print("Order has not been filled yet.")
                        LP = FTXClient.get_market(symbol_data)['last']
                        triggerOrder = FTXtriggerOrder(symbol_data,side_data,qty_data,slPrice)
                        triggerID = triggerOrder['id']
                        IDs = [ID,triggerID]
                        FTXConfig.arrID.append(IDs)
                        break
                    else:
                        print('Order has been filled.')
                        break
                except Exception as e:
                    print("The order has been cancelled.")
                    cancelled = True
                    LP = FTXClient.get_market(symbol_data)['last']
                    if type == 'Limit':
                        order_response = FTXorder(symbol_data,side_data,LP,qty_data)
                    else:
                        order_response = FTXmarketOrder(symbol_data,side_data,qty_data)
                        break
                
    if activatedB:
        closing_order = False
        countActiveBuy = 0
        countActiveSell = 0
        countClose = 0
        count = 0
        closingActiveID = 0

        if sizeDollars > 0 :
            if reopening == True:
                if side == 'buy' and side_data == 'buy':
                    order_response = FTXorder(symbol_data,side_data,price_data_b,qty_data_b)
                elif side == 'sell' and side_data == 'sell':
                    order_response = FTXorder(symbol_data,side_data,price_data_b,qty_data_b)
                
            if side == "buy"  and side_data == "sell":
                order_response = FTXorder(symbol_data,side_data,price_data_b,qty_data_b) #Second order with last price exchange and pips
                closing_order = FTXorder(symbol_data,side_data,price,size) #Closing order with the BYBIT last price 
                closingActiveID = closing_order['id']
            elif side == "sell" and side_data == "buy":
                order_response = FTXorder(symbol_data,side_data,price_data_b,qty_data_b) #Second order with last price exchange and pips
                closing_order = FTXorder(symbol_data,side_data,price,size) #Closing order with the BYBIT last price 
                closingActiveID = closing_order['id']
    
            
        elif sizeDollars == 0:
            order_response = FTXorder(symbol_data,side_data,price_data_b,qty_data_b) #If size neutral just normal order with lat price pips


        if order_response:
            while True:
                count += 1
                orderID = order_response['id']
                sleep(0.8)
                orderStatus = FTXClient.get_order_status(orderID)['status']
                orderFilledSize = FTXClient.get_order_status(orderID)['filledSize']
                if orderStatus == 'closed' and orderFilledSize == 0:
                    print("Order has been cancelled.")
                    lp = FTXClient.get_market(symbol_data)['last']
                    order_response = FTXorder(symbol_data,side_data,lp,qty_data_b)
                if orderStatus == 'closed' and orderFilledSize > 0:
                    print("Order has been filled.")
                    break
                if orderStatus == 'open' and orderFilledSize == 0:
                    break

        activeOrders = FTXClient.get_open_orders(symbol_data)
        for active in activeOrders:
            if active['side'] == "buy":
                if active['id'] == closingActiveID:
                    pass
                else:
                    countActiveBuy += 1
            elif active['side'] == "sell":
                if active['id'] == closingActiveID:
                    pass
                else:
                    countActiveSell += 1
            
        countActive = countActiveBuy + countActiveSell
        if cancel_orders == 1:
            for active in reversed(activeOrders):
                activeID = active['id']
                if countActive > 1:
                    FTXClient.cancel_order(activeID)
                    countActive -= 1

        elif countActiveBuy >= cancel_orders:
            for active in reversed(activeOrders):
                if active['side'] == 'buy':
                    activeID = active['id']
                    if cancel_orders > 1:
                        print("Cancel order when buy active is more than 1")
                        FTXClient.cancel_order(activeID)
                        cancel_orders -= 1
                    
        elif countActiveSell >= cancel_orders:
            for active in reversed(activeOrders):
                if active['side'] == 'sell':
                    activeID = active['id']
                    if cancel_orders > 1:
                        FTXClient.cancel_order(activeID)
                        cancel_orders -= 1

        elif cancel_orders == 0:
            pass

    
        if closing_order:
            while True:
                countClose += 1
                closingID = closing_order['id']
                sizeClose = FTXClient.get_position(name=symbol_data)['size']
                if countClose == 1:
                    sleep(timer_B)
                    print(f"Timer: {timer_B}")
                else:
                    sleep(recursive_timer_B)
                    print(f"Recursive timer: {recursive_timer_B}")
                fillSize = FTXClient.get_order_status(closingID)['filledSize']
                status = FTXClient.get_order_status(closingID)['status']
                if status == 'open' and fillSize == 0:
                    print("The closing order has not been filled yet.")
                    FTXClient.cancel_order(order_id=closingID)
                    lp = FTXClient.get_market(symbol_data)['last']
                    closing_order = FTXorder(symbol_data,side_data,lp,sizeClose)
                if status == 'closed' and fillSize == 0:
                    print("Closing order has been cancelled.")
                    lp = FTXClient.get_market(symbol_data)['last']
                    closing_order = FTXorder(symbol_data,side_data,lp,sizeClose)
                if status == 'closed' and fillSize > 0:
                    print("Closing order has been filled.")
                    break
                

    print("INFORMATION ABOUT MARKET: ")
    
    # # Updates counts for sell and buy orders
    # if side_data == "sell" and cancelled != True:
    #     if not c:
    #         c = Counter()
    #         c.count_sell += 1
    #         db.session.add(c)
    #     c.count_sell += 1 
    #     db.session.commit()
    # if side_data == "buy" and cancelled != True:
    #     if not c:
    #         c = Counter()
    #         c.count_buy += 1 
    #         db.session.add(c)
    #     c.count_buy += 1 
    #     db.session.commit()

    #print(f"Exits Position ==> {c.count_exits}")
    #print(f"Cancelled orders ==> {c.count_cancelled}")
    #print(f"Sell orders ==> {c.count_sell}")
    #print(f"Buy orders ==> {c.count_buy}")


    # When the request will reach the server return a response
    if order_response: 
        # if not c:
        #     c = Counter()
        #     c.count_orders += 1
        #     db.session.add(c)
        # c.count_orders += 1
        # db.session.commit()
        print(f"Orders went through") 
        return{
            "code":"Success",
            "message": f"Order excecuted, {side_data}"
            }
    else:
        print("Order failed.")
        return {
            "code": "Error",
            "message": "Order failed."
            }

       
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# BYBIT APP

@app.route("/bybit")
def bybitWelcome():
    if not g.user:
        return redirect(url_for('login'))
    return render_template('bybit/welcome.html',title="Home")


@app.route('/bybit/inputs',methods=['GET','POST'])
def bybitInputs():
    if not g.user:
        return redirect(url_for('login'))
    sndTimer = 0
    pl_long = 0
    pl_short = 0
    timer = 0
    type= ''
    options = ''
    form = Forms.BYBITInputsForms()
    orderForms = Forms.BBOrdersForms()
    stratForm = Forms.BBStrat()
    if form.validate.data:
        if int(request.form['Options']) == 1:
            try:
                if request.form['typeTimer'] == 'True':
                    type = 'Market'
                else:
                    type = 'Limit'
                    sndTimer = int(request.form['SndTimer'])
                timer = int(request.form['timer'])
                options = 'Timer Stop Loss'
                flash('Validation correct. Update done!', 'success')
            except:
                flash('Validation incorrect. Please fill all inputs!','danger')
        elif int(request.form['Options']) == 2:
            try:
                pl_long = form.percentage_long.data
                pl_short = form.percentage_short.data
                if request.form['typePercentage'] == 'True':
                    type = 'Market'
                else:
                    type = 'Limit'
                options = 'Percentage Stop Loss'
                flash('Validation correct. Update done!', 'success')
            except:
                flash('Validation incorrect. Please fill all inputs!','danger')
        else:
            flash('Validation correct. Update done!', 'success')
        inputs = BYBITInput(qty=form.quantity.data,pips_buy=form.pips_buy.data,pips_sell=form.pips_sell.data,capital=form.capital_fund.data,max_pos_buy=form.max_pos_buy.data,
                        max_pos_sell=form.max_pos_sell.data,pl_long=pl_long,pl_short=pl_short,timer=timer,order_type=type,recursive_timer=sndTimer,options=options,activated=True)
        db.session.add(inputs)
        db.session.commit()
        activatedB = BBStrategy.query.all()
        if activatedB:
            activatedB[-1].activated = False
            db.session.commit()
        else:
            ActivatedB = BBStrategy(0,0,0,0,0,'',0,False)
            db.session.add(ActivatedB)
            db.session.commit()
    if orderForms.validate_on_submit():
        try:
            url = 'https://test-webhook-app-v1.herokuapp.com/bybit/webhook'
            orderType = request.form['orderType']
            symbol = orderForms.symbols.data
            price = orderForms.limit_price.data
            qty = orderForms.qty.data
            if 'Buy' in request.form:
                if orderType == 'market':
                    order= BBmarketOrder(symbol,'Buy',qty).result()
                else:
                    requestOrder = {'passphrase':'TERMINAL','ticker':symbol,'exchange':'BYBIT',
                    'strategy':{'order_action':'buy','order_price':price}}
                    r = requests.post(url,json=requestOrder)
                    print(f"Status code: {r.status_code}")
            elif "Sell" in request.form:
                if orderType == 'market':
                    order= BBmarketOrder(symbol,'Sell',qty).result()
                else:
                    requestOrder = {'passphrase':'TERMINAL','ticker':symbol,'exchange':'BYBIT',
                    'strategy':{'order_action':'sell','order_price':price}}
                    r = requests.post(url,json=requestOrder)
                    print(f"Status code: {r.status_code}")
            if order:
                flash("Order went through.","success")
            else:
                flash("Order failed. Please try again!","danger")
            
        except:
            return redirect(url_for('bybitInputs'))
        
    if stratForm.submit.data:
        try:
            recursive_timer = 0
            orderType = request.form['typeStrat']
            recursive_timer = request.form['recursive_timer']
            inputs = BBStrategy(stratForm.qty.data,stratForm.pips_buy.data,stratForm.pips_sell.data,stratForm.timer.data,
            recursive_timer,orderType,stratForm.cancel_order.data,True)
            db.session.add(inputs)
            db.session.commit()
            activatedA = BYBITInput.query.all()
            if activatedA:
                activatedA[-1].activated = False
                db.session.commit()
            else:
                ActivatedA = BYBITInput(0,0,0,0,0,0,0,0,0,'',0,'',False)
                db.session.add(ActivatedA)
                db.session.commit()
            flash("Validation correct. Update done!","success")
        except Exception as e:
            print(e)
            flash("Inputs invalid. Please try again!","danger")
        
    return render_template('bybit/inputs.html',title="Inputs", form=form,orderForm=orderForms,stratForm=stratForm)

@app.route('/bybit/view')
def bybitView():
    if not g.user:
        return redirect(url_for('login'))
    return render_template('bybit/view.html',title="View",values=BYBITInput.query.all(),valide=BYBITInput.query.first())


@app.route('/bybit/journal')
def bybitJournal():
    if not g.user:
        return redirect(url_for('login'))
    return render_template('bybit/journal.html',title="Journal")


@app.route('/bybit/webhook',methods=['POST'])
def bybitWebhook():
    order_response = False

    data = json.loads(request.data)

    # CHECKING PASSWORD ALERT
    #----------------------------------------------------------------------------------------------------------
    # if g.apiKeyBB is None:
    #     print("The API key is not set.")
    #     return{
    #         'code':'Stop',
    #         'message':'API key'
    #     }


    # Set if condition for passwrod webhook 
    if data["passphrase"] != BYBITConfig.webhook_password:
        print("Invalid password! Please checks logs.")
        return {
            "code":"Error",
            "message":"Invalid request"
            }


    # VALIDATION AND CREATION INPUTS
    #----------------------------------------------------------------------------------------------------------

    # Check if inputs are correctly entered
    found_inputs = BYBITInput.query.all()
    found_inputs_strat = BBStrategy.query.all()

    if not found_inputs and not found_inputs_strat:
        print("Inputs are not defined. Please enter inputs!")
        return{
            'code':'Error Inputs.',
            'message':'Inputs are not defined.'
            }


    ftxSymbols = {
        'BTC-PERP':'BTCUSD',
        'SOL-PERP':'SOLUSDT'
    }

    

    

    # Get the last values into the table and put it into variables for create orders
    for item in found_inputs:
        qty_data = item.qty
        pips_data_b = item.pips_buy
        pips_data_s = item.pips_sell
        capital_data = item.capital
        max_pos_buy = item.max_pos_buy
        max_pos_sell = item.max_pos_sell
        pl_long_data = item.pl_long
        pl_short_data = item.pl_short
        options = item.options
        timer = item.timer
        recursive_timer = item.recursive_timer
        type = item.order_type
        activatedA = item.activated

    for items in found_inputs_strat:
        qty_data_B = items.qty
        pips_data_b_B = items.pips_buy
        pips_data_s_B = items.pips_sell
        timer_B = items.timer
        order_type_B = items.order_type
        recursive_timer_B = items.recursive_timer
        cancel_orders = items.cancel_orders
        activatedB = items.activated

    # Buy or Sell
    side_data = data["strategy"]["order_action"].title()
    #Get exchange platform
    exchange = data['exchange']
    if exchange == 'BYBIT':
        # Symbol: BTCUSD
        symbol_data = data["ticker"]
        # Price close FTX
        price = data["strategy"]["order_price"]
    else:
        #FTX signal from trading view
        symbol = data["ticker"]
        #Convert currency from ftx to bybit
        symbol_data = ftxSymbols.get(symbol)
        #Last price Bybit
        price = BBClient.Market.Market_symbolInfo(symbol).result()[0]['result'][0]['last_price']



    # Update price close regarding if sell or buy signal (half pips)
    if activatedA:
        if side_data == 'Sell':
            price_data = price + ((price/10000) * pips_data_s)
            price_data = price_data.__round__(3)
        elif side_data == 'Buy':
            price_data = price - ((price/10000) * pips_data_b)
            price_data = price_data.__round__(3)
    if activatedB:
        if side_data == 'Sell':
            price_data_b = price + ((price/10000) * pips_data_s_B)
            price_data_b = price_data_b.__round__(3)
        elif side_data == 'Buy':
            price_data_b = price - ((price/10000) * pips_data_b_B)
            price_data_b = price_data_b.__round__(3)


    #Select the coin for wallet 
    if symbol_data == 'SOLUSDT':
        coin = 'SOL'
    elif symbol_data == "BTCUSD":
        coin = 'BTC'
    # Get wallet balance 
    available = BBClient.Wallet.Wallet_getBalance(coin).result()[0]['result'][coin]['available_balance']    
    # Get size and side position
    size = BBClient.Positions.Positions_myPosition(symbol_data).result()[0]['result']['size']
    side = BBClient.Positions.Positions_myPosition(symbol_data).result()[0]['result']['side']

    print(f"Wallet Balance ===> {available}")
    print(f"Current size ===> {size}, side ==> {side}")

    # DEFINE MAX POSITION SIZE
    #----------------------------------------------------------------------------------------------------------
    if activatedA:
        countBuy = 0 
        countSell = 0 
        Orders = BBClient.Order.Order_getOrders(symbol=symbol_data,order_status="New").result()[0]['result']['data']
        for actives in Orders:
            if actives['side'] == "Buy":
                countBuy += 1
            elif actives['side'] == "Sell":
                countSell += 1
        
        if countSell >= max_pos_sell and max_pos_sell != 0:
            print("Max position (Short) reached.")
            return{
                'code':'Stop server.',
                'message':'Max pos reached'
            }
        elif countBuy >= max_pos_buy and max_pos_buy != 0:
            print("Max position (Long) reached.")
            return{
                'code':'Stop server.',
                'message':'Max pos reached'
            }

    # ORDERS
    #----------------------------------------------------------------------------------------------------------
    count = 0
    recursive=False
    if activatedA:
        order_response = BBorder(symbol_data,side_data,int(qty_data),price_data).result()
        if options == 'Timer Stop Loss':
            while True:
                ID = order_response[0]['result']['order_id']
                count += 1
                if count == 1:
                    sleep(timer)
                    print(f"Timer: {timer}")
                else:
                    sleep(recursive_timer)
                    print(f"Recursive timer activated: {recursive_timer}")
                status = BBClient.Order.Order_query(symbol=symbol_data, order_id=ID).result()[0]['result']['order_status']
                if status == "New":
                    BBClient.Order.Order_cancel(symbol=symbol_data,order_id=ID).result()
                    print("The order has not been filled.")
                    lp = BBClient.Market.Market_symbolInfo(symbol_data).result()[0]['result'][0]['last_price']
                    if type == "Limit": 
                        order_response = BBorder(symbol_data,side_data,int(qty_data),lp).result()
                    else:
                        order_response = BBmarketOrder(symbol_data,side_data,int(qty_data)).result()
                        break
                elif status == "Cancelled":
                    print("The order has been cancelled.")
                    lp = BBClient.Market.Market_symbolInfo(symbol_data).result()[0]['result'][0]['last_price']
                    if type == "Limit":
                        order_response = BBorder(symbol_data,side_data,int(qty_data),lp).result()
                    else:
                        order_response = BBmarketOrder(symbol_data,side_data,int(qty_data)).result()
                        break
                else:
                    print("The order has been filled.")
                    break
        elif options == 'Percentage Stop Loss':
            while True:
                count += 1
                ID = order_response[0]['result']['order_id']
                sleep(1)
                status = BBClient.Order.Order_query(symbol=symbol_data, order_id=ID).result()[0]['result']['order_status']
                if status == "New":
                    if side_data == "Sell":
                        slPrice = price_data - (price_data * (pl_short_data/100))
                        slPrice = slPrice.__round__(3)
                    else:
                        slPrice = price_data + (price_data * (pl_long_data/100))
                        slPrice = slPrice.__round__(3)
                    lp = BBClient.Market.Market_symbolInfo(symbol=symbol_data).result()[0]['result'][0]['last_price']
                    slOrder = BBtriggerOrder(symbol_data,side_data,str(qty_data),str(slPrice),lp).result()
                    print(f"Trigger stop loss placed at price: {slPrice}")
                    triggerID = slOrder[0]['result']['stop_order_id']
                    IDs = [symbol_data, ID, triggerID]
                    BYBITConfig.arrID.append(IDs)
                    break
                elif status == 'Cancelled':
                    print("The order has been cancelled.")
                    lp = BBClient.Market.Market_symbolInfo(symbol_data).result()[0]['result'][0]['last_price']
                    if type == "Limit":
                        order_response = BBorder(symbol_data,side_data,int(qty_data),lp).result()
                    else:
                        order_response = BBmarketOrder(symbol_data,side_data,int(qty_data)).result()
                        break
                else:
                    print("The order has been filled.")
                    break
            print("Checking for cancellation")
            if BYBITConfig.arrID != []:
                for orderID in BYBITConfig.arrID:
                    orderStatus = BBClient.Order.Order_query(symbol=symbol_data, order_id=orderID[1]).result()[0]['result']['order_status']
                    triggerStatus = BBClient.Order.Order_query(symbol=symbol_data, order_id=orderID[2]).result()[0]['result']['order_status']
                    if orderStatus == "New" and triggerStatus == "Triggered":
                        #If conditionnal order hits, unfilled order cancelled
                        BBClient.Order.Order_cancel(symbol=symbol_data,order_id=orderID[1]).result()
                        print("Unfilled order cancelled.")
                        BYBITConfig.arrID.remove(orderID)
                    elif orderStatus == "Filled" and triggerStatus == "Untriggered":
                        #If order filled, conditional order cancelled
                        BBClient.Conditional.Conditional_cancel(symbol=symbol_data,stop_order_id=orderID[2]).result()
                        print("Trigger order cancelled.")
                        BYBITConfig.arrID.remove(orderID)
                    else:
                        print("Waiting for action.")
    
    if activatedB:
        closing_order = False
        countActiveBuy = 0
        countActiveSell = 0
        count = 0

        if size > 0 :
            print("Closing order")
            if side == "Buy"  and side_data == "Sell":
                order_response = BBorder(symbol_data,side_data,int(qty_data_B),price_data_b).result() #Second order with last price exchange and pips
                closing_order = BBorder(symbol_data,side_data,int(size),price).result() #Closing order with the BYBIT last price 
            elif side == "Sell" and side_data == "Buy":
                order_response = BBorder(symbol_data,side_data,int(qty_data_B),price_data_b).result() #Second order with last price exchange and pips
                closing_order = BBorder(symbol_data,side_data,int(size),price).result() #Closing order with the BYBIT last price 
        elif size == 0:
            order_response = BBorder(symbol_data,side_data,int(qty_data_B),price_data_b).result() #If size neutral just normal order with lat price pips

        activeOrders = BBClient.Order.Order_getOrders(symbol=symbol_data,order_status="New").result()[0]['result']['data']
        for active in activeOrders:
            if active['side'] == "Buy":
                countActiveBuy += 1
            elif active['side'] == "Sell":
                countActiveSell += 1
        if countActiveBuy >= cancel_orders:
            for active in reversed(activeOrders):
                if active['side'] == 'Buy':
                    activeID = active['order_id']
                    #If more than one active order leave the last one
                    if cancel_orders > 1:
                        BBClient.Order.Order_cancel(symbol=symbol_data,order_id=activeID).result()
                        cancel_orders -= 1
                    #If only 1 active order cancel after next buy
                    elif cancel_orders == 1:
                        BBClient.Order.Order_cancel(symbol=symbol_data,order_id=activeID).result()
                        cancel_orders -= 1
        elif countActiveSell >= cancel_orders:
            for active in reversed(activeOrders):
                if active['side'] == 'Sell':
                    activeID = active['order_id']
                    #If more than one active order leave the last one
                    if cancel_orders > 1:
                        BBClient.Order.Order_cancel(symbol=symbol_data,order_id=activeID).result()
                        cancel_orders -= 1
                    #If only 1 active order cancel after next buy
                    elif cancel_orders == 1:
                        BBClient.Order.Order_cancel(symbol=symbol_data,order_id=activeID).result()
                        cancel_orders -= 1

    
        if closing_order:
            while True:
                count += 1
                closingID = closing_order[0]['result']['order_id']
                if count == 1:
                    sleep(timer_B)
                    print(f"Timer: {timer_B}")
                else:
                    sleep(recursive_timer_B)
                    print(f"Recursive timer: {recursive_timer_B}")
                status = BBClient.Order.Order_query(symbol=symbol_data, order_id=closingID).result()[0]['result']['order_status']
                if status == "New":
                    print("Closing order has not been filled.")
                    #Cancel closing order start recursive timer
                    BBClient.Order.Order_cancel(symbol=symbol_data,order_id=closingID).result()
                    lp = BBClient.Market.Market_symbolInfo(symbol=symbol_data).result()[0]['result'][0]['last_price']
                    closing_order = BBorder(symbol_data,side_data,int(size),lp).result()
                elif status == "Cancelled":
                    print("Closing order has been cancelled.")
                    lp = BBClient.Market.Market_symbolInfo(symbol=symbol_data).result()[0]['result'][0]['last_price']
                    closing_order = BBorder(symbol_data,side_data,int(size),lp).result()
                else:
                    print("Closing has been filled.")
                    break


    #When the request will reach the server return a response
    if order_response:
        print("Order went through.")
        return {
            "code":"Success",
            "message": f"Order excecuted, {side_data}"
            }
    else:
        print("Order failed.")
        return {
            "code": "Error!",
            "message": "Order failed."
            }
    
    

if __name__ == '__main__':
    app.run(debug=True)
        
        