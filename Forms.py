import sqlite3
from typing import Text
from flask.app import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, FloatField, IntegerField, DateField, SelectField, BooleanField
from wtforms.validators import EqualTo, DataRequired
from datetime import datetime
from scripts import get_perps, FTXQuery



class LoginForm(FlaskForm):

    username = StringField('Username', validators=[DataRequired()])

    password = PasswordField('Password', validators=[DataRequired()])

    submit = SubmitField('Login')

class FTXInputsForms(FlaskForm):

    checkbox = BooleanField('?Disabled')
    symbols = SelectField(validators=[DataRequired()],choices=[perpmarket for perpmarket in get_perps()],default=FTXQuery()[-1])

    quantity = FloatField('Quantity ($)', validators=[DataRequired()],default=FTXQuery()[1])

    pips_buy = FloatField('Pips Buy', validators=[DataRequired()],default=FTXQuery()[2])

    pips_sell = FloatField('Pips Sell', validators=[DataRequired()],default=FTXQuery()[3])

    max_pos_buy = IntegerField('Max Position (Long)', validators=[DataRequired()],default=FTXQuery()[5])
    
    max_pos_sell = IntegerField('Max Position (Short)', validators=[DataRequired()],default=FTXQuery()[6])

    
    Options = SelectField('Options',choices=[("0",'Stop Loss Options'),('1','Timer Stop Loss'),('2','Percentage Stop Loss')])

    percentage_long = FloatField(render_kw={'placeholder':'Percentage Loss (Long)'}, default=FTXQuery()[8])

    percentage_short = FloatField(render_kw={'placeholder':'Percentage Loss (Short)'}, default=FTXQuery()[9])

    validate = SubmitField('Validate')


class BYBITInputsForms(FlaskForm):

    checkbox = BooleanField('?Disabled')

    quantity = FloatField('Quantity ($)', validators=[DataRequired()],default=0)

    pips_buy = FloatField('Pips Buy', validators=[DataRequired()],default=0)

    pips_sell = FloatField('Pips Sell', validators=[DataRequired()],default=0)
    
    max_pos_buy = IntegerField('Max Position (Long)', validators=[DataRequired()],default=0)
    
    max_pos_sell = IntegerField('Max Position (Short)', validators=[DataRequired()],default=0)

    reopening = BooleanField('Reopening')

    percentage_long = FloatField(render_kw={'placeholder':'Percentage Loss (Long)'})

    percentage_short = FloatField(render_kw={'placeholder':'Percentage Loss (Short)'})

    Options = SelectField('Options',choices=[("0",'Stop Loss Options'),('1','Timer Stop Loss'),('2','Percentage Stop Loss')])

    validate = SubmitField('Validate')
    

class TestingForm(FlaskForm):
    
    Time_to_buy = DateField("Buy at",format="%H:%M:%S",default=datetime(2000,1,1,0,0,0))

    Time_to_sell = DateField("Sell at",format="%H:%M:%S",default=datetime(2000,1,1,0,0,0))

    Options = SelectField("Options",choices=[("0","Funding Rate Trades"),("1","1h"),("2","30min"),("3","15min")])

    Tp = FloatField("Take Profit",default=0)

    Sl = FloatField("Stop Loss", default=0)

    Length = IntegerField("Length",default=1)

    TimeFrame = SelectField("Timeframe",choices=[("0","Timeframe"),("1","Hour"),("2","Minute"),("3","Second")])

    RsiBuy = FloatField("RSI Buy",default=30)

    RsiSell = FloatField("RSI Sell",default=80)

    Capital = FloatField("Initial Capital",default=10000)
    
    Size = FloatField("Order Size",default=1000)

    submit_date = SubmitField('Submit')

    
class FTXOrdersForms(FlaskForm):

    limit_price = FloatField("Limit Price",validators=[DataRequired()],default=0)

    symbols = SelectField(validators=[DataRequired()],choices=[("SYMBOL"),("BTCPERP"),("SOLPERP"),("ETHPERP"),("XRPPERP")])

    qty = FloatField("Quantity ($)", validators=[DataRequired()],default=0)

    lastPrice = BooleanField('Last Price')

    Buy = SubmitField("Buy/Long")
   
    Sell = SubmitField("Sell/Short")

    
class BBOrdersForms(FlaskForm):
    
    limit_price = FloatField("Limit Price",validators=[DataRequired()],default=0)

    symbols = SelectField(validators=[DataRequired()],choices=[("SYMBOL"),("BTCUSD"),("BTCUSDT"),("SOLUSD"),("ETHUSD"),("XRPUSD")])

    qty = FloatField("Quantity ($)", validators=[DataRequired()],default=0)

    lastPrice = BooleanField('Last Price')

    Buy = SubmitField("Buy/Long")
   
    Sell = SubmitField("Sell/Short")
    

class FTXStrat(FlaskForm):

    checkbox = BooleanField('?Disabled')

    qty = FloatField("Quantity ($)",validators=[DataRequired()],default=0)

    pips_buy = FloatField('Pips Buy', validators=[DataRequired()],default=0)

    pips_sell = FloatField('Pips Sell', validators=[DataRequired()],default=0)

    timer = FloatField('Timer', validators=[DataRequired()], default=0)

    cancel_order = FloatField("#C Orders",validators=[DataRequired()],default=0)

    reopening = BooleanField('Reopening')

    recursive_timer = FloatField("Recursive Timer", render_kw={'placeholder':'Recursive Timer'})

    submit = SubmitField("Validate")


class BBStrat(FlaskForm):

    checkbox = BooleanField('?Disabled')

    qty = FloatField("Quantity ($)",validators=[DataRequired()],default=0)

    pips_buy = FloatField('Pips Buy', validators=[DataRequired()],default=0)

    pips_sell = FloatField('Pips Sell', validators=[DataRequired()],default=0)

    timer = FloatField('Timer', validators=[DataRequired()], default=0)

    recursive_timer = FloatField("Recursive Timer", render_kw={'placeholder':'Recursive Timer'})

    reopening = BooleanField('Reopening')

    cancel_order = FloatField("#C Orders",validators=[DataRequired()],default=0)

    submit = SubmitField("Validate")


class APIKEY(FlaskForm):

    apiKeyFTX = StringField("API Key (FTX)",default='')

    apiSecretFTX = StringField("API Secret")

    apiKeyBB = StringField("API Key (Bybit)")

    apiSecretBB = StringField("API Secret")

    submit = SubmitField("Save")

    
