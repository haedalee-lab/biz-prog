# 타이틀 텍스트 출력, streamlit을 import 부터 하자.
import streamlit as st
st.title("첫번째 웹 어플 만들기 🫶🏻")
"## 이건 부제목🍉"
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
    st.write("hello, streamlit👋🏻", name)

'''
:green["초록색 글씨를 써보겠습니다 💚"]
'''

'# 🎥: 이미지, 오디오, 동영상'

'#### :orange[이미지: st.image()]'
st.image("./BIZ_streamlit/사이다 사진.jpg", caption="사이다 사진", width=500)

'#### :orange[오디오: st.audio()]'
st.audio("./BIZ_streamlit/놀러오세요 동물의숲.mp3", format="audio/mpeg", loop=True)

'#### :orange[동영상: st.video()]'
# 'rb' : 바이너리 모드로 파일 열기
video_file = open("./BIZ_streamlit/영상.mp4", "rb")
video_bytes = video_file.read()

st.video(video_bytes)

st.divider()  # 👈 구분선