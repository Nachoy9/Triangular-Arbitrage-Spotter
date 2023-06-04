# Program Logic

import requests
import json
import time

exchange_tokens_info = "https://api.binance.com/api/v3/exchangeInfo"
exchange_tokens_prices = "https://api.binance.com/api/v3/ticker/bookTicker"

nowFormat = "%Y-%m-%d %H:%M:%S"

#This function will request data from the desired API
def get_request(url):

    req = requests.get(url)
    json_resp = json.loads(req.text)

    return json_resp

# This function will get the pairs with "TRADING" status
def get_tradeable_tokens():

    print("Updating tradeable token list")

    token_list = get_request(exchange_tokens_info)

    tokens_symbols = token_list["symbols"]
    tradeable_tokens = []

    for element in tokens_symbols:

        tradeable = element["status"]

        if tradeable == "TRADING":
            tradeable_tokens.append(element["symbol"])

    return tradeable_tokens

# This function will structure the list of pairs by building the triage of pairs
def structure_triangular_pairs():

    print("Structuring list")

    remove_duplicate_list = []
    triangular_pairs_list = []
    token_list = get_request(exchange_tokens_info)
    token_symbols = token_list["symbols"]

    # Pair A
    for pairA in token_symbols:

        pairA_base = pairA["baseAsset"]
        pairA_quote = pairA["quoteAsset"]
        A_pair_box = [pairA_base, pairA_quote]

        # Pair B
        for pairB in token_symbols:

            pairB_base = pairB["baseAsset"]
            pairB_quote = pairB["quoteAsset"]

            if pairB["symbol"] != pairA["symbol"]:

                if pairB_base in A_pair_box or pairB_quote in A_pair_box:

                    # Pair C
                    for pairC in token_symbols:

                        pairC_base = pairC["baseAsset"]
                        pairC_quote = pairC["quoteAsset"]

                        if pairC["symbol"] != pairA["symbol"] and pairC["symbol"] != pairB["symbol"]:

                            pair_box = [pairA_base, pairA_quote, pairB_base, pairB_quote, pairC_base, pairC_quote]
                            combine_all = [pairA["symbol"], pairB["symbol"], pairC["symbol"]]

                            counts_pairC_quote = 0

                            for i in pair_box:
                                if i == pairC_quote:
                                    counts_pairC_quote += 1

                            counts_pairC_base = 0

                            for i in pair_box:
                                if i == pairC_base:
                                    counts_pairC_base += 1

                            if counts_pairC_base == 2 and counts_pairC_quote == 2 and pairC_base != pairC_quote:

                                combined = pairA["symbol"] + "," + pairB["symbol"] + "," + pairC["symbol"]
                                unique_item = ''.join(sorted(combine_all))

                                if unique_item not in remove_duplicate_list:

                                    match_dict = {
                                        "pairA_base": pairA_base,
                                        "pairB_base": pairB_base,
                                        "pairC_base": pairC_base,
                                        "pairA_quote": pairA_quote,
                                        "pairB_quote": pairB_quote,
                                        "pairC_quote": pairC_quote,
                                        "pairA": pairA["symbol"],
                                        "pairB": pairB["symbol"],
                                        "pairC": pairC["symbol"],
                                        "combined": combined
                                    }

                                    remove_duplicate_list.append(unique_item)
                                    triangular_pairs_list.append(match_dict)

                                    print("Saving:", combined)

    with open("structured_triangular_pairs.json", "w") as fp:
        json.dump(triangular_pairs_list, fp)

# This function will keep only those pairs with "TRADING" status
def get_tradeable_structured_pairs(tradeable_tokens):

    with open("structured_triangular_pairs.json") as json_file:
        structured_pairs = json.load(json_file)

    tradeable_structured_pairs = []

    for triangular_pair in structured_pairs:

        if triangular_pair["pairA"] in tradeable_tokens and triangular_pair["pairB"] in tradeable_tokens and triangular_pair["pairC"] in tradeable_tokens:
            tradeable_structured_pairs.append(triangular_pair)

    with open("tradeable_structured_triangular_pairs.json", "w") as fp:
        json.dump(tradeable_structured_pairs, fp)

