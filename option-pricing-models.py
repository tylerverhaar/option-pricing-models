import datetime
import math
from random import gauss
import scipy.stats as si
import numpy as np

#--User Input--#

def error_message(type):
    print('Theres been an error in your entries, please try again')
    user_input(type)

def user_input(type):
    spot = input('Enter spot price:')
    strike = input('Enter strike price:')
    time = input('Enter time to maturity (in years):')
    interest = input('Enter interest rate (as decimal):')
    volatility = input('Enter volatility of underlying asset:')
    L = [spot, strike, time, interest, volatility]
    try:
        L = list(map(lambda x: float(x), L))
    except:
        error_message(type)
    if type == 1:
        #Dividend paying option case
        dividend = input('If continuous dividend, enter amount, otherwise hit "Enter":')
        if dividend == '':
            dividend = '0'
            try:
                L.append(float(dividend))
            except:
                error_message(type)
    if type == 2:
        # Number of simulations for Monte Carlo
        simulations = input('Enter number of simulations: ')
        try:
            L.append(int(simulations))
        except:
            error_message(type)
    if type == 3:
        compounds = input('Enter number of compounding periods')
        try:
            L.append(int(compounds))
        except:
            error_message(type)

    return L

#-----------------------------------------------------------------------------#

#--Black-Scholes--#

def euro(s, k, t, r, o, corp):
    d1 = (np.log(s / k) + (r + 0.5 * o ** 2) * t) / (o * np.sqrt(t))
    d2 = (np.log(s / k) + (r - 0.5 * o ** 2) * t) / (o * np.sqrt(t))
    if corp == 'call':
        result = (s * si.norm.cdf(d1, 0.0, 1.0) - k * np.exp(-r * t) 
                  * si.norm.cdf(d2, 0.0, 1.0))
    if corp == 'put':
        result = (k * np.exp(-r * t) * si.norm.cdf(-d2, 0.0, 1.0) - s 
                  * si.norm.cdf(-d1, 0.0, 1.0))
    return result

def euro_with_dividend(s, k, t, r, d, o, corp):
    d1 = (np.log(s / k) + (r - d + 0.5 * o ** 2) * t) / (o * np.sqrt(t))
    d2 = (np.log(s / k) + (r - d - 0.5 * o ** 2) * t) / (o * np.sqrt(t))
    if corp == 'call':
        result = (s * np.exp(-d * t) * si.norm.cdf(d1, 0.0, 1.0) - k 
                  * np.exp(-r * t) * si.norm.cdf(d2, 0.0, 1.0))
    if corp == 'put':
        result = (s * np.exp(-r * t) * si.norm.cdf(-d2, 0.0, 1.0) - s 
                  * np.exp(-d * t) * si.norm.cdf(-d1, 0.0, 1.0))
    return result

def black_scholes_model():
    L = user_input(1)
    # L[0] is spot
    # L[1] is strike
    # L[2] time (years)
    # L[3] interest
    # L[4] dividend
    # L[5] volatility
    corp = input('Enter option type, "call" or "put":')
    value = 0
    if L[4] != 0:
        value = euro_with_dividend(L[0], L[1], L[2], L[3], L[4], L[5], corp)
    else:
        value = euro(L[0], L[1], L[2], L[3], L[5], corp)
    print('Black-Scholes evaluates to %.4f' % value)
    option_pricing()

#-----------------------------------------------------------------------------#

#--Monte-Carlo--#

def asset_price(s,v,r,t):
    return s * math.exp((r - 0.5 * v**2) * t + v * math.sqrt(t) * gauss(0,1.0))

def monte_carlo_calculator(L):
    listofpayoffs = []
    for i in range(0,L[5]):

        st = asset_price(L[0],L[4],L[3],L[2])   
        listofpayoffs.append(max(0.0,(st-L[1])))
    return (math.exp(-L[3] * L[2])) * (sum(listofpayoffs) / float(L[5]))

def monte_carlo_model():
    L = user_input(2)
    # L[0] is spot
    # L[1] is strike
    # L[2] time (years)
    # L[3] interest
    # L[4] volatility
    # L[5] simulations
    value = monte_carlo_calculator(L)
    print( 'Monte-Carlo evaluates to: %.4f' % value)
    option_pricing()
        
#-----------------------------------------------------------------------------#

#--Binomial--#

def create_recurrsive_tree(u,d,n,leaflist,counter):
    if n <= counter:
        return leaflist    
    newleaflist = []
    for i in range(0,len(leaflist)):
        newleaflist.append(leaflist[i]*u)
        newleaflist.append(leaflist[i] * d)
    counter += 1
    return create_recurrsive_tree(u,d,n,newleaflist,counter)

def calculate_option_values(tree,strike,corp):
    if corp == 'call':
        return list(map(lambda x: max(x-strike,0),tree))
    else:
        return list(map(lambda x: max(strike-x, 0), tree))

def calculate_up_factor(t,o):
    return math.exp(o*math.sqrt(t))

def binomial_model():
    L = user_input(3)
    # L[0] is spot
    # L[1] is strike
    # L[2] time (years)
    # L[3] interest
    # L[4] volatility
    # L[5] compounding periods
    corp = input('Enter option type, "call" or "put":')
    u = calculate_up_factor(L[2],L[4])
    price_tree_leaves = create_recurrsive_tree(u,u**(-1),L[5],[L[0]],0)
    final_option_values = calculate_option_values(price_tree_leaves,L[1],corp)
    p = (math.exp(L[3]*(L[2]/L[5])))/(u-(u**(-1)))
    probability_tree_leaves = create_recurrsive_tree(p,1-p,L[5],[1],0)
    probability_times_discounting_leaves = list(
        map(lambda x: x*(math.exp(-L[3]*(L[2]/L[5]))),probability_tree_leaves))
    expected_value = sum(
        list(map(lambda x,y:x*y,probability_times_discounting_leaves,final_option_values)))
    print('Binomial Pricing Model evaluates to: %.4f' % expected_value)
    option_pricing()



#-----------------------------------------------------------------------------#

#--Option Pricing Models--#

def option_pricing():
    s = input('Please select which pricing model you would like to use: \n1 Black-Scholes\n2 Monte Carlo\n3 Binomial\n')
    if s == '1':
        black_scholes_model()
    elif s == '2':
        monte_carlo_model()
    elif s == '3':
        binomial_model()
    else:
        option_pricing()
        

option_pricing()