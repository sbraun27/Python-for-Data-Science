Feature: Find lowest volatility and highest sharp ratio for a given set of tickers
  Scenario: Find lowest volatility and highest sharp ratio
    Given I am tracking the following tickers
	  |Name|
	  |AAPL|
	  |GOOG|
	  |AMZN|
	  |F|
	  |GE|
	  |GLD|
	  |NVDA|
	  |MCD|
	  |CAT|
	  |WMT|
	Then calculate and plot the Efficient frontier over 100000 iterations
	I calculate and plot the growth over time