# This function will spot arbitrage opportunities for X as pair quote
def spot_arbitrage_opportunities_xcoin_quote(coin):

    coin_exist = False

    with open("tradeable_structured_triangular_pairs.json") as json_file:
        tradeable_structured_pairs = json.load(json_file)

    token_prices = get_request(exchange_tokens_prices)

    for triangular_pairs in tradeable_structured_pairs:

        if triangular_pairs["pairA_quote"] == coin:

            coin_exist = True

            pair_prices = get_prices(triangular_pairs, token_prices)
            surface_arb = calc_triangular_arb_surface_rate(triangular_pairs, pair_prices)

            if len(surface_arb) > 0:
                real_rate_arb =calc_orderbook_depth(surface_arb)
                print(real_rate_arb)

                # Pause so we don't saturate the API
                # time.sleep(0.1)

    if not coin_exist:
        print(coin,"does not exist.")

# This function will spot arbitrage opportunities for X as pair base
def spot_arbitrage_opportunities_xcoin_base(coin):

    coin_exist = False

    with open("tradeable_structured_triangular_pairs.json") as json_file:
        tradeable_structured_pairs = json.load(json_file)

    token_prices = get_request(exchange_tokens_prices)

    for triangular_pairs in tradeable_structured_pairs:

        if triangular_pairs["pairA_base"] == coin:

            coin_exist = True

            pair_prices = get_prices(triangular_pairs, token_prices)
            surface_arb = calc_triangular_arb_surface_rate(triangular_pairs, pair_prices)

            if len(surface_arb) > 0:
                real_rate_arb =calc_orderbook_depth(surface_arb)
                print(real_rate_arb)

                # Pause so we don't saturate the API
                # time.sleep(0.1)

    if not coin_exist:
        print(coin,"does not exist.")

# This function will get the price relation of each pair
def get_prices(triangular_pairs, token_prices):

    pairA = triangular_pairs["pairA"]
    pairB = triangular_pairs["pairB"]
    pairC = triangular_pairs["pairC"]

    for element in token_prices:

        if element["symbol"] == pairA:

            pairA_ask = float(element["askPrice"])
            pairA_bid = float(element["bidPrice"])

        elif element["symbol"] == pairB:

            pairB_ask = float(element["askPrice"])
            pairB_bid = float(element["bidPrice"])

        elif element["symbol"] == pairC:

            pairC_ask = float(element["askPrice"])
            pairC_bid = float(element["bidPrice"])

    return {
        "pairA_ask": pairA_ask,
        "pairA_bid": pairA_bid,
        "pairB_ask": pairB_ask,
        "pairB_bid": pairB_bid,
        "pairC_ask": pairC_ask,
        "pairC_bid": pairC_bid,
    }

