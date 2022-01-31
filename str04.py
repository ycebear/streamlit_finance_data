import streamlit as st
import datetime
import numpy as np
import pandas as pd
from pandas_datareader import data as pdr
from matplotlib import pyplot as plt
import matplotlib.dates as mdates

#---- READ stock price ---------------------------------
def read_stock_data(Share, Begin, End):
    begin = Begin.strftime('%Y-%m-%d')
    end   = End.strftime('%Y-%m-%d')
    
    D = pdr.get_data_yahoo(Share,begin,end)
    
    Title = Share + '   ' + begin + '  to  ' + end
    return D, Title

#---- einfacher Linien-Plot ----------------------------
def plot_data(D,Title):
    with plt.style.context('fast'):    # 'dark_background'
        fig0, ax0 = plt.subplots(figsize=(20,6))

        plt.plot(D.index, D['Open'],  'blue',   lw=6, alpha=0.7, label='open')
        plt.plot(D.index, D['Close'], 'violet', lw=6, alpha=0.7, label='close')
        plt.plot(D.index, D['High'],  'red',    lw=1, alpha=0.7, label='high')
        plt.plot(D.index, D['Low'],   'magenta',lw=1, alpha=0.7, label='low')
        plt.fill_between(D.index, D['Open'], D['Close'], color='yellow', alpha=0.6)
        plt.fill_between(D.index, D['High'], D['Low'], color='k', alpha=0.2)

        plt.margins(0.01); plt.grid(False); plt.legend(prop={'size': 15})
        plt.title(Title,fontsize=20, fontweight='bold')
        #plt.show()
        return fig0, ax0

#---- plot mit Trends --------------------------------------------
def scale(a): return (a-a.min())/(a.max()-a.min())

def get_volatility(price):
    dt_roll = 20
    mavr = price.rolling(dt_roll,center=True).mean()
    mstd = price.rolling(dt_roll,center=True).std()
    return(mavr, mstd)

def plot_volatility_3(D, nStd=2, Title='', avrLabel='', stdLabel=''):
    #https://stackoverflow.com/questions/17638137/curve-fitting-to-a-time-series-in-the-format-datetime

    #---- compute the volatility of the rolling mean periode
    mavr, mstd = get_volatility(D['Close'])

    #---- for interpolation with datetime as x-axis
    ytr =  D['Close']
    xtr = mdates.date2num(D.index)
    dd = mdates.num2date(xtr)

    with plt.style.context('fivethirtyeight'):   #('fivethirtyeight'):   #('seaborn'):
        fig, ax = plt.subplots(2, 1,  gridspec_kw={'height_ratios': [4, 1]}, sharex=True, figsize=(20,10))

        #--- price curve ---
        ax[0].plot(D.index, D['Close'], 'grey',lw=2, alpha=0.5, label='Close')
        ax[0].fill_between(D.index, D['High'], D['Low'], color='yellow', alpha=0.3, label='high/low')

        #---- rolling meand and standard deviation ----
        ax[0].plot(mavr.index, mavr, 'b',label='Close rolling mean')
        ax[0].fill_between(mstd.index, mavr-nStd*mstd, mavr+nStd*mstd, color='b', alpha=0.1, label= '2*standard deviation')

        #--- trend line 1. and 3. degree ---
        price_trend_1 = np.poly1d(np.polyfit(xtr, ytr, 3))
        price_trend_2 = np.poly1d(np.polyfit(xtr, ytr, 1))
        ax[0].plot(D.index,price_trend_1(xtr), c='red', lw=3,label='trend 3grd')
        ax[0].plot(D.index,price_trend_2(xtr), c='purple', lw=1,label='trend 1grd')

        #---- last Close ----
        ax[0].scatter(D.index[-1], D['Close'][-1], c='r', s=400)

        #--- volume ---
        #plt.step(vx,vy,color='lime',label='volume')
        ax[1].fill_between(D.index, D['Volume'].min(), D['Volume'], step="pre", color='lime',alpha=1)
        ax[1].hlines(y= D['Volume'].mean(), xmin=D.index[0], xmax=D.index[-1], ls='-.',  linewidth=2, color='green',zorder=4,label='mean volume')
        fig.autofmt_xdate()

        #--- polish grafx ---
        plt.suptitle(Title, fontsize=25, fontweight='bold')
        ax[0].legend(); ax[1].legend();
        plt.grid('on');
        fig.tight_layout();
        #plt.show()
        return fig, ax


#MMMMMMMMM MAIN MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
def main():
    st.title("Aicebear STOXX analysis")

    #---- Auswahl der Aktien ---------
    SharesList = ['AAPL', 'SWGAY', 'ZM', 'TUI1.DE',  'GOOGL','FCAU']
    # Apple, Swatch, Zoom-Videokonferenz, TUI Reiseunternehmen, Fiat-Chrysler
    Shares  = ['AAPL','TUI1.DE']

#---- Datenzeitfenster auswählen ------------------ -------------------------
    if True:
        TodayDate  = datetime.date.today()                   # heute
        st.write("The date today is: ", TodayDate)
        #----
        st.write("**Enter END date you wish**  (The end date is given as  =  TODAY    - number of days backward) **:**")
        dE = st.slider('number of days backward',max_value=2*365)
        EndDate = TodayDate - pd.DateOffset(dE)               # letzer Tag, der zu lesen ist
        st.write("the choosen end date is:",  EndDate)
        #----
        st.write("**Enter START date you wish**  (The start date is given as  =  END date - number of days backward) **:**")
        dB = st.slider('number of days backward', min_value=93, max_value=5*365)
        BeginDate = EndDate - pd.DateOffset(dB)                # Anz. Tage zurück # 1200  700
        st.write("the choosen start date is: ", BeginDate)

    for share in Shares:
        #---- Datenzeitfenster auswählen ------------------ -------------------------
        D,Title = read_stock_data(share,BeginDate, EndDate)
        #st.write(share)
        #st.write(D.head())   # die ersten Datenzeilen
        #fig, ax = plot_data(D,Title)                              # einfacher Linien-Plot
        fig, ax = plot_volatility_3(D, nStd=2, Title=Title)
        st.write(fig)

if __name__ == '__main__':
	main()