import streamlit as st
import os
import pandas as pd
import plotly.express as px
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric

# [설정] 서비스 계정 및 속성 ID
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'service-account.json'
MY_PROPERTY_ID = "523128479" 

def load_nav_data():
    client = BetaAnalyticsDataClient()
    # 유입 경로와 현재 머무는 페이지를 가져옵니다.
    request = RunReportRequest(
        property=f"properties/{MY_PROPERTY_ID}",
        date_ranges=[DateRange(start_date="30daysAgo", end_date="today")],
        dimensions=[
            Dimension(name="sessionSourceMedium"), # 어떤 채널로 왔나 (검색, 직접 등)
            Dimension(name="pagePath"),            # 어떤 페이지를 보고 있나
            Dimension(name="landingPagePlusQueryString") # 처음 도착한 페이지
        ],
        metrics=[Metric(name="sessions")],
    )
    response = client.run_report(request)
    
    rows = []
    for row in response.rows:
        rows.append({
            "Source": row.dimension_values[0].value,
            "Target_Page": row.dimension_values[1].value,
            "Landing_Page": row.dimension_values[2].value,
            "Sessions": int(row.metric_values[0].value)
        })
    return pd.DataFrame(rows)

st.title("🎨 포트폴리오 방문자 동선 리포트")

df = load_nav_data()

if not df.empty:
    # 1. 유입 경로 요약
    st.subheader("🌐 방문자 유입 경로")
    source_pie = px.pie(df, names='Source', values='Sessions', hole=0.4,
                        color_discrete_sequence=px.colors.sequential.RdPu)
    st.plotly_chart(source_pie, use_container_width=True)

    # 2. 가장 인기 있는 도착 페이지 (랜딩 페이지)
    st.subheader("🏠 처음 도착한 페이지 (Landing Page)")
    landing_bar = px.bar(df.groupby("Landing_Page")["Sessions"].sum().reset_index(), 
                         x='Sessions', y='Landing_Page', orientation='h',
                         color='Sessions', color_continuous_scale='Purples')
    st.plotly_chart(landing_bar, use_container_width=True)

    # 3. 상세 이동 경로 테이블
    st.subheader("📑 상세 페이지 뷰 데이터")
    st.table(df[['Source', 'Target_Page', 'Sessions']].head(10))
else:
    st.warning("아직 수집된 데이터가 없습니다. 사이트에 직접 접속해서 데이터를 만들어보세요!")