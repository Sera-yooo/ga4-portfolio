import streamlit as st
import os
import pandas as pd
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest

# [설정] 키 파일 경로 (이름 일치해야 함!)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'service-account.json'

# [설정] 내 GA4 속성 ID (숫자로 된 것!)
MY_PROPERTY_ID = "523128479" 

st.title("🚀 GA4 데이터 대시보드")

try:
    client = BetaAnalyticsDataClient()
    request = RunReportRequest(
        property=f"properties/{MY_PROPERTY_ID}",
        date_ranges=[{"start_date": "30daysAgo", "end_date": "today"}],
        dimensions=[{"name": "date"}],
        metrics=[{"name": "activeUsers"}]
    )
    response = client.run_report(request)

    data = []
    for row in response.rows:
        data.append({"Date": row.dimension_values[0].value, "Users": int(row.metric_values[0].value)})
    
    if data:
        df = pd.DataFrame(data)
        st.write("### 📈 일별 방문자 수")
        st.line_chart(df.set_index("Date"))
        st.dataframe(df)
    else:
        st.warning("데이터가 없어요. 블로그에 접속 좀 해주세요!")

except Exception as e:
    st.error(f"에러 발생: {e}")