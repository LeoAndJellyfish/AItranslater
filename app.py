import streamlit as st
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

# 定义设备
device = 'cuda' if torch.cuda.is_available() else 'cpu'

# Streamlit 用户界面
st.title("实时翻译应用")
st.write("请选择翻译方向：")

# 添加选择框让用户选择翻译方向
translation_direction = st.selectbox("翻译方向", ("中译英", "英译中"))

# 在 Streamlit 中使用 session_state 来存储模型和分词器
if 'model' not in st.session_state or 'tokenizer' not in st.session_state:
    if translation_direction == "中译英":
        model_name = 'Helsinki-NLP/opus-mt-zh-en'
    else:
        model_name = 'Helsinki-NLP/opus-mt-en-zh'

    st.session_state.model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(device)
    st.session_state.tokenizer = AutoTokenizer.from_pretrained(model_name)

# 如果用户选择了不同的翻译方向，重新加载模型和分词器
if st.session_state.get('last_direction') != translation_direction:
    st.session_state.last_direction = translation_direction
    if translation_direction == "中译英":
        model_name = 'Helsinki-NLP/opus-mt-zh-en'
    else:
        model_name = 'Helsinki-NLP/opus-mt-en-zh'

    st.session_state.model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(device)
    st.session_state.tokenizer = AutoTokenizer.from_pretrained(model_name)

# 提示信息
st.write("请输入要翻译的文本：")

# 文本输入框
src_text = st.text_area("输入文本")

if st.button("翻译"):
    if src_text:
        # 添加输入文本
        input_text = src_text

        # 转换输入并生成翻译
        input_ids = st.session_state.tokenizer(input_text, return_tensors="pt", padding=True, truncation=True).to(device)
        generated_tokens = st.session_state.model.generate(**input_ids)
        result = st.session_state.tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]

        # 显示翻译结果
        st.write("翻译结果：")
        st.success(result)
    else:
        st.warning("请输入要翻译的文本！")