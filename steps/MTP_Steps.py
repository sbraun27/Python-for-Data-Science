#import packages
import datetime
import quandl
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy as spy

from behave import given, when, then
################################################################################
quandl.ApiConfig.api_key = 'API key here'
num_securities = -1
num_iterations = -1
tickers = []

@given(u'I am tracking the following tickers')
def step_impl(context):
	model = getattr(context, "model", None)
	for row in context.table:
		tickers.append(row['Name'])
	num_securities = len(tickers)

@then(u'calculate and plot the Efficient frontier over {iterations:d} iterations')
def step_impl(context, iterations):
    num_iterations = iterations


@then(u'I calculate and plot the growth over time')
def step_impl(context):
	ticker_data = quandl.get_table('WIKI/PRICES', ticker = tickers,
                        qopts = { 'columns': ['date', 'ticker', 'adj_close'] },
                        date = { 'gte': '2011-01-01', 'lte': '2018-12-31' }, paginate=True)
	# clean and organize data
	# columns of tickers and their corresponding adjusted prices
	clean_on = ticker_data.set_index('date')
	table_clean = clean_on.pivot(columns='ticker')
	
	# calculate daily and annual returns of the stocks
	returns_daily = table_clean.pct_change()
	returns_annual = returns_daily.mean() * 252
	
	# get daily and annual covariance of returns of the stock
	cov_daily = returns_daily.cov()
	cov_annual = cov_daily * 252
	
	# Create lists to stores returns and volatility data
	port_returns = []
	port_volatility = []
	sharpe_ratio = []
	stock_weights = []
	
	#set random seed for reproduction's sake
	np.random.seed(101)
	
	# populate the empty lists with each portfolios returns,risk and weights
	for single_portfolio in range(num_iterations):
		weights = np.random.random(num_securities)
		weights /= np.sum(weights)
		returns = np.dot(weights, returns_annual)
		volatility = np.sqrt(np.dot(weights.T, np.dot(cov_annual, weights)))
		sharpe = returns / volatility
		sharpe_ratio.append(sharpe)
		port_returns.append(returns)
		port_volatility.append(volatility)
		stock_weights.append(weights)
	
	# a dictionary for Returns and Risk values of each portfolio
	portfolio = {'Returns': port_returns,
				'Volatility': port_volatility,
				'Sharpe Ratio': sharpe_ratio}
	
	# extend original dictionary to accomodate each ticker and weight in the portfolio
	for counter,symbol in enumerate(tickers):
		portfolio[symbol+' Weight'] = [Weight[counter] for Weight in stock_weights]
	
	# make a nice dataframe of the extended dictionary
	df = pd.DataFrame(portfolio)
	
	# get better labels for desired arrangement of columns
	column_order = ['Returns', 'Volatility', 'Sharpe Ratio'] + [stock+' Weight' for stock in tickers]
	
	# reorder dataframe columns
	df = df[column_order]
	
	# find min Volatility & max sharpe values in the dataframe (df)
	min_volatility = df['Volatility'].min()
	max_sharpe = df['Sharpe Ratio'].max()
	
	# use the min, max values to locate and create the two special portfolios
	sharpe_portfolio = df.loc[df['Sharpe Ratio'] == max_sharpe]
	min_variance_port = df.loc[df['Volatility'] == min_volatility]
	
	plt.style.use('seaborn-dark')
	df.plot.scatter(x='Volatility', y='Returns', c='Sharpe Ratio',
					cmap='RdYlGn', edgecolors='black', figsize=(10, 8), grid=True)
	plt.scatter(x=sharpe_portfolio['Volatility'], y=sharpe_portfolio['Returns'], c='red', marker='D', s=100)
	plt.scatter(x=min_variance_port['Volatility'], y=min_variance_port['Returns'], c='blue', marker='D', s=100 )
	plt.xlabel('Volatility (Std. Deviation)')
	plt.ylabel('Historic Annualized Return')
	plt.title('Efficient Frontier')
	plt.show()
	#find the row of max sharpe
	Sharpe_location = df['Sharpe Ratio'].idxmax()
	#find the row of min vol
	min_vol_location = df['Volatility'].idxmax() 
	#create an array of the weights of each portfolio
	Sharpe_Portfolio = df.iloc[Sharpe_location] 
	Sharpe_Weights = np.array(np.transpose(Sharpe_Portfolio[3:]))
	Min_Vol_Portfolio = df.iloc[min_vol_location]
	min_vol_weights = np.array(np.transpose(Min_Vol_Portfolio[3:]))
	
	#run the values of the portfolios over time
	Portolfio_Weights_End = pd.DataFrame(index = ["Min_Vol", 'Max_Sharpe'], columns = column_order[3:],
								data = [min_vol_weights, Sharpe_Weights])
	results = pd.DataFrame(np.dot(table_clean, Portolfio_Weights_End.T), columns=Portolfio_Weights_End.index, index = table_clean.index)
	
	#plot the graph over time
	plt.style.use('seaborn-dark')
	results.plot.line()
	plt.show()