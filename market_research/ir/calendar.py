import pandas as pd
import plotly.graph_objects as go
from string import punctuation
import requests
import datetime
import pandas as pd
import re 



class Calendar:
    def __init__(self, API_KEY:str, CALENDAR_ID :str):
        self.API_KEY = API_KEY
        self.CALENDAR_ID=CALENDAR_ID
        events = self._get_all_events(API_KEY, CALENDAR_ID)
        self._data = self._create_dataframe(events)
        pass
    
    @property
    def data(self):  
        return self._data
        
    def _get_all_events(self, API_KEY, CALENDAR_ID):
        start_time = datetime.datetime(2000, 1, 1).isoformat() + 'Z'  
        url = f'https://www.googleapis.com/calendar/v3/calendars/{CALENDAR_ID}/events'
        params = {
            'key': API_KEY,
            'timeMin': start_time,
            'maxResults': 250,
            'singleEvents': True,
            'orderBy': 'startTime'
        }
        events = []  
        while True:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])
                events.extend(items)  
                
                if 'nextPageToken' not in data:
                    break
                
                params['pageToken'] = data['nextPageToken']
            else:
                print(f'Error fetching events: {response.status_code} - {response.text}')
                break
        return events 


    def _create_dataframe(self, events):
        def extract_url(description):
            urls = re.findall(r'https?://[^\s<>"]+', description)  
            return ', '.join(urls) if urls else 'No URL'  
        event_list = []
        for event in events:
            event_data = {
                'summary': event.get('summary', 'No Title'),  # 이벤트 제목
                'start': event['start'].get('dateTime', event['start'].get('date')),  # 시작 시간
                'end': event['end'].get('dateTime', event['end'].get('date')),  # 종료 시간
                'description_url': extract_url(event.get('description', 'No Description')),  # URL 추출
                'location': event.get('location', 'No Location'),  # 위치
                'attendees': ', '.join([attendee['email'] for attendee in event.get('attendees', [])])  # 참석자
            }
            event_list.append(event_data)
        df = pd.DataFrame(event_list)
        return df


    def create_events_calendar(self, filter_year = 2024, month_interval=10, return_fig=False):

        def preprocess_data(df, month_interval = 10):        

            for i in range(len(df)):
                summary_text = df["summary"][i].split(":")[0]
                cleaned_summary = summary_text.replace("sony","").replace("'s'","").replace("inch'","").replace("-'"," ")[:10] + "..."
                df.at[i, "keywords_summary"] = cleaned_summary
        
            # 요일 및 색상 매핑
            day_mapping = {
                'Monday': 0,
                'Tuesday': 1,
                'Wednesday': 2,
                'Thursday': 3,
                'Friday': 4,
                'Saturday': 5,
                'Sunday': 6,
            }
    
            df['start'] = pd.to_datetime(df['start'])
            df['year'] = df['start'].dt.year
            df['month'] = df['start'].dt.to_period('M').dt.start_time
            df['day_of_week'] = df['start'].dt.day_name()
            df['day_index'] = df['day_of_week'].map(day_mapping)
            df['month_number'] = df['month'].dt.strftime('%B')
        
            month_interval = month_interval
            df['month_numeric'] = df['month'].dt.month * month_interval
            df['week_number'] = df['start'].dt.isocalendar().week - df['start'].dt.to_period('M').dt.start_time.dt.isocalendar().week + 1
            df['week_label'] = df['week_number'].astype(str) + 'w'
        
            return df
        
        month_colors = {
            1: 'red',
            2: 'green',
            3: 'blue',
            4: 'orange',
            5: 'purple',
            6: 'pink',
            7: 'brown',
            8: 'cyan',
            9: 'magenta',
            10: 'gold',
            11: 'lightblue',
            12: 'lime'
        }
        
        df = self._data
        df = preprocess_data(df, month_interval=month_interval)  
        df[df['year'] == filter_year]
        
        marker_size = 11
        
        fig = go.Figure()
        point_counter = {}

        for i in range(len(df)):
            key = (df['month_numeric'][i], df['week_number'][i])

            if key not in point_counter:
                point_counter[key] = 0
            else:
                point_counter[key] += month_interval/7

            y_offset = point_counter[key]
            month = df['month_numeric'][i] // month_interval
            marker_color = month_colors.get(month, 'black')

            # 이벤트에 대한 산점도 추가
            fig.add_trace(go.Scatter(
                x=[df['week_number'][i]],
                y=[df['month_numeric'][i] + y_offset],
                mode='markers+text',
                textposition='middle right',
                text=df["keywords_summary"][i],
                # textfont=dict(size=12),
                marker=dict(size=marker_size, color=marker_color),
                hovertemplate=f'{df["summary"][i]}<extra></extra>',
                showlegend=False,
            ))

            # 설명 링크 추가
            fig.add_trace(go.Scatter(
                x=[df['week_number'][i]],
                y=[df['month_numeric'][i] + y_offset],
                mode='text',
                text=f'<a href="{df["description_url"][i]}" target="_blank" style="color:blue;"> </a>',
                textfont=dict(size=15),
                textposition='middle center',
                hovertemplate=f'{df["summary"][i]}<extra></extra>',
                showlegend=False,
            ))


        fig.update_xaxes(
            tickvals=df['week_number'].unique(),
            ticktext=[f'{int(w)}w' for w in sorted(df['week_number'].unique(), reverse=True)],
            visible=False
        )

        fig.update_yaxes(
            tickmode='array',
            tickvals=[month_interval * i for i in range(1, 13)],
            ticktext=[
                'January', 'February', 'March', 'April', 'May',
                'June', 'July', 'August', 'September',
                'October', 'November', 'December'
            ],
            autorange='reversed',
            gridcolor='lightgray',
        )

        # 레이아웃 업데이트
        fig.update_layout(
            title='Events Calendar',
            width=600,
            height=800,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='black'),
            margin=dict(l=0, r=0, t=0, b=0)  # 여백 설정
        )

        
        if return_fig:
            return fig
        else:
            fig.show()

