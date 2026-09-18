# main.py
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계", layout="wide"
)

st.title("영화 데이터 그래프 도감 2 - 분포와 관계")


# 데이터 불러오기 및 전처리
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    df = pd.read_csv(url)

    # 장르 전처리: .str.split().str[0]을 사용하여 안전하게 첫 번째 장르만 추출
    df["genre"] = df["genre"].astype(str).str.split("|").str[0]
    return df


df = load_data()

# ---------------------------------------------------------
# 1. 장르별 영화 편수 (도넛 그래프)
# ---------------------------------------------------------
st.header("1. 장르별 영화 편수 분포")

# 장르별 편수 집계
genre_counts = df["genre"].value_counts().reset_index()
genre_counts.columns = ["genre", "count"]

# Plotly 도넛 그래프 생성
fig1 = px.pie(
    genre_counts,
    values="count",
    names="genre",
    hole=0.4,
    title="장르별 영화 비율 및 편수",
)

fig1.update_traces(
    textinfo="percent+label",
    hovertemplate="<b>장르: %{label}</b><br>편수: %{value}편<br>비율: %{percent}",
)

st.plotly_chart(fig1, use_container_width=True)

st.divider()
st.markdown(
    "**💡 이 그래프로 알 수 있는 것:** 개봉 영화 중 특정 주요 장르가 차지하는 비율과 전체적인 장르 다양성을 한눈에 파악할 수 있습니다."
)

st.write("")

# ---------------------------------------------------------
# 2. 장르 및 영화별 총 관객 수 (트리맵)
# ---------------------------------------------------------
st.header("2. 장르별 영화 총 관객 수 분포 (트리맵)")

fig2 = px.treemap(
    df,
    path=[px.Constant("전체 장르"), "genre", "movieNm"],
    values="total_audi",
    title="장르 및 영화별 총 관객 수 (칸 크기: 총 관객 수)",
    color="genre",
)

fig2.update_traces(
    hovertemplate="<b>%{label}</b><br>총 관객 수: %{value:,.0f}명"
)

st.plotly_chart(fig2, use_container_width=True)

st.divider()
st.markdown(
    "**💡 이 그래프로 알 수 있는 것:** 어떤 장르가 전체 흥행(총 관객 수)을 주도하는지, 그리고 해당 장르 내에서 어떤 영화가 독점적이거나 높은 기여를 했는지 직관적으로 비교할 수 있습니다."
)

st.write("")

# ---------------------------------------------------------
# 3. 총 관객 수 분포 (히스토그램)
# ---------------------------------------------------------
st.header("3. 총 관객 수 분포 (히스토그램)")

fig3 = px.histogram(
    df,
    x="total_audi",
    nbins=30,
    title="총 관객 수 분포",
    labels={"total_audi": "총 관객 수", "count": "영화 수"},
    color_discrete_sequence=["#636EFA"],
)

fig3.update_layout(
    xaxis_title="총 관객 수(명)", yaxis_title="영화 수(편)", bargap=0.1
)

st.plotly_chart(fig3, use_container_width=True)

# 주요 통계 동적 계산
top_movie = df.loc[df["total_audi"].idxmax()]
top_movie_name = top_movie["movieNm"]
top_movie_audi = top_movie["total_audi"]

under_1m_ratio = (df["total_audi"] < 1000000).mean() * 100

st.divider()
st.markdown(
    f"**💡 이 그래프로 알 수 있는 것:** 전체 영화의 **{under_1m_ratio:.1f}%**가 관객 수 **100만 명 미만 구간**에 집중되어 있어 하위 구간 밀집도가 매우 높습니다. 가장 관객 수가 많은 영화는 **'{top_movie_name}'**(총 {top_movie_audi:,.0f}명)입니다."
)

st.write("")

# ---------------------------------------------------------
# 4. 개봉일 스크린 수와 총 관객 수의 관계 (산점도)
# ---------------------------------------------------------
st.header("4. 개봉일 스크린 수 vs 총 관객 수 (산점도)")

fig4 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
    hover_data={"first_scrn": ":,f", "total_audi": ":,f", "genre": True},
    title="개봉일 스크린 수와 총 관객 수의 산점도 (장르별 구분)",
    labels={"first_scrn": "개봉일 스크린 수", "total_audi": "총 관객 수"},
)

fig4.update_traces(
    marker=dict(size=9, opacity=0.8),
    hovertemplate="<b>%{hovertext}</b><br>장르: %{customdata[2]}<br>개봉일 스크린 수: %{x:,.0f}개<br>총 관객 수: %{y:,.0f}명",
)

