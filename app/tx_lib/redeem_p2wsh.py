from Bitbnb.Wallet import Wallet

if __name__ == '__main__':   
    # generated by Bitbnb app when user clicks "reserve"
    txid_with_p2wsh = '100fc7f91ced97bab1c4e54757f56c38be311f14e029ca6ff16a4c892df572bc'
    serial_script = '76a91438e36fc755a30589652fc01830de28bcd58178bd8763ac670313c024b17576a914ad86bcc9e99b6888c9e99019b74caece625fe98c88ac68'

    # from owner's wallet
    wallet = Wallet('bob_wallet', 'jag2k2', 'jeff1229', '169.254.122.179', 18332)
    tx_id = wallet.finalize_reservation(txid_with_p2wsh, serial_script)
    print(tx_id)