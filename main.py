from solders.keypair import Keypair

from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment
from raydium.liquidity_remover import remove
from configparser import ConfigParser
import os, sys, asyncio, base58

config = ConfigParser()
config.read(os.path.join(sys.path[0], "data", "config.ini"))
RPC_HTTPS_URL = config.get("RPC_URL", "rpc_url")


async def main():
    private_key = input("Enter your wallet private key: ")

    while True:

        pool_id = input("Enter the pool id (pool id, pair address, amm id are same things): ")

        payer = Keypair.from_bytes(base58.b58decode(private_key))

        # # Solana Client Initialization
        ctx = AsyncClient(
            RPC_HTTPS_URL,
            commitment=Commitment("confirmed"),
            timeout=30,
            blockhash_cache=True,
        )
        print()

        txn = await remove(ctx, pool_id, payer)

        if txn != "failed":
            print(f"https://solscan.io/tx/{txn}\n")
        else:
            print("Unkown error occured\n")

        print("="*50)
        print("="*50)



if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