# This function will calculate the surface rate
def calc_triangular_arb_surface_rate(triangular_pairs, pair_prices):

    starting_ammount = 1
    min_surface_rate = 0
    surface_dict = {}
    contract_2 = ""
    contract_3 = ""
    direction_trade_1 = ""
    direction_trade_2 = ""
    direction_trade_3 = ""
    acquired_coin_t2 = 0
    acquired_coin_t3 = 0
    calculated = 0

    pairA_base = triangular_pairs["pairA_base"]
    pairA_quote = triangular_pairs["pairA_quote"]

    pairB_base = triangular_pairs["pairB_base"]
    pairB_quote = triangular_pairs["pairB_quote"]

    pairC_base = triangular_pairs["pairC_base"]
    pairC_quote = triangular_pairs["pairC_quote"]

    pairA = triangular_pairs["pairA"]
    pairB = triangular_pairs["pairB"]
    pairC = triangular_pairs["pairC"]

    pairA_ask = pair_prices["pairA_ask"]
    pairA_bid = pair_prices["pairA_bid"]

    pairB_ask = pair_prices["pairB_ask"]
    pairB_bid = pair_prices["pairB_bid"]

    pairC_ask = pair_prices["pairC_ask"]
    pairC_bid = pair_prices["pairC_bid"]

    direction_list = ["forward", "reverse"]

    for direction in direction_list:

        swap_1 = 0
        swap_2 = 0
        swap_3 = 0
        swap_1_rate = 0
        swap_2_rate = 0
        swap_3_rate = 0
        contract_1 = pairA

        if direction == "forward":

            swap_1 = pairA_base
            swap_2 = pairA_quote
            swap_1_rate = 1 * pairA_ask
            direction_trade_1 = "base_to_quote"

        elif direction == "reverse":

            swap_1 = pairA_quote
            swap_2 = pairA_base
            swap_1_rate = 1 / pairA_bid
            direction_trade_1 = "quote_to_base"

        acquired_coin_t1 = starting_ammount * swap_1_rate

        if direction == "forward":

            if pairA_quote == pairB_base and calculated == 0:

                swap_2_rate = 1 * pairB_bid
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "base_to_quote"
                contract_2 = pairB

                if pairB_quote == pairC_base:

                    swap_3 = pairC_base
                    swap_3_rate = 1 * pairC_bid
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pairC

                elif pairB_quote == pairC_quote:
                    swap_3 = pairC_quote
                    swap_3_rate = 1 / pairC_ask
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pairC

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

            if pairA_quote == pairB_quote and calculated == 0:

                swap_2_rate = 1 / pairB_ask
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "quote_to_base"
                contract_2 = pairB

                if pairB_base == pairC_base:

                    swap_3 = pairC_base
                    swap_3_rate = 1 * pairC_bid
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pairC

                elif pairB_base == pairC_quote:

                    swap_3 = pairC_quote
                    swap_3_rate = 1 / pairC_ask
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pairC

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

            if pairA_quote == pairC_base and calculated == 0:

                swap_2_rate = 1 * pairC_bid
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "base_to_quote"
                contract_2 = pairC

                if pairC_quote == pairB_base:

                    swap_3 = pairB_base
                    swap_3_rate = 1 * pairB_bid
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pairB

                elif pairC_quote == pairB_quote:
                    swap_3 = pairB_quote
                    swap_3_rate = 1 / pairB_ask
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pairB

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

            if pairA_quote == pairC_quote and calculated == 0:

                swap_2_rate = 1 / pairC_ask
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "quote_to_base"
                contract_2 = pairC

                if pairC_base == pairB_base:

                    swap_3 = pairB_base
                    swap_3_rate = 1 * pairB_bid
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pairB

                elif pairC_base == pairB_quote:
                    swap_3 = pairB_quote
                    swap_3_rate = 1 / pairB_ask
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pairB

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

        if direction == "reverse":

            if pairA_base == pairB_base and calculated == 0:

                swap_2_rate = 1 * pairB_bid
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "base_to_quote"
                contract_2 = pairB

                if pairB_quote == pairC_base:

                    swap_3 = pairC_base
                    swap_3_rate = 1 * pairC_bid
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pairC

                elif pairB_quote == pairC_quote:

                    swap_3 = pairC_quote
                    swap_3_rate = 1 / pairC_ask
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pairC

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

            if pairA_base == pairB_quote and calculated == 0:

                swap_2_rate = 1 / pairB_ask
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "quote_to_base"
                contract_2 = pairB

                if pairB_base == pairC_base:

                    swap_3 = pairC_base
                    swap_3_rate = 1 * pairC_bid
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pairC

                elif pairB_base == pairC_quote:

                    swap_3 = pairC_quote
                    swap_3_rate = 1 / pairC_ask
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pairC

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

            if pairA_base == pairC_base and calculated == 0:

                swap_2_rate = 1 * pairC_bid
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "base_to_quote"
                contract_2 = pairC

                if pairC_quote == pairB_base:

                    swap_3 = pairB_base
                    swap_3_rate = 1 * pairB_bid
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pairB

                elif pairC_quote == pairB_quote:

                    swap_3 = pairB_quote
                    swap_3_rate = 1 / pairB_ask
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pairB

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

            if pairA_base == pairC_quote and calculated == 0:

                swap_2_rate = 1 / pairC_ask
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "quote_to_base"
                contract_2 = pairC

                if pairC_base == pairB_base:

                    swap_3 = pairB_base
                    swap_3_rate = 1 * pairB_bid
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pairB

                elif pairC_base == pairB_quote:

                    swap_3 = pairB_quote
                    swap_3_rate = 1 / pairB_ask
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pairB

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

        pnl = acquired_coin_t3 - starting_ammount
        pnl_percentage = (pnl / starting_ammount) * 100 if pnl != 0 else 0

        trade_desc_1 = f"Start with {starting_ammount} {swap_1}. Swap at {swap_1_rate} for {swap_2} acquiring {acquired_coin_t1}"
        trade_desc_2 = f"Start with {acquired_coin_t1} {swap_2}. Swap at {swap_2_rate} for {swap_3} acquiring {acquired_coin_t2}"
        trade_desc_3 = f"Start with {acquired_coin_t2} {swap_3}. Swap at {swap_3_rate} for {swap_1} acquiring {acquired_coin_t3}"

        if pnl_percentage > min_surface_rate:
            surface_dict = {
                "swap_1": swap_1,
                "swap_2": swap_2,
                "swap_3": swap_3,
                "contract_1": contract_1,
                "contract_2": contract_2,
                "contract_3": contract_3,
                "direction_trade_1": direction_trade_1,
                "direction_trade_2": direction_trade_2,
                "direction_trade_3": direction_trade_3,
                "starting_amount": starting_ammount,
                "acquired_coin_t1": acquired_coin_t1,
                "acquired_coin_t2": acquired_coin_t2,
                "acquired_coin_t3": acquired_coin_t3,
                "swap_1_rate": swap_1_rate,
                "swap_2_rate": swap_2_rate,
                "swap_3_rate": swap_3_rate,
                "pnl_perc": pnl_percentage,
                "direction": direction,
                "trade_description_1": trade_desc_1,
                "trade_description_2": trade_desc_2,
                "trade_description_3": trade_desc_3,
            }

            # Exit if we spot an opportunity
            return surface_dict

    return surface_dict

