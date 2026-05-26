# 타이틀 텍스트 출력, streamlit을 import 부터 하자.
import streamlit as st
st.title("첫번째 웹 어플 만들기 🫶🏻")
"## 이건 부제목🍉"
"## 혀니쭈 안뇽 🐥"
#uv run streamlit run biz_st.py를 터미널에 입력하여 실행.
#줄바꿈을 위해서는 스페이스 2번 or 엔터 두번.

"""
[네이버](https://www.naver.com)  
[홍익대학교](https://www.hongik.ac.kr)
"""

st.caption("이건 캡션입니다. 작고, 흐린 글씨로 표현: st.caption()") 

#코드블록 내 색상 불러오기를 원하면 언어 이름을 백틱뒤에 붙여봐라.
'''
```python 
import streamlit as st
print("코드블록")
'''

with st.echo():
    #이 블록의 코드와 결과를 출력. 인덴트 블록을 실행하라.
    name = "haejin"
    st.write("hello, streamlit 👋🏻", f' -from {name}-')

'''
:green[초록색 글씨를 써보겠습니다 💚]
'''

'# 🎥: 이미지, 오디오, 동영상'

'#### :orange[이미지: st.image()]'
st.image("./BIZ_streamlit/사이다 사진.jpg", caption="사이다 사진", width=500)

'#### :orange[오디오: st.audio()]'
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
audio_path = os.path.join(current_dir, "놀러오세요 동물의숲.mp3")
st.audio(audio_path, format="audio/mpeg", loop=True)

'#### :orange[동영상: st.video()]'
# 'rb' : 바이너리 모드로 파일 열기
video_file = open("./BIZ_streamlit/영상.mp4", "rb")
video_bytes = video_file.read()
st.video(video_bytes)
st.divider()  # 👈 구분선

'#### :orange[pandas 데이터프레임]'
import pandas as pd
df = pd.DataFrame(
    {
        "id": [1, 2, 3],
        "name": ["앨리스", "밥", "찰리"],
        "age": [24, 34, 45]
    }
)
df #데이터프레임을 표로 출력!
#주의. 모든 셀의 데이터 타입은 같아야한다. 행과 열의 인덱스는 존재. 이름은 미존. 
#행은 인덱스를 갖고, 열은 컬럼명을 갖는다. 열기준 datatype.
#data를 넣는 여러가지 방법 중 딕셔너리 방식이 가장 쉽다. key는 컬럼명, value는 리스트로 데이터 넣기.
#데이터프레임은 literal이다. 즉, 스트림릿 매직에 의해 자동으로 출력된다. print(df)로 출력할 필요 없다.

"""
|이름|학번|학과|
|---|---|---|
|김해진|C331284|경영학부|
|사이다|C000000|기염딩이|
"""

st.metric("temperature","70°F","-1.2°F")
