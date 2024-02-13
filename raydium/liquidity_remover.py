from spl.token.instructions import close_account, CloseAccountParams
from spl.token.constants import TOKEN_PROGRAM_ID

from solana.rpc.api import RPCException
from solana.rpc.api import Client
from solana.rpc.commitment import Commitment

from utils.seed_acc import create_account_with_seed_args
from utils.make_instructions import (
    fetch_pool_keys,
    sell_get_token_account,
    make_liquidity_remover_instruction,
)
from utils.checkBalance import getBalance

from configparser import ConfigParser
import time, os, sys


config = ConfigParser()
config.read(os.path.join(sys.path[0], "data", "config.ini"))
RPC_HTTPS_URL = config.get("RPC_URL", "rpc_url")

solana_client_non_async = Client(
    RPC_HTTPS_URL,
    commitment=Commitment("confirmed"),
    timeout=30,
    blockhash_cache=True,
)


async def remove(solana_client, amm_id, payer):

    pool_keys = await fetch_pool_keys(amm_id)

    if pool_keys == "failed":
        print("Failed to retrieve pool keys...")
        return "failed"

    txnBool = True
    while txnBool:
        try:
            # Get lp balance
            amount_in = await getBalance(pool_keys["lp_mint"], solana_client, payer)

            # get token program id for mint
            TOKEN_PROGRAM_ID_MINT = None
            if (
                str(pool_keys["base_mint"])
                == "So11111111111111111111111111111111111111112"
            ):
                accountProgramId = await solana_client.get_account_info_json_parsed(
                    pool_keys["quote_mint"]
                )
                TOKEN_PROGRAM_ID_MINT = accountProgramId.value.owner
            else:
                accountProgramId = await solana_client.get_account_info_json_parsed(
                    pool_keys["base_mint"]
                )
                TOKEN_PROGRAM_ID_MINT = accountProgramId.value.owner

            # get lp mint account
            lp_account_pk = await sell_get_token_account(
                solana_client, payer.pubkey(), pool_keys["lp_mint"]
            )

            if (
                str(pool_keys["base_mint"])
                == "So11111111111111111111111111111111111111112"
            ):
                # get quote mint account
                quoteAccount_pk = await sell_get_token_account(
                    solana_client, payer.pubkey(), pool_keys["quote_mint"]
                )

                # get base mint account
                base_token_account_pk, swap_tx, payer, base_account_keyPair, opts = (
                    create_account_with_seed_args(
                        solana_client_non_async,
                        TOKEN_PROGRAM_ID,
                        payer.pubkey(),
                        payer,
                        amount_in,
                        False,
                        "confirmed",
                    )
                )

                # create seed account close instructions
                closeAcc = close_account(
                    CloseAccountParams(
                        account=base_token_account_pk,
                        dest=payer.pubkey(),
                        owner=payer.pubkey(),
                        program_id=TOKEN_PROGRAM_ID,
                    )
                )

            else:

                base_token_account_pk = await sell_get_token_account(
                    solana_client, payer.pubkey(), pool_keys["base_mint"]
                )  # account of liquidity

                quoteAccount_pk, swap_tx, payer, base_account_keyPair, opts = (
                    create_account_with_seed_args(
                        solana_client_non_async,
                        TOKEN_PROGRAM_ID,
                        payer.pubkey(),
                        payer,
                        amount_in,
                        False,
                        "confirmed",
                    )
                )

                closeAcc = close_account(
                    CloseAccountParams(
                        account=quoteAccount_pk,
                        dest=payer.pubkey(),
                        owner=payer.pubkey(),
                        program_id=TOKEN_PROGRAM_ID,
                    )
                )

        
            print("Create Liquidity Instructions...")
            instructions_swap = await make_liquidity_remover_instruction(
                payer.pubkey(),
                lp_account_pk,
                quoteAccount_pk,
                base_token_account_pk,
                pool_keys,
                TOKEN_PROGRAM_ID_MINT,
                amount_in,
            )

            # add instructions to txn
            swap_tx.add(instructions_swap)
            swap_tx.add(closeAcc)
            signers = [payer]
            try:
                print("Execute Transaction...")
                start_time = time.time()

                txn = await solana_client.send_transaction(swap_tx, *signers)
                txid_string_sig = txn.value
                print(f"Transaction Sent: https://solscan.io/tx/{txn.value}")
                end_time = time.time()
                execution_time = end_time - start_time
                print(f"Execution time of send: {execution_time} seconds\n--------------------------------")
                # once txn has been sent, it has already been successful and u can access it on solscan.
                # remaining code is only to confirm if there were any errors in the txn or not.





                print("Getting status of transaction now...")
                checkTxn = True
                while checkTxn:
                    try:
                        status = await solana_client.get_transaction(
                            txid_string_sig, "json"
                        )
                        if status.value.transaction.meta.err == None:
                            print("Transaction Success", txn.value)

                            end_time = time.time()
                            execution_time = end_time - start_time
                            print(f"Total Execution time: {execution_time} seconds")

                            txnBool = False
                            checkTxn = False
                            return txid_string_sig

                        else:
                            print("Transaction Failed")
                            end_time = time.time()
                            execution_time = end_time - start_time
                            print(f"Execution time: {execution_time} seconds")
                            checkTxn = False

                    except Exception as e:
                        time.sleep(0.1)

            except RPCException as e:
                print(f"[Important] Error: [{e.args[0].data.logs}]...\nRetrying...")
                time.sleep(0.1)

            except Exception as e:
                print(f"[Important] Error: [{e}]...\nEnd...")
                txnBool = False
                return "failed"
        except Exception as e:
            if "NoneType" in str(e):
                print(e)
                return "failed"
            print("[Important] Main LP Remove error Raydium... retrying...\n", e)
