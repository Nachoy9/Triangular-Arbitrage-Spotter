# Main Menu

import json
import triarblogic
import os.path
import time

nowFormat = "%Y-%m-%d %H:%M:%S"

stp_path = "structured_triangular_pairs.json"
tstp_path = "tradeable_structured_triangular_pairs.json"

if __name__ == '__main__':

    close = False

    while close is False:

        nowTime = time.strftime(nowFormat, time.localtime())

        if os.path.exists(stp_path):
            last_modified = os.path.getmtime(stp_path)
            last_stp_modified_time = time.strftime(nowFormat, time.localtime(last_modified))
        else:
            last_stp_modified_time = ("N/A")

        if os.path.exists(tstp_path):
            last_modified = os.path.getmtime(tstp_path)
            last_tstp_modified_time = time.strftime(nowFormat, time.localtime(last_modified))
        else:
            last_tstp_modified_time = ("N/A")

        print("\nMain Menu:\n")
        print("Current time:", nowTime, "\n")
        print("1. Update tradeable token list.")
        print("2. Update structured pair list. Last time updated: ", last_stp_modified_time)
        print("3. Update tradeable structured pair list. Last time updated: ", last_tstp_modified_time)
        print("4. Spot opportunities for X coin (base).")
        print("5. Spot opportunities for X coin (quote).")
        print("6. Exit.")

        opc = int(input("\nPick an option: "))

        if opc == 1:
            tradeable_tokens = triarblogic.get_tradeable_tokens()
            print("Tradeable token list has been updated\n")
        elif opc == 2:
            triarblogic.structure_triangular_pairs()
            print("Pair list has been structured\n")
        elif opc == 3:
            triarblogic.get_tradeable_structured_pairs(tradeable_tokens)
            print("Tradeable structured pairs list has been generated\n")
        elif opc == 4:
            coin = input("\nPick a coin: ").upper()
            print("\nLooking for trades with", coin)
            triarblogic.spot_arbitrage_opportunities_xcoin_base(coin)
        elif opc == 5:
            coin = input("\nPick a coin: ").upper()
            print("\nLooking for trades with", coin)
            triarblogic.spot_arbitrage_opportunities_xcoin_quote(coin)
        elif opc == 6:
            print("\nClosing program\n")
            close = True


