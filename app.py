import streamlit as st
import google.generativeai as genai
from docx import Document
import io

# --- 页面基础设置 ---
st.set_page_config(
    page_title="智慧教案小助手",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 智慧教案小助手")
st.caption("上传您的课程讲稿，AI为您一键生成教案初稿。")

# --- API Key配置 ---
# 为了安全，建议使用st.secrets管理API Key，但为方便本地运行，先用侧边栏输入
# 新代码
# --- API Key配置 ---
# 从Streamlit的Secrets中安全地读取API Key
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    st.sidebar.success("AI引擎已准备就绪！")
except:
    st.sidebar.error("请先在云端配置您的Google API密钥。")

# --- 核心功能函数 ---
def generate_lesson_plan(lecture_text, template_type, extra_info):
    """调用AI模型生成教案的核心函数"""
    model = genai.GenerativeModel('gemini-1.5-flash') # 或者使用 gemini-1.5-pro

    # 根据模板选择不同的指令
    if template_type == "理论教学":
        template_prompt = """
        请严格按照【理论教学模板】的结构，为以下课程讲稿生成一份详细的教案。
        规则：
        1. 教学目标需包含素质、知识、能力三个维度。
        2. 教学重难点的“解决措施”部分请简略描述方法即可。
        3. 对于模板中要求，但讲稿未明确提及的环节（如复习旧课、课堂小结、教学反思），请你创造性地设计和生成。
        4. 语言风格需专业、严谨，符合高职教学规范。
        """
    else: # 理实一体教学
        template_prompt = """
        请严格按照【理实一体教学模板】的结构，为以下课程讲稿生成一份详细的教案。
        规则：
        1. 教学目标需包含素质、知识、能力三个维度。
        2. 教学重难点的“解决措施”部分请简略描述方法即可。
        3. 对于模板中要求，但讲稿未明确提及的环节（如组织教学、课堂小结、教学反思），请你创造性地设计和生成。
        4. “新课教学”部分必须包含“知识储备”、“实操任务布置”、“实操”三个子环节。
        """
    
    final_prompt = f"""
    {template_prompt}

    # 辅助信息:
    课程名称: {extra_info['course_name']}
    授课班级: {extra_info['class_name']}
    授课日期: {extra_info['course_date']}

    # 课程讲稿内容:
    ---
    {lecture_text}
    ---

    # 现在，请生成教案:
    """

    try:
        response = model.generate_content(final_prompt)
        return response.text
    except Exception as e:
        return f"生成失败，发生错误：{e}"

# --- 主界面布局 ---
col1, col2 = st.columns(2)

with col1:
    st.header("1. 输入信息")
    
    template_choice = st.radio(
        "选择教案模板",
        ("理论教学", "理实一体教学"),
        horizontal=True
    )

    uploaded_file = st.file_uploader("上传课程讲稿 (.docx)", type=["docx"])

    st.subheader("辅助信息")
    course_name = st.text_input("课程名称")
    class_name = st.text_input("授课班级")
    course_date = st.date_input("授课日期")

    generate_button = st.button("✨ 一键生成教案", type="primary", use_container_width=True)

with col2:
    st.header("2. AI生成结果")
    
    if generate_button:
        if not api_key:
            st.error("请输入API密钥后再生成。")
        elif uploaded_file is not None:
            with st.spinner("AI正在奋笔疾书中，请稍候..."):
                # 读取Word文档内容
                doc = Document(uploaded_file)
                full_text = [para.text for para in doc.paragraphs]
                lecture_content = "\n".join(full_text)
                
                extra_info_dict = {
                    "course_name": course_name,
                    "class_name": class_name,
                    "course_date": str(course_date)
                }
                
                # 调用AI生成
                generated_plan = generate_lesson_plan(lecture_content, template_choice, extra_info_dict)
                
                st.text_area("教案初稿（可复制）", value=generated_plan, height=600)
        else:
            st.warning("请先上传您的课程讲稿。")

st.sidebar.markdown("---")
st.sidebar.info("本工具由Streamlit驱动，AI核心为Google Gemini。")
