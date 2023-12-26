from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import erniebot
import os

app = FastAPI()
origins = [
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

# Set authentication params
erniebot.api_type = "aistudio"
erniebot.access_token = os.getenv("ACCESS_TOKEN")

system="""你是一个文字推理游戏“狼人杀”的游戏玩家，狼人杀的游戏说明和规则如下：

### 玩家与角色设置 ###
游戏共9个玩家参与，分别扮演5种角色，其中，1个玩家扮演预言家，1个玩家扮演女巫，1个玩家扮演猎人，3个玩家扮演村民，3个玩家扮演狼人。

### 阵营设置 ###
游戏分为“狼人阵营”和“好人阵营”。
狼人阵营里只有狼人一种角色。
好人阵营里有“村民”、“预言家”、“女巫”和“猎人”四种角色。
“预言家”、“女巫”和“猎人”为神。

### 获胜条件 ###
若所有的神或者所有的村民死亡，则判定狼人阵营获胜。
若所有的狼人死亡，则判定好人阵营获胜。

### 角色介绍 ###
预言家：身份是神，技能是每天晚上可以查验一名玩家的真实身份属于好人阵营还是狼人阵营，简称“好人”或“狼人”。
女巫：身份是神，技能是有两瓶药水，一瓶是灵药，可以在晚上救活被杀死的玩家包括自己。一瓶是毒药，可以在晚上毒死除自己外的任意玩家。
猎人：身份是神，技能是被狼人杀害或者被投票处决后，可以开枪射杀任意一个玩家；请注意，当猎人被毒死时，技能无法使用。
村民：身份是平民，没有技能。
狼人：身份是狼人，技能是存活的狼人每天晚上可以共同袭击杀死一个玩家；狼人在发言时，可以假冒预言家、女巫或猎人以迷惑其它好人。

### 游戏常用语 ###
查杀：指预言家查验结果为狼人的玩家。
金水：指预言家查验结果为好人的玩家。
银水：指女巫救活的玩家。
有身份：指自己的角色不是村民。
强神：指技能比较厉害的神。
悍跳：指有狼人嫌疑的玩家称自己为神。
对跳：指有狼人嫌疑的玩家称自己为神或指在其他玩家宣称自己为神后，有玩家宣称其神的身份为假，自己才是真神。
刀口：指狼人在晚上杀死的玩家。
挡刀：指好人玩家伪装自己的身份迷惑狼人，让狼人杀死自己，避免更重要的玩家被杀的套路。
扛推：指好人玩家在发言环节被怀疑而被投票处决。

### 游戏规则 ###
1.狼人每晚必须杀人。
2.预言家每晚必须查验，且每天必须跳出来报查验结果。
3.女巫第一晚必须救人，且每天必须跳出来报救了谁毒了谁。
4.狼人假冒预言家时，不可以给狼人和刀口发金水。
5.狼人假冒女巫时，不可以给狼人和刀口发银水。
6.村民可以假冒猎人，但不可以假冒预言家和女巫。
"""


class ChatBody(BaseModel):
    model: str = Field(
        title="默认模型",
        default="ernie-bot",
        pattern=r"^ernie-bot(-4)?(-turbo)?$",
    )
    temperature: float = Field(title="temperature", default=0.95, min=0.01, max=1.0)
    top_p: float = Field(title="top_p", default=0.8, min=0.01, max=1.0)
    penalty_score: float = Field(
        title="penalty_score", default=1.0, min=1.0, max=2.0
    )
    api_key: str = Field(title="API Key", default=os.getenv("QIANFAN_AK"))
    secret_key: str = Field(title="Secret Key", default=os.getenv("QIANFAN_SK"))
    prompt: str = Field(..., title="对话内容")


@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}

@app.post("/chat")
async def chat(chatBody: ChatBody):
    try:
        response = erniebot.ChatCompletion.create(
            model=chatBody.model,
            temperature=chatBody.temperature,
            top_p=chatBody.top_p,
            penalty_score=chatBody.penalty_score,
            system=system,
            messages=[
                {
                    "role": "user",
                    "content": chatBody.prompt
                }
            ])
        return {"status": "ok", "result": response.get_result()}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/", response_class=HTMLResponse)
async def index():
    return """
        <!DOCTYPE html>
        <html lang="en">

        <head>
        <meta charset="UTF-8">
        <link rel="icon" href="/assets/logo-vV0L7iSP.png">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI狼人杀</title>
        <script type="module" crossorigin src="/assets/index-UPX9kkZO.js"></script>
        <link rel="stylesheet" crossorigin href="/assets/index-iRHCnFKE.css">
        </head>

        <body>
        <div id="app"></div>
        </body>

        </html>
    """