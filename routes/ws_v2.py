import json
from fastapi import APIRouter,WebSocket, WebSocketDisconnect ,Depends
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
from core.security import get_current_user
from agent_v2.agent import ws_agent
from services.memory_service import get_session_messages,save_session_messages


router=APIRouter(tags=["ws-v2"])
runner=InMemoryRunner(agent=ws_agent,app_name="ai_agent_ws")

@router.websocket("/ws/v2/{session_id}")
async def websocket_v2(websocket: WebSocket, session_id:str):
    await websocket.accept()

    history = []
    message_count = 0
    user_id = 1  # fill fix after

    history = await get_session_messages(user_id,session_id)

    adk_session = await runner.session_service.create_session(
        app_name="ai_agent_ws",
        user_id=str(user_id)
    )

    try:
        while True:
            question = await websocket.receive_text()
            history.append({"role":"user","content":question})
            message_count+=1

            async for event in runner.run_async(
                user_id=str(user_id),
                session_id=adk_session.id,
                new_message=Content(
                    role="user",
                    parts=[Part(text=question)]
                )
            ):
                if event.content and event.content.parts:
                    part = event.content.parts[0]

                    #tool call event
                    if hasattr(part,"function_call") and part.function_call:
                        await websocket.send_text(json.dumps({
                            "type":"tool_call",
                            "tool":part.function_call.name,
                            "input":str(part.function_call.args)
                        }))
                    
                    #tool result event
                    elif hasattr(part, "function_response") and part.function_response:
                        await websocket.send_text(json.dumps({
                            "type":"tool_result",
                            "tool":part.function_response.name,
                            "output":str(part.function_response.response)
                        }))

                    #final answer
                    elif event.is_final_response() and hasattr(part,"text") and part.text:
                        history.append({"role":"assistant","content":part.text})
                        await websocket.send_text(json.dumps({
                            "type":"answer",
                            "text":part.text
                        }))
                #periodic flush for every 3 messages
                if message_count % 3 == 0:
                    await save_session_messages(user_id,session_id,history)
    
    except WebSocketDisconnect:
        #saving to Redis on disconnect
        await save_session_messages(user_id,session_id,history)