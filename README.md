This is a python program for spotting triangular arbitrage opportunities on Binance DEX. It can be modified to spot opportunities on other DEXs too.

Information about Binance API can be found under https://binance-docs.github.io/apidocs/spot/en/#general-info.

This program will only spot and show TriArb opportunities, use it at your own risk.

In order to use the program for the very first time:

1. Update tradeable token list.
2. Update structured pair list. This step will generate a json file with the structured pairs (Check the example file).
3. Update tradeable structured pair list. This step will generate a json file with the structured pairs that are live trading (Check the example file).

Once you have updated tradeable structured pair list (Step 2 and 3), there is no need to run them again until Binance adds a new trading pair.

Note 1: Step 2 will take a few minutes to complete.
Note 2: In order to update tradeable structured pair list you need to run Step 1 first.