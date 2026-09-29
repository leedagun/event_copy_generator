import os
import json
import streamlit as st
from PIL import Image
import google.generativeai as genai

st.set_page_config(page_title="이벤트 이미지 맞춤형 광고 문구 생성기", page_icon="🎨", layout="wide")

with st.sidebar:
    st.header("⚙️ 웹 프로그램 설정")
    api_key_input = st.text_input("Gemini API Key 입력", type="password", help="Google AI Studio에서 발급받은 API Key를 입력하세요.")
    model_choice = st.selectbox("사용할 AI 모델", ["gemini-1.5-flash", "gemini-1.5-pro"], index=0)
    st.markdown("---")
    st.markdown("### 💡 이용 가이드")
    st.markdown("1. 사이드바에 Gemini API Key를 입력합니다.\n2. 이벤트 포스터 이미지를 업로드합니다.\n3. 추가 요구사항이 있다면 적어주세요.\n4. 생성 버튼을 누르고 문구를 확인하세요!")

st.title("🎨 이벤트 이미지 플랫폼별 광고 문구 생성 웹 프로그램")
st.write("홍보용 이벤트 이미지를 업로드하면, Gemini AI가 이미지를 분석해 **블로그, 인스타그램, 카카오톡** 맞춤형 문구를 만들어 드립니다.")

col_left, col_right = st.columns([1, 1.5], gap="large")

with col_left:
    st.subheader("1️⃣ 이미지 및 옵션 입력")
    uploaded_file = st.file_uploader("이벤트 이미지 업로드 (PNG, JPG)", type=["png", "jpg", "jpeg"])
    
    image = None
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="업로드된 이벤트 이미지", use_container_width=True)
        
    extra_request = st.text_area("추가 요구사항 (선택사항)", placeholder="예: '선착순 50명 마감 강조해줘', '20대 대상 친근한 반말로 해줘'")
    generate_btn = st.button("🚀 블로그·인스타·카톡 문구 생성하기", type="primary", use_container_width=True)

with col_right:
    st.subheader("2️⃣ 플랫폼별 생성 결과")
    
    if generate_btn:
        if not api_key_input:
            st.error("⚠️ 사이드바에 Gemini API Key를 먼저 입력해주세요!")
        elif image is None:
            st.warning("⚠️ 분석할 이벤트 이미지를 업로드해주세요!")
        else:
            with st.spinner("🤖 Gemini가 이미지를 분석하고 플랫폼별 맞춤 카피를 작성 중입니다..."):
                try:
                    genai.configure(api_key=api_key_input)
                    model = genai.GenerativeModel(model_choice)
                    
                    prompt = """
                    당신은 10년 차 전문 마케터이자 각 SNS 플랫폼 알고리즘을 꿰뚫고 있는 카피라이터입니다.
                    사용자가 제공한 이벤트 이미지를 분석하여 네이버 블로그, 인스타그램, 카카오톡(채널/단톡방용)에 최적화된 마케팅 문구를 작성하세요.
                    
                    반드시 아래의 JSON 구조로만 응답해주세요. 다른 텍스트는 포함하지 마세요.
                    {
                      "blog": {
                        "title": "검색 유입용 네이버 블로그 포스팅 제목",
                        "content": "블로그용 본문 (도입부, 이벤트 상세 내용, 참여 방법, 유의사항 구조 포함)"
                      },
                      "instagram": {
                        "content": "인스타그램용 본문 (이모지 풍성하게, 가독성 좋은 줄바꿈, 하단 해시태그 10개 포함)"
                      },
                      "kakao": {
                        "content": "카카오톡(채널/단톡방)용 본문 (한눈에 들어오는 가독성, 핵심 혜택 강조, 참여 링크 유도형 문구)"
                      }
                    }
                    """
                    
                    response = model.generate_content([image, prompt])
                    
                    clean_text = response.text.strip()
                    if clean_text.startswith("```json"):
                        clean_text = clean_text[7:]
                    if clean_text.endswith("```"):
                        clean_text = clean_text[:-3]
                        
                    result_json = json.loads(clean_text.strip())
                    st.success("문구 생성이 완료되었습니다! 🎉")
                    
                    st.markdown("---")
                    st.markdown("### 📝 네이버/티스토리 블로그 포스팅")
                    st.text_input("블로그 제목", result_json["blog"]["title"], key="out_blog_title")
                    st.text_area("블로그 본문", result_json["blog"]["content"], height=220, key="out_blog_content")
                    
                    st.markdown("---")
                    st.markdown("### 📸 인스타그램 마케팅 문구")
                    st.text_area("인스타그램 복사 영역", result_json["instagram"]["content"], height=180, key="out_ig")
                    
                    st.markdown("---")
                    st.markdown("### 💬 카카오톡 (단톡방/채널) 메시지 문구")
                    st.text_area("카카오톡 복사 영역", result_json["kakao"]["content"], height=150, key="out_kakao")
                    
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {e}")
    else:
        st.info("왼쪽에서 이미지를 업로드하고 **'문구 생성하기'** 버튼을 클릭해 주세요.")