# 필요한 라이브러리들을 모두 불러옵니다.
import pandas as pd
import matplotlib.pyplot as plt
import platform
from matplotlib import font_manager
import os
import datetime as dt


def set_korean_font():
    """
    운영체제(플랫폼)에 맞는 한글 폰트를 자동으로 설정합니다.
    Mac, Windows, Linux 환경에 모두 대응합니다.
    """
    os_name = platform.system()
    if os_name == 'Windows':
        font_name = 'Malgun Gothic'
    elif os_name == 'Darwin':  # macOS
        font_name = 'AppleGothic'
    else:  # Linuxㅁ
        font_name = 'NanumGothic'

    try:
        # 시스템에 폰트가 있는지 확인하고, 없으면 기본 폰트로 설정
        font_manager.findfont(font_name, rebuild_if_missing=True)
        plt.rc('font', family=font_name)
    except:
        print(f"'{font_name}' 폰트를 찾을 수 없어 기본 폰트로 표시됩니다.")

    # 마이너스 부호가 깨지는 현상을 방지합니다.
    plt.rc('axes', unicode_minus=False)
    print(f"한글 폰트가 '{plt.rcParams['font.family'][0]}'으로 설정되었습니다. (OS: {os_name})")


def analyze_and_visualize_rates(file_path, output_folder="output"):
    """
    RPA가 수집한 환율 CSV 파일을 읽어 분석하고, 월별 평균 추이 그래프를 생성합니다.

    Args:
        file_path (str): 원본 데이터 CSV 파일 경로
        output_folder (str): 결과물이 저장될 폴더 이름
    """
    # --- 1. 데이터 불러오기 및 전처리 ---
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"오류: 파일을 찾을 수 없습니다. 경로를 확인해주세요: {file_path}")
        return

    # 컬럼 이름 통일
    df.columns = ['Date', 'Currency', 'Rate']

    # 비어있거나 불완전한 행 제거
    df.dropna(subset=['Date', 'Currency'], inplace=True)

    # 'Date' 열을 날짜 형식으로 변환하고, 시간 정보는 제거 (중복 방지)
    df['Date'] = pd.to_datetime(df['Date']).dt.normalize()

    # 중복된 데이터가 있다면 가장 마지막 것만 남기고 제거
    df.drop_duplicates(subset=['Date', 'Currency'], keep='last', inplace=True)

    # --- 2. 데이터 가공 (피벗 테이블 & 월별 리샘플링) ---
    # 일별 데이터로 피벗 테이블 생성
    pivot_df = df.pivot(index='Date', columns='Currency', values='Rate')

    # 일별 데이터를 월별 평균 데이터로 리샘플링
    monthly_avg_df = pivot_df.resample('ME').mean()

    print("\n" + "=" * 50)
    print("          주요 통화별 월 평균 환율 (원)")
    print("=" * 50)
    print(monthly_avg_df.style.format("{:,.2f}"))
    print("=" * 50 + "\n")

    # --- 3. 월별 평균 데이터 시각화 ---
    fig, ax = plt.subplots(figsize=(18, 10))

    # 컬러맵 가져오기 (최신 matplotlib 방식)
    cmap = plt.get_cmap('tab10')

    # 각 통화별로 반복하면서 그래프 그리기
    for i, currency in enumerate(monthly_avg_df.columns):
        ax.plot(monthly_avg_df.index, monthly_avg_df.iloc[:, i], marker='o', linestyle='--', label=currency,
                color=cmap(i))

        # 각 데이터 포인트에 수치 주석 추가
        for date, rate in monthly_avg_df[[currency]].itertuples():
            if pd.notna(rate):
                ax.annotate(f"{rate:,.2f}",
                            (date, rate),
                            textcoords="offset points",
                            xytext=(0, 10),
                            ha='center',
                            fontsize=8,
                            color=cmap(i))

    # 그래프 꾸미기
    ax.set_title('주요 통화별 월 평균 환율 변동 추이', fontsize=18)
    ax.set_xlabel('월(Month)', fontsize=12)
    ax.set_ylabel('평균 매매기준율 (원)', fontsize=12)
    ax.legend(title='통화코드')
    ax.grid(True)
    plt.tight_layout()

    # --- 4. 결과물 저장 ---
    # 결과물 저장 폴더가 없으면 새로 생성
    csv_output_folder = "data"
    graph_output_folder = "graph"
    if not os.path.exists(csv_output_folder):
        os.makedirs(csv_output_folder)
    if not os.path.exists(graph_output_folder):
        os.makedirs(graph_output_folder)

    today_str = dt.datetime.now().strftime('%Y-%m-%d')

    # 월별 평균 데이터를 CSV 파일로 저장
    monthly_csv_path = os.path.join(csv_output_folder, f"환율_월별평균_{today_str}.csv")
    monthly_avg_df.to_csv(monthly_csv_path, encoding='utf-8-sig')
    print(f"월별 평균 데이터가 '{monthly_csv_path}' 파일로 저장되었습니다.")

    # 그래프를 이미지 파일로 저장
    graph_path = os.path.join(graph_output_folder, f"환율_월별그래프_{today_str}.png")
    plt.savefig(graph_path)
    print(f"그래프가 '{graph_path}' 파일로 저장되었습니다.")

    # 화면에 그래프 보여주기
    plt.show(block=True)


# --- 메인 코드 실행 부분 ---
if __name__ == '__main__':
    # 한글 폰트 설정 함수 실행
    set_korean_font()

    # RPA가 데이터를 저장하는 파일 경로
    rpa_output_file = "C:/RPA_Result/exchange_rates.csv"

    # 분석 및 시각화 함수 실행
    analyze_and_visualize_rates(rpa_output_file)
