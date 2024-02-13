from spl.token.instructions import (
    create_associated_token_account,
    get_associated_token_address,
)

from solders.pubkey import Pubkey
from solders.instruction import Instruction

from solana.rpc.types import TokenAccountOpts
from solana.transaction import AccountMeta

from utils.layouts import LIQ_LAYOUT
from utils.constants import AMM_PROGRAM_ID, SERUM_PROGRAM_ID, withdrawQueue, lpVault

import time, os, sys
from configparser import ConfigParser
import http.client
import json


config = ConfigParser()
config.read(os.path.join(sys.path[0], "data", "config.ini"))
AUTH = config.get("KOKIEZ_API", "auth_key")


async def make_liquidity_remover_instruction(
    payer_pk, Lp_account, quoteAccount, BaseAccount, accounts, TOKEN_PROGRAM_ID, amount
):

    keys = [
        #     // system
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        #     // amm
        AccountMeta(pubkey=accounts["amm_id"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["authority"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["open_orders"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["target_orders"], is_signer=False, is_writable=True
        ),
        AccountMeta(pubkey=accounts["lp_mint"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["base_vault"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["quote_vault"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=withdrawQueue, is_signer=False, is_writable=True),
        AccountMeta(pubkey=lpVault, is_signer=False, is_writable=True),
        #     // market
        AccountMeta(pubkey=SERUM_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["market_id"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["market_base_vault"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["market_quote_vault"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["market_authority"], is_signer=False, is_writable=False
        ),
        #     // user
        AccountMeta(pubkey=Lp_account, is_signer=False, is_writable=True),
        AccountMeta(pubkey=BaseAccount, is_signer=False, is_writable=True),
        AccountMeta(pubkey=quoteAccount, is_signer=False, is_writable=True),
        AccountMeta(pubkey=payer_pk, is_signer=True, is_writable=False),
        #     // market
        AccountMeta(pubkey=accounts["event_queue"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["bids"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["asks"], is_signer=False, is_writable=True),
    ]
    data = LIQ_LAYOUT.build(dict(instruction=4, amount_in=amount))
    return Instruction(AMM_PROGRAM_ID, data, keys)



async def sell_get_token_account(
    ctx, owner: Pubkey.from_string, mint: Pubkey.from_string
):
    try:
        account_data = await ctx.get_token_accounts_by_owner(
            owner, TokenAccountOpts(mint)
        )
        return account_data.value[0].pubkey
    except:
        return "Mint Token Not found"


async def fetch_pool_keys(pair_address: str):
    """Get it via kokiez api"""
    try:
        if pair_address != None:
            a = time.time()

            conn = http.client.HTTPSConnection("www.kokiez.com")
            headers = {"Auth": AUTH}
            conn.request("GET", f"/api/v1/{pair_address}", headers=headers)
            res = conn.getresponse()
            amm_info = json.loads(res.read().decode())

            if (
                amm_info != None
                and "error" not in str(amm_info)
                and "Too Many Requests" not in str(amm_info)
            ):
                print("Total time taken (seconds) to get pool keys: ", time.time() - a)
                return {
                    "amm_id": Pubkey.from_string(amm_info["amm_id"]),
                    "authority": Pubkey.from_string(amm_info["authority"]),
                    "base_mint": Pubkey.from_string(amm_info["base_mint"]),
                    "base_decimals": amm_info["base_decimals"],
                    "quote_mint": Pubkey.from_string(amm_info["quote_mint"]),
                    "quote_decimals": amm_info["quote_decimals"],
                    "lp_mint": Pubkey.from_string(amm_info["lp_mint"]),
                    "open_orders": Pubkey.from_string(amm_info["open_orders"]),
                    "target_orders": Pubkey.from_string(amm_info["target_orders"]),
                    "base_vault": Pubkey.from_string(amm_info["base_vault"]),
                    "quote_vault": Pubkey.from_string(amm_info["quote_vault"]),
                    "market_id": Pubkey.from_string(amm_info["market_id"]),
                    "market_base_vault": Pubkey.from_string(
                        amm_info["market_base_vault"]
                    ),
                    "market_quote_vault": Pubkey.from_string(
                        amm_info["market_quote_vault"]
                    ),
                    "market_authority": Pubkey.from_string(
                        amm_info["market_authority"]
                    ),
                    "bids": Pubkey.from_string(amm_info["bids"]),
                    "asks": Pubkey.from_string(amm_info["asks"]),
                    "event_queue": Pubkey.from_string(amm_info["event_queue"]),
                    "pool_open_time": amm_info["pool_open_time"],
                }

    except:
        return "failed"






async def get_token_account(ctx, owner: Pubkey.from_string, mint: Pubkey.from_string):
    try:
        account_data = await ctx.get_token_accounts_by_owner(
            owner, TokenAccountOpts(mint)
        )
        return account_data.value[0].pubkey, None
    except:
        swap_associated_token_address = get_associated_token_address(owner, mint)
        swap_token_account_Instructions = create_associated_token_account(
            owner, owner, mint
        )
        return swap_associated_token_address, swap_token_account_Instructions