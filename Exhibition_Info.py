import requests
from bs4 import BeautifulSoup

# def Exihibition_Infomation():
ExihibitionList = []

# 中正紀念堂展館
for Page in range(1, 3):
    Url = f'https://www.cksmh.gov.tw/activitysoonlist_369_{Page}.html'
    Response = requests.get(Url)
    Soup = BeautifulSoup(Response.content, 'html.parser')

    # 從 HTML 抓取內容
    Titles = Soup.find_all('div', class_='h3')  # 展名
    Dates = Soup.find_all('span', class_='date')  # 展期
    Location = Soup.find_all('span', class_='location')  # 地點

    # 處理資料並存入 dictionary
    for i in range(len(Titles)):
        Title = Titles[i].text
        Date = Dates[i].text
        DateList = Date.replace(' ~ ', '').replace(' ', '').replace('\n', ',').split(',')
        StartDate = DateList[2]
        EndDate = DateList[3]
        DateTime = DateList[4]
        LocationList = Location[i].text.strip('地點：')
        Link = Soup.find('a', title=Title+'「另開新視窗」').get('href')

        Dict = {
            'Title': Title,  # 展名
            'StartDate': StartDate,  # 起始日
            'EndDate': EndDate,  # 結束日
            'Time': DateTime,  # 時間
            'Location': LocationList,  # 地點
            'Link': Link
        }
        ExihibitionList.append(Dict)

print(ExihibitionList)