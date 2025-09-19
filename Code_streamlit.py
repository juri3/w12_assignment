import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup

# 데이터 로드

if __name__ == "__main__":
    st.title('Title')

    service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    # url 전달
    url_jobkor = 'https://www.jobkorea.co.kr/Search/?stext='+'데이터분석'
    url_saram = 'https://www.saramin.co.kr/zf_user/search/recruit?searchword='+'데이터분석'

    #############################잡코리아
    driver.get(url_jobkor)

    # 기다려달라는 값을 전달 : 최대 10초 기다리기
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-sentry-component='JobList']")))


    # 드라이버 접근 > 페이지 소스 가져오기
    html_jobkor = driver.page_source
    soup_jobkor = BeautifulSoup(html_jobkor, 'html.parser')
    # print(soup_jobkor)


    #############################사람인
    driver.get(url_saram)

    # 기다려달라는 값을 전달 : 최대 10초 기다리기
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.content_wrap")))


    # 드라이버 접근 > 페이지 소스 가져오기
    html_saram = driver.page_source
    soup_saram = BeautifulSoup(html_saram, 'html.parser')

    # 드라이버 종료(필수)
    driver.quit() 

    site_list = []
    companys_list = []
    recruits_list = []
    detail_list = []
    url_list = []

    items= soup_jobkor.select_one("div[data-sentry-component='JobList']").select("div[data-sentry-component='CardCommon']")
    for item in items:
        item_divide = item.select_one("div[data-sentry-element='Block']").select("div[data-sentry-source-file='index.tsx']")
        
        site_list.append("Job_Korea")

        company = item_divide[3].select_one('a[data-sentry-element="BaseLink"]:not([data-sentry-component="Title"]) span')
        companys_list.append(company.get_text(strip=True) if company else None) 
        # print(companys_list)
        
        recruit = item_divide[4].select_one('a[data-sentry-element="BaseLink"][data-sentry-component="Title"]')
        recruits_list.append(recruit.get_text(strip=True) if recruit else None) 
        # print(recruits_list)

        url_list.append(recruit["href"] if recruit else None)
        # print(url_list)

        detail = item_divide[6].select_one("div.Flex_display_flex__i0l0hl2.Flex_direction_column__i0l0hl4 div[class*='Flex_gap_space16'][class*='Flex_direction_row']")
        detail_items = [sp.get_text(strip=True) for sp in detail]
        detail_list.append(detail_items)
        # print(detail_list)

    detail_item=[]

    items= soup_saram.find('div', class_='content_wrap').find_all('div', class_='item_recruit')
    for item in items:
        # print(item)
        site = "Saramin"
        company = item.find('strong', class_='corp_name').text
        recruit = item.find('h2', class_='job_tit').text
        detail = item.find('div', class_='job_condition').find_all('span')
        for span in detail:
            detail_item.append(span.text)
        url = item.find('h2', class_='job_tit').find("a")["href"]
        
        site_list.append(site)
        companys_list.append(company.strip().replace('\n',''))
        recruits_list.append(recruit.replace('\n',''))
        detail_list.append(detail_item)
        url_list.append(url)


    data = {
        "Site": site_list,
        "Col_Company": companys_list,
        "Col_Recruit": recruits_list,
        "Col_detail": detail_list,
        "Col_url": url_list,
    }

    df = pd.DataFrame(data)

    df_group = df.groupby('Site').agg(
        Count=('Site', 'count')
    ).reset_index()

    total = df_group['Count'].sum()
    df_group['Ratio'] = round(df_group['Count']/total * 100, 2)



    with st.form('form1'):
        btn1 = st.form_submit_button('Recruit Searching')

        if btn1:
            st.dataframe(df, width=1500, use_container_width=True)
            st.dataframe(df_group, width=300)

            fig = px.pie(values=df_group['Ratio'], names=df_group['Site'], title="Recruitment Ratio")
            fig.update_layout(showlegend=True)
            
            st.plotly_chart(fig, theme="streamlit", use_container_width=True)
            

            



        

            



