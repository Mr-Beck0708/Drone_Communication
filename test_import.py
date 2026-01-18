
try:
    from src.crypto.kyber import KyberKEM
    print("KyberKEM imported successfully")
    k = KyberKEM()
    print("KyberKEM instantiated")
    print(f"OQS Available: {hasattr(k, 'kem') and k.kem is not None}")
except Exception as e:
    print(f"Caught exception: {e}")
    import traceback
    traceback.print_exc()
