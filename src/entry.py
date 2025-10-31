from workers import WorkerEntrypoint, Response
import json
from openai import OpenAI

class Default(WorkerEntrypoint):
    async def fetch(self, request, env):
        # 处理 CORS 预检请求
        if request.method == "OPTIONS":
            return Response.json({}, headers=self._get_cors_headers())

        if request.method == "GET":
            return Response("Hello there:)")

        # 处理 POST 请求
        if request.method != 'POST':
            return Response.json(
                {'error': 'Method not allowed'}, 
                status=405,
                headers=self._get_cors_headers()
            )
        try:
            # 解析请求体
            body = await request.json()
            q = body.get('q', '').strip()
            
            # 验证输入
            if not q:
                return Response.json(
                    {
                        'success' : False,
                        'error': 'missing q'
                    }, 
                    status=400,
                    headers=self._get_cors_headers()
                )
            # 提取回复内容
            answer = self.ai_api(q)
            # 返回响应
            return Response.json({
                'success' : True,
                'result': answer
            }, headers=self._get_cors_headers())
            
        except json.JSONDecodeError:
            return Response.json(
                {'error': 'Invalid JSON in request body'}, 
                status=400,
                headers=self._get_cors_headers()
            )
        except Exception as e:
            return Response.json(
                {'error': f'Internal server error: {str(e)}'}, 
                status=500,
                headers=self._get_cors_headers()
            )
    
    def _get_cors_headers(self):
        """获取 CORS 头信息"""
        return {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS, GET",
            "Access-Control-Allow-Headers": "Content-Type, Authorization"
        }
    
    def ai_api(self, q):
        client = OpenAI(api_key="sk-dc5ae06c3bee483db2dd01ea5fbc004a", base_url="https://api.deepseek.com/v1")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "user", "content": q},
            ],
            stream=False
        )
        return response.choices[0].message.content
    
