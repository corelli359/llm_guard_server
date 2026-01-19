import time
import json
from sanic import Sanic, Request, response
from sanic.log import logger

# 获取名为 'audit' 的特定 logger，该 logger 在 logging_config 中配置为只写文件
audit_logger = logger.getChild("audit") # 实际上 sanic.log.logger 是 root 下的，我们需要获取独立的

import logging
audit_logger = logging.getLogger("audit")


def setup_audit_middleware(app: Sanic):
    
    @app.on_request
    async def on_request(request: Request):
        request.ctx.start_time = time.time()

    @app.on_response
    async def on_response(request: Request, response: response.BaseHTTPResponse):
        try:
            latency = (time.time() - request.ctx.start_time) * 1000 # ms
            
            # 尝试解析 request body，如果是 json
            req_body = None
            try:
                if request.json:
                    req_body = request.json
            except:
                req_body = request.body.decode('utf-8') if request.body else None

            # 尝试解析 response body
            res_body = None
            # 注意：流式响应 (StreamResponse) 可能拿不到 body，需要特殊处理，这里先处理普通响应
            if hasattr(response, "body") and response.body:
                 try:
                     res_body = json.loads(response.body)
                 except:
                     res_body = response.body.decode('utf-8')[:1000] # 截断防止过长

            log_entry = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "level": "INFO",
                "logger": "audit",
                "method": request.method,
                "path": request.path,
                "status": response.status,
                "latency_ms": round(latency, 2),
                "client_ip": request.remote_addr or request.ip,
                "request": req_body,
                "response": res_body,
                # "request_id": request.headers.get("X-Request-ID") # 如果有 gateway 传透
            }
            
            # 使用 json.dumps 确保只有一行，方便 filebeat 采集
            audit_logger.info(json.dumps(log_entry, ensure_ascii=False))

        except Exception as e:
            # 审计日志自身报错不能影响业务，打印错误即可
            logger.error(f"Audit Log Error: {e}")
