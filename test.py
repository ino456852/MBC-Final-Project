import pandas as pd
import matplotlib.pyplot as plt
import platform

system_name = platform.system()

if system_name == 'Windows':
    plt.rcParams['font.family'] = 'Malgun Gothic'

plt.rc('axes', unicode_minus=False)

df = pd.read_csv("data/exchange_rates.csv")

df.head()
df.info()
df.describe()



df['Date'] = pd.to_datetime(df['Date'])

df.info()

print(f"중복 제거 전 데이터 갯수{len(df)}")
df.drop_duplicates(subset=['Date','Currency'],keep='last',inplace=True)
print(f"중복 제거 후 데이터 갯수{len(df)}")

# 'Date'를 인덱스로, 'currency'를 컬럼으로, 'Rate'을 값으로 하는 피벗 테이블 생성
pivot_df = df.pivot(index='Date', columns='Currency', values='Rate')

# 피벗 테이블의 앞부분 5줄 확인
pivot_df.head()

pivot_df.plot(figsize=(15, 7))
plt.title('통화별 환율 변동 추이')
plt.ylabel('Rate')
plt.grid(True)
plt.show(block=True)