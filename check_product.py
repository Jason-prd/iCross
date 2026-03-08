import requests

BASE = 'http://127.0.0.1:8000'

# Login first
login_data = {'username': 'admin@icross.com', 'password': 'admin123'}
r = requests.post(f'{BASE}/api/v1/auth/login', data=login_data)
if r.status_code == 200:
    token = r.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # Get products
    r = requests.get(f'{BASE}/api/v1/ozon/db/products?limit=5', headers=headers)
    if r.status_code == 200:
        data = r.json()
        products = data.get('data', [])
        print(f"Total products: {len(products)}")
        
        # Find specific product
        target_offer_id = "SKU#0523235411-1-0"
        for product in products:
            if target_offer_id in product.get('offer_id', ''):
                print(f"\n=== Product: {product.get('offer_id')} ===")
                for key, value in product.items():
                    print(f"  {key}: {repr(value)[:100]}")
                break
        else:
            # Print first product fields
            print("\n=== First Product Fields ===")
            for key, value in products[0].items():
                print(f"  {key}: {type(value).__name__}")
