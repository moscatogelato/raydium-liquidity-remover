from typing import Tuple
import solders.system_program as sp
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price


import spl.token.instructions as spl_token
from spl.token._layouts import ACCOUNT_LAYOUT
from spl.token.constants import WRAPPED_SOL_MINT
from spl.token.client import Token

from solana.rpc.commitment import Commitment
from solana.rpc.types import TxOpts
from solana.transaction import Transaction
from configparser import ConfigParser
import os, sys

config = ConfigParser()


def create_account_with_seed_args(
    ctx,
    program_id: Pubkey,
    owner: Pubkey,
    payer: Keypair,
    amount: int,
    skip_confirmation: bool,
    commitment: Commitment,
) -> Tuple[Pubkey, Transaction, Keypair, Keypair, TxOpts]:

    config.read(os.path.join(sys.path[0], "data", "config.ini"))
    GAS_PRICE = config.getint("GAS", "limit")
    GAS_LIMIT = config.getint("GAS", "price")

    new_keypair = Keypair()
    seed_str = str(new_keypair.pubkey())[0:32]

    seed_pk = Pubkey.create_with_seed(payer.pubkey(), seed_str, program_id)
    amount = Token.get_min_balance_rent_for_exempt_for_account(ctx)

    txn = Transaction(fee_payer=payer.pubkey())

    """
        Gas and shit
        """
    txn.add(set_compute_unit_price(GAS_PRICE))
    txn.add(set_compute_unit_limit(GAS_LIMIT))

    txn.add(
        sp.create_account_with_seed(
            sp.CreateAccountWithSeedParams(
                from_pubkey=payer.pubkey(),
                to_pubkey=seed_pk,
                base=payer.pubkey(),
                seed=seed_str,
                lamports=amount,
                space=ACCOUNT_LAYOUT.sizeof(),
                owner=program_id,
            )
        )
    )

    txn.add(
        spl_token.initialize_account(
            spl_token.InitializeAccountParams(
                account=seed_pk,
                mint=WRAPPED_SOL_MINT,
                owner=owner,
                program_id=program_id,
            )
        )
    )

    return (
        seed_pk,
        txn,
        payer,
        new_keypair,
        TxOpts(skip_confirmation=skip_confirmation, preflight_commitment=commitment),
    )
