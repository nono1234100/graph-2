import re
from collections import Counter, defaultdict
from itertools import combinations

import pandas as pd
import plotly.express as px
import streamlit as st

# 페이지 설정
st.set_page_config(page_title="급식 규칙 찾기", layout="wide")
st.title("🍱 급식 규칙 찾기 (연관 규칙 분석)")


# 데이터 로드 및 전처리 함수
@st.cache_data
def load_and_preprocess_data():
    url = "https://raw.githubusercontent.com/it-teacher-go/data-share-/main/songtan_meals_184.csv"
    df = pd.read_csv(url, encoding="utf-8")

    transactions = []
    all_items = set()

    for raw_menu in df["메뉴"].dropna():
        # 세로줄(|)로 분리
        items = raw_menu.split("|")
        cleaned_items = set()
        for item in items:
            # 괄호 및 괄호 안 내용 제거 및 공백 정돈
            cleaned = re.sub(r"\(.*?\)", "", item).strip()
            if cleaned:
                cleaned_items.add(cleaned)
                all_items.add(cleaned)

        if cleaned_items:
            transactions.append(cleaned_items)

    total_days = len(transactions)
    total_unique_items = len(all_items)

    return transactions, total_days, total_unique_items, sorted(list(all_items))


# 연관 규칙 계산 함수
@st.cache_data
def calculate_rules(transactions, total_days):
    pair_counts = defaultdict(int)
    item_counts = Counter()

    for itemset in transactions:
        for item in itemset:
            item_counts[item] += 1
        # 하루 식단 내 메뉴 2개 조합
        for pair in combinations(sorted(list(itemset)), 2):
            pair_counts[pair] += 1

    rules = []
    # (A -> B) 및 (B -> A) 규칙 생성
    for (item_a, item_b), co_occurrence in pair_counts.items():
        count_a = item_counts[item_a]
        count_b = item_counts[item_b]

        # A -> B
        supp_ab = co_occurrence / total_days
        conf_ab = co_occurrence / count_a
        lift_ab = conf_ab / (count_b / total_days)

        rules.append(
            {
                "조건": item_a,
                "결과": item_b,
                "동시": co_occurrence,
                "지지도": round(supp_ab, 4),
                "신뢰도": round(conf_ab, 4),
                "향상도": round(lift_ab, 4),
            }
        )

        # B -> A
        conf_ba = co_occurrence / count_b
        lift_ba = conf_ba / (count_a / total_days)

        rules.append(
            {
                "조건": item_b,
                "결과": item_a,
                "동시": co_occurrence,
                "지지도": round(supp_ab, 4),
                "신뢰도": round(conf_ba, 4),
                "향상도": round(lift_ba, 4),
            }
        )

    rules_df = pd.DataFrame(rules)
    unique_pair_count = len(pair_counts)

    return rules_df, unique_pair_count


# 데이터 로드
transactions, total_days, total_unique_items, all_items_list = (
    load_and_preprocess_data()
)
rules_df, unique_pair_count = calculate_rules(transactions, total_days)

# 요약 정보 출력
st.markdown(
    f"**급식 일수:** {total_days}일 | **메뉴 종류 수:** {total_unique_items}개 | **함께 나온 적이 있는 메뉴 쌍의 수:** {unique_pair_count}쌍"
)
st.divider()

# 사이드바 컨트롤
st.sidebar.header("필터 및 정렬 설정")

# 정렬 기준 선택
sort_option = st.sidebar.selectbox(
    "정렬 기준 선택", options=["향상도", "신뢰도", "동시"], index=0
)

# 메뉴 필터링 선택
selected_menu = st.sidebar.selectbox(
    "특정 메뉴 선택 (전체 보기: 선택 안 함)",
    options=["전체 보기"] + all_items_list,
    index=0,
)

# 데이터 필터링 및 정렬
filtered_df = rules_df.copy()

if selected_menu != "전체 보기":
    filtered_df = filtered_df[
        (filtered_df["조건"] == selected_menu)
        | (filtered_df["결과"] == selected_menu)
    ]

# 선택한 정렬 기준에 따라 내림차순 정렬
filtered_df = filtered_df.sort_values(by=sort_option, ascending=False).reset_index(
    drop=True
)

# 향상도 상위 10개 가로 막대그래프 (Plotly)
st.subheader("📊 향상도 상위 10개 규칙")

if not filtered_df.empty:
    top10_df = filtered_df.sort_values(by="향상도", ascending=False).head(10)
    # 그래프 시각화를 위한 규칙 이름 생성 (예: 김치볶음밥 -> 계란국)
    top10_df["규칙"] = top10_df["조건"] + " ➔ " + top10_df["결과"]

    # y축에 정렬 순서를 유지하기 위해 data frame 순서 조절
    top10_df = top10_df.sort_values(by="향상도", ascending=True)

    fig = px.bar(
        top10_df,
        x="향상도",
        y="규칙",
        orientation="h",
        text="향상도",
        title="향상도(Lift) Top 10 규칙",
        labels={"향상도": "향상도", "규칙": "연관 규칙 (조건 ➔ 결과)"},
    )
    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("선택한 메뉴에 대한 연관 규칙이 없습니다.")

st.divider()

# 표 출력
st.subheader("📋 연관 규칙 결과 표")
st.dataframe(filtered_df, use_container_width=True)