# This function will calculate the orderbook depth
def calc_orderbook_depth(surface_arb):

    swap_1 = surface_arb["swap_1"]

    starting_amount = 100

    contract_1 = surface_arb["contract_1"]
    contract_2 = surface_arb["contract_2"]
    contract_3 = surface_arb["contract_3"]

    contract_1_direction = surface_arb["direction_trade_1"]
    contract_2_direction = surface_arb["direction_trade_2"]
    contract_3_direction = surface_arb["direction_trade_3"]

    url1 = f"https://api.binance.com/api/v3/depth?symbol={contract_1}&limit=750"
    depth_1_prices = get_request(url1)
    depth_1_ref_prices = ref_orderbook(depth_1_prices, contract_1_direction)

    # time.sleep(0.1)

    url2 = f"https://api.binance.com/api/v3/depth?symbol={contract_2}&limit=750"
    depth_2_prices = get_request(url2)
    depth_2_ref_prices = ref_orderbook(depth_2_prices, contract_2_direction)

    # time.sleep(0.1)

    url3 = f"https://api.binance.com/api/v3/depth?symbol={contract_3}&limit=750"
    depth_3_prices = get_request(url3)
    depth_3_ref_prices = ref_orderbook(depth_3_prices, contract_3_direction)

    acquired_coin_t1 = calculate_acquired_tokens(starting_amount, depth_1_ref_prices)
    acquired_coin_t2 = calculate_acquired_tokens(acquired_coin_t1, depth_2_ref_prices)
    acquired_coin_t3 = calculate_acquired_tokens(acquired_coin_t2, depth_3_ref_prices)

    pnl = acquired_coin_t3 - starting_amount
    pnl_perc = (pnl/starting_amount) * 100 if pnl != 0 else 0

    print("\n",contract_1,"-",contract_2,"-",contract_3)
    print(surface_arb["contract_2"])
    print(surface_arb["contract_2"])
    print(surface_arb["contract_2"])

    if pnl_perc > 0:
        trade_dict = {
            "pnl": pnl,
            "pnl_perc": pnl_perc,
            "contract_1": contract_1,
            "contract_2": contract_2,
            "contract_3": contract_3,
            "contract_1_dir": contract_1_direction,
            "contract_2_dir": contract_2_direction,
            "contract_3_dir": contract_3_direction
        }
        return trade_dict
    else:
        return "No depth or trade for loss"

def calculate_acquired_tokens(amount_in, ref_depth):

    trading_balance = amount_in
    quantity_bought = 0
    acquired_tokens = 0
    counts = 0

    for level in ref_depth:

        level_price = level[0]
        level_quantity = level[1]

        if trading_balance <= level_quantity:
            quantity_bought = trading_balance
            trading_balance = 0
            amount_out = quantity_bought * level_price

        if trading_balance > level_quantity:
            quantity_bought = level_quantity
            trading_balance -= quantity_bought
            amount_out = quantity_bought * level_price

        acquired_tokens = acquired_tokens + amount_out

        if trading_balance == 0:
            return acquired_tokens

        counts += 1
        if counts == len(ref_depth):
            return 0

def ref_orderbook(prices, direction):

    main_price_list = []

    if direction == "base_to_quote":

        for price in prices["bids"]:

            bid_price = float(price[0])
            adj_price = 1 * bid_price if bid_price != 0 else 0
            adj_quantity = float(price[1])
            main_price_list.append([adj_price, adj_quantity])

    elif direction == "quote_to_base":

        for price in prices["asks"]:

            ask_price = float(price[0])
            adj_price = 1 / ask_price if ask_price != 0 else 0
            adj_quantity = float(price[1])
            main_price_list.append([adj_price, adj_quantity])

    return main_price_list
