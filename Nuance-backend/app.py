import logging
from flask import Flask, request, jsonify
from flask_cors import CORS  # 使用正式的flask-cors扩展
from conversation import ConversationAgent
from polish import ArticlePolisher

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('api.log')
    ]
)

app = Flask(__name__)
agent = ConversationAgent()

# 正确的CORS配置
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:8080", "http://127.0.0.1:8080"],
        "methods": ["OPTIONS", "POST", "GET"],
        "allow_headers": ["Content-Type", "X-Request-ID"],
        "supports_credentials": False
    }
})

# app.py 中添加性能日志和超时控制
from datetime import datetime

@app.before_request
def log_request_start():
    request.start_time = datetime.now()
    logging.info(f"Request started: {request.method} {request.path}")

@app.after_request
def log_request_completion(response):
    duration = (datetime.now() - request.start_time).total_seconds()
    logging.info(f"Request completed in {duration:.2f}s - Status: {response.status_code}")
    response.headers['X-Process-Time'] = str(duration)
    return response
@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    logging.info("Health check received")
    return jsonify({"status": "healthy", "service": "conversation-api"})



@app.route('/api/start', methods=['POST', 'OPTIONS'])
def start_session():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()

    # 统一校验逻辑
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    data = request.get_json()
    if not data:
        return jsonify({"error": "Empty request body"}), 400

    if 'session_id' not in data or 'mood' not in data:
        return jsonify({"error": "Missing session_id or mood"}), 400

    try:
        start_time = datetime.now()
        logging.info(f"Start session data: {data}")

        result = agent.start_session(data['session_id'], data['mood'])
        logging.info(f"Session started: {result}")

        return jsonify(result)
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/reply', methods=['POST', 'OPTIONS'])
def handle_reply():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()

    try:
        data = request.get_json()
        logging.info(f"Reply request data: {data}")

        # 增强参数校验
        if not data or not isinstance(data, dict):
            error_msg = "Invalid request data format"
            logging.warning(error_msg)
            return jsonify({"error": error_msg}), 400

        session_id = data.get('session_id')
        user_input = data.get('user_input')

        if not session_id or not user_input:
            error_msg = "Missing session_id or user_input"
            logging.warning(error_msg)
            return jsonify({"error": error_msg}), 400

        # 确保user_input是字符串
        if not isinstance(user_input, str):
            user_input = str(user_input)
            logging.warning(f"Converted user_input to string: {user_input}")

        result = agent.user_reply(session_id, user_input)
        logging.info(f"Reply handled: {result}")

        if "error" in result and result['error']!=None:
            logging.error(f"Reply error: {result['error']}")
            return jsonify(result), 400

        return jsonify(result)
    except Exception as e:
        logging.error(f"Unexpected error in handle_reply: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/history/<session_id>', methods=['GET'])
def get_history(session_id):
    try:
        logging.info(f"Get history for session: {session_id}")
        history = agent.get_history(session_id)
        return jsonify({
            "session_id": session_id,
            "history": history
        })
    except Exception as e:
        logging.error(f"Error getting history: {str(e)}")
        return jsonify({"error": "Failed to get history"}), 500


@app.route('/api/end/<session_id>', methods=['POST'])
def end_session(session_id):
    try:
        logging.info(f"Ending session: {session_id}")
        agent.cleanup_session(session_id)
        return jsonify({
            "status": "success",
            "session_id": session_id
        })
    except Exception as e:
        logging.error(f"Error ending session: {str(e)}")
        return jsonify({"error": "Failed to end session"}), 500


def _build_cors_preflight_response():
    response = jsonify({"status": "preflight"})
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    response.headers.add("Access-Control-Allow-Methods", "POST")
    return response


@app.route('/api/generate-article', methods=['POST', 'OPTIONS'])
async def generate_article():
    """生成润色文章的API端点"""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()

    try:
        # 参数校验
        data = request.get_json()
        if not data or not isinstance(data, dict):
            return jsonify({"error": "Invalid request format"}), 400

        required_fields = ['session_id', 'mood']
        if any(field not in data for field in required_fields):
            return jsonify({"error": f"Missing required fields: {required_fields}"}), 400

        # 获取对话历史
        session_id = data['session_id']
        history = agent.get_history(session_id)
        if not history:

            return jsonify({"error": "No conversation history found"}), 404

        # 准备润色数据
        messages = [
            {"type": msg['role'], "text": msg['content']}
            for msg in history
            if msg['role'].lower() in ['user', 'ai']
        ]
        # 初始化实例
        polisher = ArticlePolisher()
        # 调用文章润色
        polish_result = await polisher.polish(
            messages=messages,
            mood=data['mood']
        )

        if polish_result["status"] != "success":
            return jsonify({
                "error": polish_result.get("error", "Article generation failed"),
                "details": polish_result
            }), 500

        return jsonify({
            "session_id": session_id,
            "article": polish_result["article"],
            "word_count": polish_result["word_count"],
            "generated_at": datetime.now().isoformat()
        })

    except Exception as e:
        logging.error(f"Article generation error: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


# 在app.py的顶部导入部分添加
from correct import WritingCorrectionAgent

# 在初始化部分添加（在agent = ConversationAgent()之后）
correction_agent = WritingCorrectionAgent()


# 新增API端点（可以放在generate_article端点之后）
@app.route('/api/analyze-writing', methods=['POST', 'OPTIONS'])
def analyze_writing():
    """分析用户写作并提供更正建议的独立端点"""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()

    try:
        # 参数校验
        data = request.get_json()
        logging.info(f"Analyze writing request data: {data}")

        if not data or not isinstance(data, dict):
            error_msg = "Invalid request data format"
            logging.warning(error_msg)
            return jsonify({"error": error_msg}), 400

        # 支持两种输入方式：
        # 1. 直接提供conversation_data
        # 2. 提供session_id从历史记录获取
        if 'conversation_data' in data:
            conversation_data = data['conversation_data']
            if not isinstance(conversation_data, list):
                return jsonify({"error": "conversation_data must be a list"}), 400
        elif 'session_id' in data:
            session_id = data['session_id']
            history = agent.get_history(session_id)
            if not history:
                return jsonify({"error": "No conversation history found"}), 404

            # 转换历史记录格式
            conversation_data = [
                {
                    "type": msg['role'],
                    "text": msg['content'],
                    "time": "unknown"  # 历史记录可能没有时间戳
                }
                for msg in history
                if msg['role'].lower() in ['user', 'ai']
            ]
        else:
            return jsonify({"error": "Must provide either conversation_data or session_id"}), 400

        # 调用分析功能
        result = correction_agent.analyze_writing(conversation_data)
        logging.info(f"Writing analysis result: {result}")

        if "error" in result:
            logging.error(f"Analysis error: {result['error']}")
            return jsonify(result), 500

        return jsonify({
            "status": "success",
            "analysis": result,
            "analyzed_at": datetime.now().isoformat()
        })

    except Exception as e:
        logging.error(f"Unexpected error in analyze_writing: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500
if __name__ == '__main__':
    logging.info("Starting conversation API server")
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )