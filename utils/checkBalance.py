from solders.pubkey import Pubkey
from solana.rpc.types import TokenAccountOpts
import time


async def getBalance(mint, solana_client, payer):
    balanceBool = True
    while balanceBool:
        try:
            tokenPk = mint

            accountProgramId = await solana_client.get_account_info_json_parsed(tokenPk)
            programid_of_token = accountProgramId.value.owner

            accounts = (
                await solana_client.get_token_accounts_by_owner_json_parsed(
                    payer.pubkey(), TokenAccountOpts(program_id=programid_of_token)
                )
            ).value
            for account in accounts:
                mint_in_acc = account.account.data.parsed["info"]["mint"]
                if mint_in_acc == str(mint):
                    amount_in = int(
                        account.account.data.parsed["info"]["tokenAmount"]["amount"]
                    )
                    break
            if int(amount_in) > 0:
                balanceBool = False
            else:
                print("No Balance, Retrying...")
                time.sleep(0.5)
        except Exception as e:
            pass

    return amount_in
