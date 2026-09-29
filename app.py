import os
import json
import streamlit as st
from PIL import Image
from google import genai
from google.genai import types

# 1. 웹 페이지 기본 설정
st.set_page_config(
    page_title="이벤트 이미지 맞춤형 광고 문구 생성기 (Gemini)",
    page_icon="🎨",
    layout="wide"
)

# 세션 상태 초기화
if "gemini_api_key" not in st.session_state:
    st.session_state["gemini_api_key"] = ""
if "result_data" not in st.session_state:
    st.session_state["result_data"] = None

# 2. 사이드바 - 설정 영역
with st.sidebar:
    st.header("⚙️ 웹 프로그램 설정")
    api_key_input = st.text_input(
        "Gemini API Key 입력", 
        type="password", 
        value=st.session_state["gemini_api_key"],
        help="Google AI Studio에서 발급받은 Gemini API Key를 입력하세요."
    )
    if api_key_input:
        st.session_state["gemini_api_key"] = api_key_input
        
    model_choice = st.selectbox(
        "사용할 AI 모델",
        ["gemini-2.5-flash", "gemini-2.5-pro"],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### 💡 이용 가이드")
    st.markdown("1. 사이드바에 Gemini API Key를 입력합니다.\n2. 이벤트 포스터 이미지를 업로드합니다.\n3. 추가 요구사항이 있다면 적어주세요.\n4. 생성 버튼을 누르고 플랫폼별 문구를 확인하세요!")

# 3. 메인 화면 UI
st.title("🎨 이벤트 이미지 플랫폼별 광고 문구 생성 웹 프로그램")
st.write("홍보용 이벤트 이미지를 업로드하면, Gemini AI가 이미지를 분석해 **인스타그램, 블로그, 페이스북, X(트위터)** 맞춤형 문구를 만들어 드립니다.")

col_left, col_right = st.columns([1, 1.5], gap="large")

with col_left:
    st.subheader("1️⃣ 이미지 및 옵션 입력")
    uploaded_file = st.file_uploader("이벤트 이미지 업로드 (PNG, JPG)", type=["png", "jpg", "jpeg"])
    
    image = None
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="업로드된 이벤트 이미지", use_container_width=True)
        
    extra_request = st.text_area(
        "추가 요구사항 (선택사항)", 
        placeholder="예: '선착순 50명 마감 강조해줘', '20대 대상 친근한 반말로 해줘'",
        key="extra_request_input"
    )
    
    generate_btn = st.button("🚀 플랫폼별 광고 문구 생성하기", type="primary", use_container_width=True)

with col_right:
    st.subheader("2️⃣ 플랫폼별 생성 결과")
    
    if generate_btn:
        if not st.session_state["gemini_api_key"]:
            st.error("⚠️ 사이드바에 Gemini API Key를 먼저 입력해주세요!")
        elif image is None:
            st.warning("⚠️ 분석할 이벤트 이미지를 업로드해주세요!")
        else:
            with st.spinner("🤖 Gemini가 이미지를 분석하고 플랫폼별 맞춤 카피를 작성 중입니다..."):
                try:
                    client = genai.Client(api_key=st.session_state["gemini_api_key"])
                    
                    prompt = f"""
                    당신은 10년 차 전문 마케터이자 각 SNS 플랫폼 알고리즘을 꿰뚫고 있는 카피라이터입니다.
                    사용자가 제공한 이벤트 이미지를 분석하여 인스타그램, 블로그, 페이스북, X(트위터)에 최적화된 마케팅 문구를 작성하세요.
                    추가 요구사항: {extra_request if extra_request else '없음'}
                    
                    반드시 아래의 JSON 구조로만 응답해주세요. 다른 텍스트는 포함하지 마세요.
                    {{
                      "instagram": {{
                        "content": "인스타그램용 본문 (이모지 풍성하게, 가독성 좋은 줄바꿈, 하단 해시태그 10개 포함)"
                      }},
                      "blog": {{
                        "title": "검색 유입용 블로그 포스팅 제목",
                        "content": "블로그용 본문 (도입부, 이벤트 상세 내용, 참여 방법, 유의사항 구조 포함)"
                      }},
                      "facebook": {{
                        "content": "페이스북용 본문 (친근하고 소통하는 톤, 참여 링크 유도 CTA 포함)"
                      }},
                      "twitter": {{
                        "content": "X(트위터)용 본문 (280자 내외, 직관적이고 트렌디한 요약 문구)"
                      }}
                    }}
                    """
                    
                    response = client.models.generate_content(
                        model=model_choice,
                        contents=[image, prompt],
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                        ),
                    )
                    
                    # 결과를 세션 상태에 저장하여 UI 충돌 방지
                    st.session_state["result_data"] = json.loads(response.text)
                    st.success("문구 생성이 완료되었습니다! 🎉")
                    
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {e}")

    # 세션에 저장된 결과가 있는 경우 화면에 안전하게 렌더링
    if st.session_state["result_data"]:
        result_json = st.session_state["result_data"]
        
        tab_ig, tab_blog, tab_fb, tab_tw = st.tabs(["📸 인스타그램", "📝 블로그", "📘 페이스북", "✖️ X (트위터)"])
        
        with tab_ig:
            st.markdown("### 인스타그램 마케팅 문구")
            st.text_area("복사해서 사용하세요", result_json["instagram"]["content"], height=300, key="safe_res_ig")
            
        with tab_blog:
            st.markdown("### 네이버/티스토리 블로그 포스팅")
            st.text_input("블로그 제목", result_json["blog"]["title"], key="safe_res_blog_title")
            st.text_area("블로그 본문", result_json["blog"]["content"], height=300, key="safe_res_blog_content")
            
        with tab_fb:
            st.markdown("### 페이스북 광고 문구")
            st.text_area("복사해서 사용하세요", result_json["facebook"]["content"], height=300, key="safe_res_fb")
            
        with tab_tw:
            st.markdown("### X (트위터) 문구")
            st.text_area("복사해서 사용하세요", result_json["twitter"]["content"], height=250, key="safe_res_tw")
    else:
        if not generate_btn:
            st.info("왼쪽에서 이미지를 업로드하고 **'플랫폼별 광고 문구 생성하기'** 버튼을 클릭해 주세요.")
