from brivas_security import require_3fish_auth

class CryptoAgent:
    @require_3fish_auth
    def transfer_bitcoin(self, amount, address):
        print(f"💰 Initiating transfer of {amount} BTC to {address}")
        return True

if __name__ == "__main__":
    agent = CryptoAgent()
    try:
        agent.transfer_bitcoin(5.85, "bc1q_test_wallet")
    except Exception as e:
        print(f"Aborted: {e}")
