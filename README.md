# Raydium Liquidity Remover
This script will allow you to remove LP within seconds rather than waiting for minutes on raydium for any token.


# Requirements
1. RPC Provider Http(s) URL
2. Kokiez API key to fetch pool keys.
3. Wallet private key.
4. Pool id.
5. Python version greater than or equal to 3.12.

# Getting started
1. Clone the repo

    ```
   git clone https://github.com/kokiez/raydium-liquidity-remover
   
   cd raydium-liquidity-remover
   ```
   
      ### OR
   
   Download the repo by clicking on green button `code` > `download zip`. Then `Unzip`/`Extract` it.

3. Install Requirements
 `pip install -r requirements.txt`

4. Edit the config.ini...
5. Run main.py by the following command:
 `python main.py`
6. Enter your wallet private key and pool id, the program will remove total LP

# Proof and Speed of working:
**Tested on simple sol/usdc and atlas/sol pairs:**
![1](https://github.com/kokiez/raydium-liquidity-remover/assets/105941365/cdc5ad00-b7e4-44bb-9543-301361ac6d8f)

# Kokiez API Pricing:
  1) 10$ for 5 days 
  2) 30$ for 30 days

# Contact
For business inquiries, please contact us at:
 - Telegram: `kokiez4000`
 
**Note:** The contact is not for customer support but rather business inquiries.
# Donations

Solana address: `4nyNbPDTG7qAcfGpcTSuD7i9gD6L4URarkh5RcPfw1mW`


# Disclaimer
Please note that this code is for educational purposes, I will not be responsible if any of my codes are used for illegal purposes.


# FAQ
1. I received an error stating module "blabla" not found. Simply copy the error to bing chat and say how to fix this error.
2. The program gave me an error saying market program id mismatch at the time of sending txn. Solution: goto `utils` > `constants` and read what is written there about a [**SERUM_PROGRAM_ID**](https://github.com/kokiez/raydium-liquidity-remover/blob/main/utils/constants.py#L19).

# References

1. https://github.com/raydium-io/raydium-sdk
2. https://github.com/raydium-io/raydium-frontend
3. https://michaelhly.com/solana-py/
4. https://kevinheavey.github.io/solders/index.html


