from workers import WorkerEntrypoint, Response
import js.fetch
import json
from urllib.parse import urlparse, parse_qs


class Default(WorkerEntrypoint):
    async def fetch(self, request, env):
        # 处理 CORS 预检请求
        if request.method == "OPTIONS":
            return Response.json({}, headers=self._get_cors_headers())

        # if request.method == "GET":
        #     return Response("Hello there:)")

        # # 处理 POST 请求
        # if request.method != 'POST':
        #     return Response.json(
        #         {'error': 'Method not allowed'}, 
        #         status=405,
        #         headers=self._get_cors_headers()
        #     )
        try:
            # 解析请求体
            # body = await request.json()
            # q = body.get('q', '').strip()
            url = urlparse(request.url)
            params = parse_qs(url.query)
            q = params["q"][0]
            # 验证输入
            if not q:
                return Response.json(
                    {
                        'success' : False,
                        'error': 'missing param q'
                    }, 
                    headers=self._get_cors_headers()
                )
            # 提取回复内容
            result = await self.ai_api(q)
            if result.get('success') == False:
                return Response.json({
                    'success' : False,
                    'error': result.get('error')
                }, headers=self._get_cors_headers())

            if answer is None:
                return Response.json(
                    {'success' : False,'error': answer}, 
                    headers=self._get_cors_headers()
                )
            # 返回响应
            return Response.json(
                    {'success' : True,'result': answer}, 
                    headers=self._get_cors_headers()
                )
        except json.JSONDecodeError:
            return Response.json(
                {'success' : False,'error': 'Invalid JSON in request body'}, 
                headers=self._get_cors_headers()
            )
        except Exception as e:
            return Response.json(
                {'success' : False, 'error': f'Internal server error: {str(e)}'}, 
                headers=self._get_cors_headers()
            )
    
    def _get_cors_headers(self):
        return {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS, GET",
            "Access-Control-Allow-Headers": "Content-Type, Authorization"
        }
    
    async def ai_api(self, q):
        api_key = "sk-dc5ae06c3bee483db2dd01ea5fbc004a"
        deepseek_url = "https://api.deepseek.com/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [{
                "role": "user",
                "content": q
            }],
            "stream": False
        }
        # 调用API
        response = await js.fetch(deepseek_url, {
            "method": "POST",
            "headers": headers,
            "body": json.dumps(payload)
        })
        if not response.ok:
            error_text = await response.text()
            return {
                "success" : False,
                "error" : error_text
            }
        # 解析 DeepSeek API 响应
        result_data = await response.json()
        # 提取回复内容
        if (result_data.get('choices') and len(result_data['choices']) > 0 and result_data['choices'][0].get('message')):
            answer = result_data['choices'][0]['message']['content']
            return {
                "success" : True,
                "answer" : answer
            }
        return {
            "success" : False,
            "error" : "no valid answer"
        }
        
