import streamlit as st
import requests

# Streamlit 用户界面
st.title("AItranslater")
st.write("在线版，仅支持API")
mode = "使用API"
if mode == "使用API":
    # 选择认证方式
    auth_method = st.radio("请选择认证方式:", ("API密钥", "账号密码"))

    # 用户输入API的URL
    API_URL = st.text_input("请输入翻译API的URL", "https://api.lingyiwanwu.com/v1/chat/completions")
    API_KEY = 0
    if auth_method == "API密钥":
        # 用户输入API密钥
        API_KEY = st.text_input("请输入API密钥", type="password")  # 密钥输入框，隐藏输入
    else:
        # 用户输入用户名和密码
        USERNAME = st.text_input("请输入用户名")
        PASSWORD = st.text_input("请输入密码", type="password")  # 密码输入框，隐藏输入
        if PASSWORD==st.secrets.admin_password.password and USERNAME==st.secrets.admin_password.username:
            API_KEY = st.secrets.admin_password.API_KEY

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

# 提示信息
st.write("请输入要翻译的文本：")

# 文本输入框
src_text = st.text_area("输入文本")

if st.button("翻译"):
    if src_text:
        if not API_URL or 'selected_model' not in st.session_state:
            st.error("请提供有效的API URL和选择模型！")
        else:
            # 确定认证方式
            if auth_method == "API密钥" and not API_KEY:
                st.error("请提供有效的API密钥！")
            elif auth_method == "账号密码" and (not USERNAME or not PASSWORD):
                st.error("请提供有效的用户名和密码！")
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
                        st.error("认证错误：API Key或用户名密码无效，请确保你的认证信息有效。")
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
        st.warning("请输入要翻译的文本！")