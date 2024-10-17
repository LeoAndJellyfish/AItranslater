import streamlit as st
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import os
import requests

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
st.write("请选择翻译方式：")

# 默认选择API模式
mode = st.selectbox("选择翻译方式", ("使用API", "使用模型"))

if mode == "使用API":
    # 用户输入API的URL和API密钥
    API_URL = st.text_input("请输入翻译API的URL", "https://api.lingyiwanwu.com/v1/chat/completions")
    API_KEY = st.text_input("请输入API密钥", type="password")  # 密钥输入框，隐藏输入

    # 当用户输入API密钥后自动获取模型列表
    if API_KEY:
        try:
            headers = {
                'Authorization': f'Bearer {API_KEY}'
            }
            model_response = requests.get('https://api.lingyiwanwu.com/v1/models', headers=headers)
            if model_response.status_code == 200:
                models = model_response.json().get('data', [])
                model_list = [model['id'] for model in models]
                selected_model = st.selectbox("请选择使用的模型", model_list, key="model_selection")
                st.session_state.selected_model = selected_model
                if 'selected_model' in st.session_state:
                    st.write("当前选择的模型:", st.session_state.selected_model)
                else:
                    st.error("未选择模型！")
            else:
                st.error(f"获取模型失败，错误代码: {model_response.status_code}")
        except Exception as e:
            st.error(f"获取模型过程中发生错误: {str(e)}")
else:
    st.write("请选择翻译方向：")
    translation_direction = st.selectbox("翻译方向", ("中译英", "英译中"))

    # 根据选择加载相应的模型
    model_name = 'Helsinki-NLP/opus-mt-zh-en' if translation_direction == "中译英" else 'Helsinki-NLP/opus-mt-en-zh'
    if 'model' not in st.session_state or st.session_state.get('last_direction') != translation_direction:
        st.session_state.last_direction = translation_direction
        try:
            st.session_state.model, st.session_state.tokenizer = load_model(model_name)
            st.success("模型加载成功！")
        except Exception as e:
            st.error(f"加载模型失败: {str(e)}")

# 提示信息
st.write("请输入要翻译的文本：")

# 文本输入框
src_text = st.text_area("输入文本")

if st.button("翻译"):
    if src_text:
        if mode == "使用API":
            if not API_URL or 'selected_model' not in st.session_state:
                st.error("请提供有效的API URL和选择模型！")
            else:
                if not API_KEY:
                    st.error("请提供有效的API密钥！")
                else:
                    try:
                        # 构造请求的body
                        messages = [
                            {"role": "system", "content": "你是一个翻译助手，负责根据用户的需求进行文本翻译，默认为中英互译。"},
                            {"role": "user", "content": src_text}
                        ]
                        
                        # 发送请求到第三方API
                        payload = {
                            "model": st.session_state.selected_model,  # 使用会话状态中的模型
                            "messages": messages
                        }
                        headers = {
                            'Authorization': f'Bearer {API_KEY}',
                            'Content-Type': 'application/json'
                        }
                        response = requests.post(API_URL, json=payload, headers=headers)

                        # 根据状态码进行错误处理
                        if response.status_code == 200:
                            result = response.json().get('choices')[0].get('message').get('content')  # 根据API的返回格式获取翻译结果
                            st.write("翻译结果：")
                            st.success(result)
                        elif response.status_code == 400:
                            st.error("请求错误：模型的输入超过了模型的最大上下文，或输入格式错误。请检查输入。")
                        elif response.status_code == 401:
                            st.error("认证错误：API Key缺失或无效，请确保你的API Key有效。")
                        elif response.status_code == 404:
                            st.error("未找到：无效的Endpoint URL或模型名，请确保使用正确的Endpoint URL或模型名。")
                        elif response.status_code == 429:
                            st.error("请求过多：在短时间内发出的请求太多，请控制请求速率。")
                        elif response.status_code == 500:
                            st.error("内部服务器错误：服务端出现问题，请稍后重试。")
                        elif response.status_code == 529:
                            st.error("系统繁忙：请稍后再试。")
                        else:
                            st.error(f"翻译失败，错误代码: {response.status_code}")
                    except Exception as e:
                        st.error(f"翻译过程中发生错误: {str(e)}")
        else:
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