import streamlit as st
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import os

# 定义设备
device = 'cuda' if torch.cuda.is_available() else 'cpu'

# 定义模型保存路径
model_dir = 'models'
os.makedirs(model_dir, exist_ok=True)  # 创建模型文件夹（如果不存在）

# 下载并加载模型
def load_model(model_name):
    model_path = os.path.join(model_dir, model_name)
    if not os.path.exists(model_path):
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model.save_pretrained(model_path)
        tokenizer.save_pretrained(model_path)
    else:
        model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
        tokenizer = AutoTokenizer.from_pretrained(model_path)
    return model.to(device), tokenizer

# Streamlit 用户界面
st.title("实时翻译应用")
st.write("请选择翻译方向：")

# 添加选择框让用户选择翻译方向
translation_direction = st.selectbox("翻译方向", ("中译英", "英译中"))

# 根据选择加载相应的模型
model_name = 'Helsinki-NLP/opus-mt-zh-en' if translation_direction == "中译英" else 'Helsinki-NLP/opus-mt-en-zh'
if 'model' not in st.session_state or st.session_state.get('last_direction') != translation_direction:
    st.session_state.last_direction = translation_direction
    try:
        st.session_state.model, st.session_state.tokenizer = load_model(model_name)
    except Exception as e:
        st.error(f"加载模型失败: {str(e)}")

# 提示信息
st.write("请输入要翻译的文本：")

# 文本输入框
src_text = st.text_area("输入文本")

if st.button("翻译"):
    if src_text:
        try:
            # 转换输入并生成翻译
            input_ids = st.session_state.tokenizer(src_text, return_tensors="pt", padding=True, truncation=True).to(device)
            generated_tokens = st.session_state.model.generate(**input_ids)
            result = st.session_state.tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
            
            # 显示翻译结果
            st.write("翻译结果：")
            st.success(result)
        except Exception as e:
            st.error(f"翻译过程中发生错误: {str(e)}")
    else:
        st.warning("请输入要翻译的文本！")
