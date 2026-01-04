import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

# 설정 가능한 파라미터
NUM_RECORDS = 100  # 생성할 레코드 수
START_DATE = datetime(2025, 1, 1)  # 시작 날짜
END_DATE = datetime(2025, 12, 31)  # 종료 날짜
ROOT_DIR = Path(__file__).parent.parent
OUTPUT_FILE = ROOT_DIR / 'sales_data_random.csv'  # 출력 파일명

# 제품 데이터 (제품명, 카테고리, 최소가격, 최대가격)
PRODUCTS = [
    ('Laptop', 'Electronics', 1200000, 2000000),
    ('Monitor', 'Electronics', 300000, 600000),
    ('Keyboard', 'Electronics', 50000, 150000),
    ('Wireless Mouse', 'Electronics', 20000, 80000),
    ('Headset', 'Electronics', 50000, 120000),
    ('Webcam', 'Electronics', 60000, 150000),
    ('USB Memory', 'Electronics', 15000, 40000),
    ('Mouse Pad', 'Electronics', 10000, 30000),
    ('Tablet', 'Electronics', 500000, 1200000),
    ('Desk', 'Furniture', 150000, 400000),
    ('Chair', 'Furniture', 100000, 300000),
    ('Bookshelf', 'Furniture', 200000, 500000),
    ('Lamp', 'Furniture', 30000, 100000),
]

# 지역 리스트
REGIONS = ['Seoul', 'Busan', 'Daegu', 'Incheon', 'Gwangju', 'Daejeon', 'Ulsan']

# 고객 등급 리스트 (등급, 가중치)
CUSTOMER_GRADES = [
    ('VIP', 0.2),      # 20%
    ('Premium', 0.3),   # 30%
    ('Regular', 0.5),   # 50%
]

def random_date(start, end):
    """시작일과 종료일 사이의 랜덤 날짜 생성"""
    delta = end - start
    random_days = random.randint(0, delta.days)
    return start + timedelta(days=random_days)

def weighted_choice(choices):
    """가중치 기반 랜덤 선택"""
    items, weights = zip(*choices)
    return random.choices(items, weights=weights)[0]

def generate_sales_data(num_records):
    """판매 데이터 생성"""
    records = []
    
    for _ in range(num_records):
        # 랜덤 날짜
        date = random_date(START_DATE, END_DATE)
        
        # 랜덤 제품 선택
        product_name, category, min_price, max_price = random.choice(PRODUCTS)
        
        # 수량 (1-15개)
        quantity = random.randint(1, 15)
        
        # 단가 (제품별 가격 범위 내에서)
        unit_price = random.randint(min_price, max_price)
        # 천 원 단위로 반올림
        unit_price = round(unit_price / 1000) * 1000
        
        # 총액
        total_amount = quantity * unit_price
        
        # 랜덤 지역
        region = random.choice(REGIONS)
        
        # 가중치 기반 고객 등급
        customer_grade = weighted_choice(CUSTOMER_GRADES)
        
        # 레코드 생성
        record = {
            'Date': date.strftime('%Y-%m-%d'),
            'Product': product_name,
            'Category': category,
            'Quantity': quantity,
            'Unit_Price': unit_price,
            'Total_Amount': total_amount,
            'Region': region,
            'Customer_Grade': customer_grade
        }
        
        records.append(record)
    
    # 날짜순 정렬
    records.sort(key=lambda x: x['Date'])
    
    return records

def save_to_csv(records, filename):
    """CSV 파일로 저장"""
    fieldnames = ['Date', 'Product', 'Category', 'Quantity', 'Unit_Price', 
                  'Total_Amount', 'Region', 'Customer_Grade']
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    
    print(f"✅ {len(records)}개의 레코드가 '{filename}' 파일로 저장되었습니다.")

if __name__ == '__main__':
    print(f"📊 랜덤 판매 데이터 생성 중...")
    print(f"   - 레코드 수: {NUM_RECORDS}")
    print(f"   - 기간: {START_DATE.strftime('%Y-%m-%d')} ~ {END_DATE.strftime('%Y-%m-%d')}")
    print(f"   - 출력 파일: {OUTPUT_FILE}")
    print()
    
    # 데이터 생성
    sales_data = generate_sales_data(NUM_RECORDS)
    
    # CSV 저장
    save_to_csv(sales_data, OUTPUT_FILE)
    
    # 샘플 데이터 출력
    print("\n📋 샘플 데이터 (처음 5개):")
    for i, record in enumerate(sales_data[:5], 1):
        print(f"{i}. {record['Date']} | {record['Product']} | {record['Quantity']}개 | {record['Total_Amount']:,}원 | {record['Region']}")