fig4.update_layout(
    xaxis_title="개봉일 스크린 수(개)",
    yaxis_title="총 관객 수(명)",
    legend_title="장르",
)

st.plotly_chart(fig4, use_container_width=True)

st.divider()
st.markdown(
    "**💡 이 그래프로 알 수 있는 것:** 개봉일 스크린 수가 많을수록 대체로 총 관객 수도 증가하는 양의 상관관계를 보이지만, 초기 스크린 수가 적음에도 입소문 등을 통해 높은 흥행실적을 기록한 영화(아웃라이어)도 확인할 수 있습니다."
)

st.write("")

# ---------------------------------------------------------
# 5. 주요 장르별 총 관객 수 분포 (상자 그림)
# ---------------------------------------------------------
st.header("5. 주요 장르별 총 관객 수 분포 (박스플롯)")

# 영화 수 10편 이상인 장르만 추출
genre_counts_series = df["genre"].value_counts()
top_genres = genre_counts_series[genre_counts_series >= 10].index
filtered_df = df[df["genre"].isin(top_genres)]

fig5 = px.box(
    filtered_df,
    x="genre",
    y="total_audi",
    color="genre",
    points="outliers",
    hover_name="movieNm",
    title="영화 수 10편 이상 장르의 총 관객 수 분포",
    labels={"genre": "장르", "total_audi": "총 관객 수"},
)

fig5.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>장르: %{x}<br>총 관객 수: %{y:,.0f}명"
)

fig5.update_layout(
    xaxis_title="장르", yaxis_title="총 관객 수(명)", showlegend=False
)

st.plotly_chart(fig5, use_container_width=True)

st.divider()
st.markdown(
    "**💡 이 그래프로 알 수 있는 것:** 주요 장르별 흥행의 중간값과 편차를 비교할 수 있으며, 특정 장르에서 상자 밖으로 크게 벗어난 흥행 대작(이상치)의 유무와 분포 특성을 파악할 수 있습니다."
)

st.write("")

# ---------------------------------------------------------
# 6. 개봉일 스크린 수 vs 총 관객 수 (버블 차트)
# ---------------------------------------------------------
st.header("6. 개봉일 스크린 수 vs 총 관객 수 (버블 차트)")

fig6 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    size="first_week_audi",
    color="genre",
    hover_name="movieNm",
    hover_data={
        "first_scrn": ":,f",
        "total_audi": ":,f",
        "first_week_audi": ":,f",
        "genre": True,
    },
    title="개봉일 스크린 수와 총 관객 수의 관계 (버블 크기: 개봉 첫 주 관객 수)",
    labels={
        "first_scrn": "개봉일 스크린 수",
        "total_audi": "총 관객 수",
        "first_week_audi": "개봉 첫 주 관객 수",
    },
    size_max=40,
)

fig6.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>장르: %{customdata[3]}<br>개봉일 스크린 수: %{x:,.0f}개<br>총 관객 수: %{y:,.0f}명<br>개봉 첫 주 관객 수: %{customdata[2]:,.0f}명"
)

fig6.update_layout(
    xaxis_title="개봉일 스크린 수(개)",
    yaxis_title="총 관객 수(명)",
    legend_title="장르",
)

st.plotly_chart(fig6, use_container_width=True)

st.divider()
st.markdown(
    "**💡 이 그래프로 알 수 있는 것:** 버블의 크기(개봉 첫 주 관객 수)를 함께 고려하면, 초기 선전(첫 주 관객)이 최종 총 관객 수 및 스크린 수 확보와 얼마나 밀접하게 연관되어 있는지 복합적으로 분석할 수 있습니다."
)

st.write("")

# ---------------------------------------------------------
# 7. 국가 및 장르별 영화 편수 (선버스트 차트)
# ---------------------------------------------------------
st.header("7. 국가 및 장르별 영화 편수 (선버스트 차트)")

fig7 = px.sunburst(
    df,
    path=["nation", "genre"],
    title="제작 국가 및 장르별 영화 편수 비율 (칸 크기: 영화 편수)",
    color="nation",
)

fig7.update_traces(
    hovertemplate="<b>%{label}</b><br>영화 편수: %{value}편<br>비율: %{percentParent:.1%}"
)

st.plotly_chart(fig7, use_container_width=True)

st.divider()
st.markdown(
    "**💡 이 그래프로 알 수 있는 것:** 주요 제작 국가별로 개봉 영화의 주력 장르가 어떻게 구성되어 있는지 계층 구조를 통해 한눈에 비교할 수 있습니다."
)
