import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

const NODE_ID = "AICG3D_CharacterCardStudio";
const STATE_WIDGET = "card_state";
const WIDTH_WIDGET = "width";
const HEIGHT_WIDGET = "height";
const CSS_URL = new URL("./character_card_studio.css", import.meta.url).href;
const SLOT_MIME = "application/x-character-card-slot";
const IMAGE_MIME = "application/x-character-card-image";

const FALLBACK_TEMPLATES = [
    {"id":"bighead_body3","name":"四格·偏立","description":"左侧一个大的正面头肩肖像，右侧并列正面/侧面/背面三个完整全身。","layout_prompt":"左右两栏：左栏只有1个大头肩肖像；右栏只有3个等宽全身竖格，依次为正面、侧面、背面。总共4格。","width":1920,"height":1200,"defaults":{"title":"未命名角色","subtitle":"角色设定","style":"统一角色资产，纯白棚拍背景，柔和棚拍光，写实电影级","background":"#ffffff","accent":"#d86b73"},"cells":[{"id":"head_big","label":"正面大头像","role":"portrait","prompt":"正面头肩肖像，头部到肩部完整入镜，五官和发饰清晰，正视镜头，画面里只有一个人。","x":0.03,"y":0.03,"w":0.4,"h":0.94,"mirror":false},{"id":"body_front","label":"正面全身","role":"turnaround","prompt":"正面完整全身站姿，双臂自然下垂，从头顶到鞋底完整不裁切，画面里只有一个人。","x":0.46,"y":0.12,"w":0.16,"h":0.78,"mirror":false},{"id":"body_side","label":"侧面全身","role":"turnaround","prompt":"严格90度左侧面完整全身，人物朝画面右侧，只能看到左半边脸和左耳，从头顶到鞋底完整不裁切。","x":0.635,"y":0.12,"w":0.16,"h":0.78,"mirror":false},{"id":"body_back","label":"背面全身","role":"turnaround","prompt":"严格180度背面完整全身，只能看到后脑和后背，从头顶到鞋底完整不裁切。","x":0.81,"y":0.12,"w":0.16,"h":0.78,"mirror":false}]},
    {"id":"dualfour_ref","name":"四格·双帧","description":"等分2×2：上排正面和四分之三头肩，下排正面和背面全身。","layout_prompt":"等分2行×2列：上排左格正面头肩、右格四分之三头肩；下排左格正面全身、右格背面全身。总共4格，不能增加第三排。","width":1920,"height":1200,"defaults":{"title":"未命名角色","subtitle":"双视设定","style":"统一角色资产，纯白棚拍背景，柔和棚拍光，写实电影级","background":"#ffffff","accent":"#6b8dd8"},"cells":[{"id":"head_front","label":"正面头像","role":"portrait","prompt":"正面头肩特写，头部到肩部完整入镜，正视镜头，不出现第二个人。","x":0.03,"y":0.03,"w":0.46,"h":0.43,"mirror":false},{"id":"head_three_quarter","label":"四分之三头像","role":"portrait","prompt":"四分之三侧脸头肩特写，脸朝画面右前方，能同时看到两侧脸颊轮廓，眼神看向镜头。","x":0.51,"y":0.03,"w":0.46,"h":0.43,"mirror":false},{"id":"body_front","label":"正面全身","role":"turnaround","prompt":"正面完整全身站姿，正视镜头，从头顶到鞋底完整不裁切，画面里只有一个人。","x":0.03,"y":0.52,"w":0.46,"h":0.45,"mirror":false},{"id":"body_back","label":"背面全身","role":"turnaround","prompt":"严格180度背面完整全身，只能看到后脑和后背，从头顶到鞋底完整不裁切。","x":0.51,"y":0.52,"w":0.46,"h":0.45,"mirror":false}]},
    {"id":"fiveref","name":"五格·正反","description":"上排正面和四分之三头肩，下排正面/侧面/背面三个完整全身。","layout_prompt":"两排结构：上排只有2格，都是头肩肖像；下排只有3格，都是完整全身。总共5格。","width":1920,"height":1200,"defaults":{"title":"未命名角色","subtitle":"五视设定","style":"统一角色资产，纯白棚拍背景，柔和棚拍光，写实电影级","background":"#ffffff","accent":"#65a89a"},"cells":[{"id":"head_front","label":"正面头像","role":"portrait","prompt":"正面头肩特写，头部到肩部完整入镜，正视镜头。","x":0.03,"y":0.03,"w":0.47,"h":0.43,"mirror":false},{"id":"head_three_quarter","label":"四分之三头像","role":"portrait","prompt":"四分之三侧脸头肩特写，脸朝画面右前方，眼神看向镜头，与正面头像角度明显不同。","x":0.5,"y":0.03,"w":0.47,"h":0.43,"mirror":false},{"id":"body_front","label":"正面全身","role":"turnaround","prompt":"正面完整全身站姿，从头顶到鞋底完整不裁切，画面里只有一个人。","x":0.03,"y":0.52,"w":0.305,"h":0.45,"mirror":false},{"id":"body_side","label":"侧面全身","role":"turnaround","prompt":"严格90度左侧面完整全身，人物朝画面右侧，从头顶到鞋底完整不裁切。","x":0.348,"y":0.52,"w":0.305,"h":0.45,"mirror":false},{"id":"body_back","label":"背面全身","role":"turnaround","prompt":"严格180度背面完整全身，只能看到后脑和后背，从头顶到鞋底完整不裁切。","x":0.665,"y":0.52,"w":0.305,"h":0.45,"mirror":false}]},
    {"id":"head_body_6","name":"六格·三视图","description":"上排正面/侧面/后脑三个头肩，下排正面/侧面/背面三个完整全身。","layout_prompt":"等分2排×3列：上排3格全是头肩肖像，下排3格全是完整全身。总共6格，不能生成九宫格。","width":1920,"height":1280,"defaults":{"title":"未命名角色","subtitle":"三视图设定","style":"统一角色资产，纯白棚拍背景，柔和棚拍光，写实电影级","background":"#ffffff","accent":"#6b8dd8"},"cells":[{"id":"head_front","label":"正面头像","role":"portrait","prompt":"正面头肩特写，头部到肩部完整入镜，正视镜头。","x":0.03,"y":0.03,"w":0.303,"h":0.43,"mirror":false},{"id":"head_side","label":"侧面头像","role":"portrait","prompt":"严格90度侧面头肩特写，人物朝画面右侧，只能看到左半边脸和左耳。","x":0.345,"y":0.03,"w":0.303,"h":0.43,"mirror":false},{"id":"head_back","label":"后脑头像","role":"portrait","prompt":"背面头肩特写，只能看到后脑和发型，看不到脸。","x":0.66,"y":0.03,"w":0.303,"h":0.43,"mirror":false},{"id":"body_front","label":"正面全身","role":"turnaround","prompt":"正面完整全身站姿，从头顶到鞋底完整不裁切，画面里只有一个人。","x":0.03,"y":0.52,"w":0.303,"h":0.45,"mirror":false},{"id":"body_side","label":"侧面全身","role":"turnaround","prompt":"严格90度左侧面完整全身，人物朝画面右侧，从头顶到鞋底完整不裁切。","x":0.345,"y":0.52,"w":0.303,"h":0.45,"mirror":false},{"id":"body_back","label":"背面全身","role":"turnaround","prompt":"严格180度背面完整全身，只能看到后脑和后背，从头顶到鞋底完整不裁切。","x":0.66,"y":0.52,"w":0.303,"h":0.45,"mirror":false}]},
    {"id":"sixtilt_ref","name":"六格·主视觉","description":"左侧大幅主立绘；右侧两排双格，底部横条面料细节。","layout_prompt":"非等分布局：左侧1个大幅主立绘；右侧上排2格（正面头像、微笑），中排2格（侧面全身、动作全身），右下1个横向面料细节条。总共6格。","width":1920,"height":1280,"defaults":{"title":"未命名角色","subtitle":"主视觉设定","style":"统一角色资产，纯白棚拍背景，柔和棚拍光，写实电影级","background":"#ffffff","accent":"#9b7dd8"},"cells":[{"id":"hero","label":"主立绘","role":"hero","prompt":"正面完整全身主立绘，自然站姿，从头顶到鞋底完整入镜，画面里只有一个人。","x":0.03,"y":0.08,"w":0.39,"h":0.84,"mirror":false},{"id":"head_front","label":"正面头像","role":"portrait","prompt":"正面头肩特写，头部到肩部完整入镜，正视镜头。","x":0.45,"y":0.08,"w":0.26,"h":0.25,"mirror":false},{"id":"ex_smile","label":"微笑表情","role":"expression","prompt":"头肩微笑特写，嘴角上扬、眼睛微弯，和正面冷静头像表情明显不同。","x":0.735,"y":0.08,"w":0.235,"h":0.25,"mirror":false},{"id":"body_side","label":"侧面全身","role":"turnaround","prompt":"严格90度左侧面完整全身，人物朝画面右侧，从头顶到鞋底完整不裁切。","x":0.45,"y":0.36,"w":0.26,"h":0.27,"mirror":false},{"id":"action_pose","label":"动作全身","role":"turnaround","prompt":"动态站姿完整全身，手臂动作与主立绘明显不同，从头顶到鞋底完整不裁切。","x":0.735,"y":0.36,"w":0.235,"h":0.27,"mirror":false},{"id":"de_fabric","label":"面料细节","role":"detail","prompt":"横向服饰面料与刺绣微距，只展示纹理、褶皱和金线，不出现人物脸部或全身。","x":0.45,"y":0.66,"w":0.52,"h":0.26,"mirror":false}]},
    {"id":"expr_body_8","name":"八格·表情谱","description":"上排4个不同表情头肩，下排正面/侧面/背面/动作四个完整全身。","layout_prompt":"等分2排×4列：上排4格全部是不同表情的头肩；下排4格全部是完整全身。总共8格。","width":1920,"height":1200,"defaults":{"title":"未命名角色","subtitle":"多视图设定","style":"统一角色资产，纯白棚拍背景，柔和棚拍光，写实电影级","background":"#ffffff","accent":"#d86b73"},"cells":[{"id":"head_neutral","label":"平静","role":"expression","prompt":"头肩特写，中性平静，嘴唇闭合，目光平视，面部放松。","x":0.03,"y":0.03,"w":0.225,"h":0.43,"mirror":false},{"id":"head_happy","label":"开心大笑","role":"expression","prompt":"头肩特写，张嘴露齿开心大笑，眼睛弯成月牙，和第一格表情明显不同。","x":0.268,"y":0.03,"w":0.225,"h":0.43,"mirror":false},{"id":"head_serious","label":"认真","role":"expression","prompt":"头肩特写，嘴唇紧抿、眉头微蹙，严肃直视镜头。","x":0.505,"y":0.03,"w":0.225,"h":0.43,"mirror":false},{"id":"head_surprised","label":"惊讶","role":"expression","prompt":"头肩特写，眼睛圆睁、眉毛抬高、嘴巴微张呈惊讶表情。","x":0.743,"y":0.03,"w":0.225,"h":0.43,"mirror":false},{"id":"body_front","label":"正面全身","role":"turnaround","prompt":"正面完整全身站姿，双臂自然下垂，从头顶到鞋底完整不裁切。","x":0.03,"y":0.52,"w":0.225,"h":0.45,"mirror":false},{"id":"body_profile","label":"左侧面全身","role":"turnaround","prompt":"严格90度左侧面完整全身，人物朝画面右侧，从头顶到鞋底完整不裁切。","x":0.268,"y":0.52,"w":0.225,"h":0.45,"mirror":false},{"id":"body_back","label":"背面全身","role":"turnaround","prompt":"严格180度背面完整全身，只能看到后脑和后背，从头顶到鞋底完整不裁切。","x":0.505,"y":0.52,"w":0.225,"h":0.45,"mirror":false},{"id":"body_action","label":"动作全身","role":"turnaround","prompt":"自然行走动作完整全身，步态与前三格站姿不同，从头顶到鞋底完整不裁切。","x":0.743,"y":0.52,"w":0.225,"h":0.45,"mirror":false}]},
    {"id":"school_ref","name":"十格·设定集","description":"左侧主立绘；右侧上排三视图、中排三表情、下排三细节。","layout_prompt":"左右两栏：左栏只有1个大幅主立绘；右栏3列×3行，依次为上排3格全身、中排3格表情头肩、下排3格局部细节。总共10格。","width":2000,"height":1400,"defaults":{"title":"未命名角色","subtitle":"角色设定集","style":"统一角色资产，纯白棚拍背景，柔和棚拍光","background":"#ffffff","accent":"#e08a9a"},"cells":[{"id":"hero","label":"主立绘","role":"hero","prompt":"单个人物正面完整全身主立绘，自然站姿，从头顶到鞋底完整入镜，画面里不能出现第二个人或拼贴。","x":0.03,"y":0.08,"w":0.3,"h":0.86,"mirror":false},{"id":"body_front","label":"正面全身","role":"turnaround","prompt":"正面完整全身站姿，从头顶到鞋底完整不裁切。","x":0.36,"y":0.08,"w":0.2,"h":0.4,"mirror":false},{"id":"body_side","label":"侧面全身","role":"turnaround","prompt":"严格90度左侧面完整全身，人物朝画面右侧，从头顶到鞋底完整不裁切。","x":0.58,"y":0.08,"w":0.2,"h":0.4,"mirror":false},{"id":"body_back","label":"背面全身","role":"turnaround","prompt":"严格180度背面完整全身，只能看到后脑和后背，从头顶到鞋底完整不裁切。","x":0.8,"y":0.08,"w":0.17,"h":0.4,"mirror":false},{"id":"ex_1","label":"甜美微笑","role":"expression","prompt":"头肩特写，张嘴露齿甜笑，眼睛弯起，表情明亮。","x":0.36,"y":0.52,"w":0.2,"h":0.2,"mirror":false},{"id":"ex_2","label":"低头沉思","role":"expression","prompt":"头肩特写，低头垂眼，不看镜头，表情安静克制。","x":0.58,"y":0.52,"w":0.2,"h":0.2,"mirror":false},{"id":"ex_3","label":"惊讶张嘴","role":"expression","prompt":"头肩特写，眼睛睁大、眉毛抬高、嘴巴张开，表情惊讶。","x":0.8,"y":0.52,"w":0.17,"h":0.2,"mirror":false},{"id":"de_1","label":"服装细节","role":"detail","prompt":"制服领口、徽章和衣料纹理的局部微距，不出现完整人物。","x":0.36,"y":0.75,"w":0.2,"h":0.2,"mirror":false},{"id":"de_2","label":"配饰细节","role":"detail","prompt":"领结或发饰的局部微距，不出现人物脸部。","x":0.58,"y":0.75,"w":0.2,"h":0.2,"mirror":false},{"id":"de_3","label":"鞋履细节","role":"detail","prompt":"鞋履结构和材质的局部微距，不出现完整人物。","x":0.8,"y":0.75,"w":0.17,"h":0.2,"mirror":false}]},
    {"id":"xianxia_ref","name":"十四格·全图鉴","description":"左侧四全身+三头像，右侧四表情+三细节，最后一行横条面料。","layout_prompt":"左右两栏：左栏上排4个全身，下排3个头像；右栏上排3个表情，中排3格（1个表情+2个细节），底部1个横条面料细节。总共14格，不能多出第4行。","width":2200,"height":1300,"defaults":{"title":"未命名角色","subtitle":"完整图鉴","style":"统一角色资产，纯白棚拍背景，柔和棚拍光，写实精致","background":"#ffffff","accent":"#7a9bd8"},"cells":[{"id":"body_front","label":"正面全身","role":"turnaround","prompt":"正面完整全身站姿，从头顶到鞋底完整不裁切，画面里只有一个人。","x":0.02,"y":0.03,"w":0.125,"h":0.42,"mirror":false},{"id":"body_right","label":"右侧面全身","role":"turnaround","prompt":"严格90度右侧面完整全身，人物朝画面左侧，只能看到右半边脸和右耳，从头顶到鞋底完整不裁切。","x":0.155,"y":0.03,"w":0.125,"h":0.42,"mirror":false},{"id":"body_back","label":"背面全身","role":"turnaround","prompt":"严格180度背面完整全身，只能看到后脑和后背，从头顶到鞋底完整不裁切。","x":0.29,"y":0.03,"w":0.125,"h":0.42,"mirror":false},{"id":"body_left","label":"左侧面全身","role":"turnaround","prompt":"严格90度左侧面完整全身，人物朝画面右侧，只能看到左半边脸和左耳，与右侧面方向相反。","x":0.425,"y":0.03,"w":0.125,"h":0.42,"mirror":false},{"id":"head_1","label":"正面头像","role":"portrait","prompt":"正面头肩肖像，头部到肩部完整入镜，平静正视镜头。","x":0.02,"y":0.47,"w":0.15,"h":0.43,"mirror":false},{"id":"head_2","label":"侧面头像","role":"portrait","prompt":"严格90度侧面头肩肖像，人物朝画面右侧，展示侧脸轮廓。","x":0.18,"y":0.47,"w":0.15,"h":0.43,"mirror":false},{"id":"head_3","label":"斜侧头像","role":"portrait","prompt":"四分之三斜侧头肩肖像，脸朝画面右前方，眼神看向镜头。","x":0.34,"y":0.47,"w":0.15,"h":0.43,"mirror":false},{"id":"ex_1","label":"温柔微笑","role":"expression","prompt":"头肩特写，闭唇温柔微笑，嘴角微扬，眼神柔和。","x":0.58,"y":0.03,"w":0.12,"h":0.25,"mirror":false},{"id":"ex_2","label":"惊讶张嘴","role":"expression","prompt":"头肩特写，眼睛圆睁、眉毛抬起、嘴巴微张，表情惊讶。","x":0.71,"y":0.03,"w":0.12,"h":0.25,"mirror":false},{"id":"ex_3","label":"闭眼沉思","role":"expression","prompt":"头肩特写，双眼闭合，头部微低，嘴唇轻抿，表情安静。","x":0.84,"y":0.03,"w":0.12,"h":0.25,"mirror":false},{"id":"ex_4","label":"蹙眉清冷","role":"expression","prompt":"头肩特写，眉头微蹙，眼神冷峻直视，和微笑表情明显不同。","x":0.58,"y":0.3,"w":0.12,"h":0.25,"mirror":false},{"id":"de_1","label":"眼部细节","role":"detail","prompt":"单只眼睛的微距特写，展示瞳色、虹膜纹理和睫毛，不出现整张脸。","x":0.71,"y":0.3,"w":0.12,"h":0.25,"mirror":false},{"id":"de_2","label":"配饰细节","role":"detail","prompt":"项链、耳环或发饰的微距特写，不出现人物脸部。","x":0.84,"y":0.3,"w":0.12,"h":0.25,"mirror":false},{"id":"de_3","label":"面料细节","role":"detail","prompt":"横向服饰面料与刺绣微距，只展示布料纹理、褶皱和图案，不出现人物。","x":0.58,"y":0.57,"w":0.38,"h":0.37,"mirror":false}]},
    {"id":"scene_six_view","kind":"scene","name":"场景·六面图","description":"上传任意一张场景图，生成正面参考、左向、右向、反向、俯视和环境细节共六个视图。","layout_prompt":"等分2排×3列：上排依次为正面参考、左向视角、右向视角；下排依次为反向视角、俯视视角、环境细节。总共6格。","width":1920,"height":1280,"defaults":{"title":"未命名场景","subtitle":"场景多视角设定","style":"写实场景概念设计，统一空间结构、材质、透视和光照","background":"#ffffff","accent":"#4f8a8b"},"cells":[{"id":"scene_front","label":"正面参考","role":"scene_anchor","prompt":"保留上传的场景图作为唯一空间锚点，不重绘、不改变构图；若没有上传参考图，则生成一张场景正面主视图。场景为主，不新增人物或动物。","x":0.03,"y":0.03,"w":0.303,"h":0.45,"mirror":false},{"id":"scene_left","label":"左向视角","role":"scene_view","prompt":"从正面相机位置向左转约90度，展示同一场景的左侧区域；延续地形、建筑、道路、植被、主要物件、材质和光照。场景为主，不新增人物或动物。","x":0.345,"y":0.03,"w":0.303,"h":0.45,"mirror":false},{"id":"scene_right","label":"右向视角","role":"scene_view","prompt":"从正面相机位置向右转约90度，展示同一场景的右侧区域；延续地形、建筑、道路、植被、主要物件、材质和光照。场景为主，不新增人物或动物。","x":0.66,"y":0.03,"w":0.303,"h":0.45,"mirror":false},{"id":"scene_back","label":"反向视角","role":"scene_view","prompt":"从正面相机位置转身约180度，展示相机背后的反方向场景；保持同一空间的结构、尺度、主要物件位置和光照方向。场景为主，不新增人物或动物。","x":0.03,"y":0.52,"w":0.303,"h":0.45,"mirror":false},{"id":"scene_top","label":"俯视视角","role":"scene_view","prompt":"升高相机并向下俯拍，展示同一场景的地形、建筑、道路、植被或主要物件的位置关系；保持空间布局连续。场景为主，不新增人物或动物。","x":0.345,"y":0.52,"w":0.303,"h":0.45,"mirror":false},{"id":"scene_detail","label":"环境细节","role":"scene_detail","prompt":"提取该场景中最有辨识度的材质、纹理、植被、建筑构件或装饰细节，做一张局部微距；颜色和材质必须与环境一致。场景为主，不新增人物或动物。","x":0.66,"y":0.52,"w":0.303,"h":0.45,"mirror":false}]}
];

const PAYLOAD_FALLBACK = {
    version: 3,
    templates: FALLBACK_TEMPLATES,
    defaultNegative: "低质量，模糊，畸形，多余肢体，错误手指，身份漂移，脸部崩坏，性别漂移，服装结构错误，配饰缺失，面板布局混乱，重复人物，复制同一张脸，画格数量错误，多出画格，缺少画格，画格合并，九宫格误生成，文字乱码，水印，logo，头部裁切，脚部裁切，鞋履裁切，半身替代全身，断脚，切头，灰色背景，深灰背景，暗背景，渐变背景，纹理背景，阴影背景",
};

let payloadPromise = null;
let stylePromise = null;

function el(tag, className = "", text = "") {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text) node.textContent = text;
    return node;
}

function ensureStyle() {
    if (stylePromise) return stylePromise;
    stylePromise = new Promise((resolve) => {
        const existing = document.getElementById("ccs-character-card-style");
        if (existing) {
            resolve();
            return;
        }
        const link = document.createElement("link");
        link.id = "ccs-character-card-style";
        link.rel = "stylesheet";
        link.href = CSS_URL;
        link.addEventListener("load", resolve, { once: true });
        link.addEventListener("error", resolve, { once: true });
        document.head.append(link);
    });
    return stylePromise;
}

function loadPayload() {
    if (payloadPromise) return payloadPromise;
    payloadPromise = (async () => {
        try {
            const response = await api.fetchApi("/aicg3d/character-card/templates");
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const data = await response.json();
            if (!Array.isArray(data?.templates) || !data.templates.length) throw new Error("empty templates");
            return {
                version: data.version || 1,
                templates: data.templates,
                defaultNegative: String(data.defaultNegative || PAYLOAD_FALLBACK.defaultNegative),
            };
        } catch (error) {
            console.warn("[CharacterCardStudio] Using bundled templates:", error);
            return PAYLOAD_FALLBACK;
        }
    })();
    return payloadPromise;
}

function widgetOf(node, name) {
    return node?.widgets?.find((widget) => widget?.name === name);
}

function setWidgetValue(node, name, value) {
    const widget = widgetOf(node, name);
    if (!widget) return false;
    if (widget.value !== value) widget.value = value;
    return true;
}

function markWidgetHidden(widget) {
    if (!widget) return;
    if (!widget.__ccsNative) {
        widget.__ccsNative = {
            type: widget.type,
            hidden: widget.hidden,
            computeSize: widget.computeSize,
            optionsHidden: widget.options?.hidden,
            optionsCanvasOnly: widget.options?.canvasOnly,
        };
    }
    widget.options = widget.options || {};
    widget.options.hidden = true;
    widget.options.canvasOnly = true;
    if (widget._state?.options) {
        widget._state.options.hidden = true;
        widget._state.options.canvasOnly = true;
    }
    widget.hidden = true;
    widget.type = "hidden";
    widget.computeSize = () => [0, -4];
}

function autoHideWidgets(nodeType, names) {
    const prototype = nodeType?.prototype;
    if (!prototype || prototype.__ccsAutoHide || typeof prototype.addWidget !== "function") return;
    const wanted = new Set(names);
    const original = prototype.addWidget;
    prototype.__ccsAutoHide = true;
    prototype.addWidget = function (...args) {
        const widget = original.apply(this, args);
        try {
            const name = widget?.name ?? (typeof args[1] === "string" ? args[1] : "");
            if (wanted.has(name)) markWidgetHidden(widget);
        } catch (error) {
            console.error("[CharacterCardStudio]", error);
        }
        return widget;
    };
}

function refreshVueWidgets(node) {
    if (!globalThis.LiteGraph?.vueNodesMode) return;
    const list = node?.widgets;
    if (!Array.isArray(list) || !list.length) return;
    try {
        node._widgets = [...list];
        node.setDirtyCanvas?.(true, true);
    } catch (error) {
        console.warn("[CharacterCardStudio] Widget refresh failed", error);
    }
}

function refreshNode(node) {
    node._widgetSlotsDirty = true;
    node.setDirtyCanvas?.(true, true);
    app.graph?.setDirtyCanvas?.(true, true);
}

function clone(value) {
    return JSON.parse(JSON.stringify(value));
}

function clampNumber(value, low, high, fallback) {
    const number = Number(value);
    return Number.isFinite(number) ? Math.max(low, Math.min(high, number)) : fallback;
}

function roundDimension(value) {
    const clamped = clampNumber(value, 512, 4096, 1024);
    return Math.round(clamped / 16) * 16;
}

function uid() {
    return `slot_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 7)}`;
}

function slotFromCell(cell, index) {
    return {
        id: uid(),
        cellId: cell.id,
        label: cell.label || `画格 ${index + 1}`,
        role: cell.role || "custom",
        prompt: cell.prompt || "",
        image: "",
        subfolder: "",
        fit: ["turnaround", "hero", "scene_anchor"].includes(cell.role) ? "contain" : "cover",
        zoom: 1,
        offsetX: 0,
        offsetY: 0,
        lockIdentity: true,
        enabled: true,
    };
}

function defaultState(template, payload, previous = null) {
    const defaults = template.defaults || {};
    const previousTemplate = payload.templates.find((item) => item.id === previous?.templateId);
    const kindChanged = Boolean(previousTemplate && previousTemplate.kind !== template.kind);
    const leavingScene = kindChanged && previousTemplate?.kind === "scene";
    const genericTitle = ["", "未命名角色", "未命名场景"].includes(previous?.title || "");
    const state = {
        version: 2,
        templateId: template.id,
        title: kindChanged && genericTitle ? (defaults.title || "未命名主体") : (previous?.title || defaults.title || "未命名主体"),
        subtitle: kindChanged ? (defaults.subtitle || template.name || "设定卡") : (previous?.subtitle || defaults.subtitle || template.name || "设定卡"),
        identity: kindChanged ? "" : (previous?.identity || ""),
        appearance: kindChanged ? "" : (previous?.appearance || ""),
        outfit: kindChanged ? "" : (previous?.outfit || ""),
        palette: leavingScene ? "" : (previous?.palette || ""),
        style: kindChanged ? (defaults.style || "") : (previous?.style || defaults.style || ""),
        negativePrompt: previous?.negativePrompt || payload.defaultNegative,
        background: previous?.background || defaults.background || "#ffffff",
        accent: previous?.accent || defaults.accent || "#d86b73",
        showLabels: previous?.showLabels ?? false,
        width: roundDimension(previous?.width || template.width || 1920),
        height: roundDimension(previous?.height || template.height || 1080),
        slots: template.cells.map((cell, index) => {
            const base = slotFromCell(cell, index);
            const old = previous?.slots?.find((slot) => slot?.cellId === cell.id);
            if (!old) return base;
            // 切模板时：标签和提示词永远用新模板的默认值，只保留图片和视觉微调
            return {
                ...base,
                id: old.id || base.id,
                image: old.image || "",
                subfolder: old.subfolder || "",
                fit: ["contain", "cover"].includes(old.fit) ? old.fit : base.fit,
                zoom: clampNumber(old.zoom, 0.5, 3, 1),
                offsetX: clampNumber(old.offsetX, -1, 1, 0),
                offsetY: clampNumber(old.offsetY, -1, 1, 0),
                lockIdentity: old.lockIdentity !== false,
                enabled: old.enabled !== false,
            };
        }),
        library: Array.isArray(previous?.library) ? clone(previous.library) : [],
    };
    return state;
}

function normaliseState(raw, payload, template) {
    const base = defaultState(template, payload);
    if (!raw || typeof raw !== "object") return base;
    const result = {
        ...base,
        version: 2,
        title: String(raw.title ?? base.title),
        subtitle: String(raw.subtitle ?? base.subtitle),
        identity: String(raw.identity ?? ""),
        appearance: String(raw.appearance ?? ""),
        outfit: String(raw.outfit ?? ""),
        palette: String(raw.palette ?? ""),
        style: String(raw.style ?? base.style),
        negativePrompt: String(raw.negativePrompt ?? payload.defaultNegative),
        background: String(raw.background ?? base.background),
        accent: String(raw.accent ?? base.accent),
        showLabels: Boolean(raw.showLabels),
        width: roundDimension(raw.width ?? base.width),
        height: roundDimension(raw.height ?? base.height),
    };
    const slots = Array.isArray(raw.slots) ? raw.slots : [];
    result.slots = template.cells.map((cell, index) => {
        const indexed = slots[index] && typeof slots[index] === "object" ? slots[index] : {};
        const source = slots.find((item) => item && typeof item === "object" && item.cellId === cell.id)
            || (!indexed.cellId ? indexed : {});
        return {
            ...slotFromCell(cell, index),
            id: String(source.id || uid()),
            image: String(source.image || ""),
            subfolder: String(source.subfolder || ""),
            fit: source.fit === "contain" || (source.fit == null && ["turnaround", "hero", "scene_anchor"].includes(cell.role)) ? "contain" : "cover",
            zoom: clampNumber(source.zoom, 0.5, 3, 1),
            offsetX: clampNumber(source.offsetX, -1, 1, 0),
            offsetY: clampNumber(source.offsetY, -1, 1, 0),
            lockIdentity: source.lockIdentity !== false,
            enabled: source.enabled !== false,
        };
    });
    const seen = new Set();
    result.library = [];
    for (const item of Array.isArray(raw.library) ? raw.library : []) {
        if (!item || typeof item !== "object") continue;
        const image = String(item.image || item.name || "");
        const subfolder = String(item.subfolder || "");
        const key = `${subfolder}\u0000${image}`;
        if (!image || seen.has(key)) continue;
        seen.add(key);
        result.library.push({
            image,
            subfolder,
            name: String(item.name || image.split("/").pop() || image),
            useForIdentity: item.useForIdentity !== false,
        });
    }
    for (const slot of result.slots) {
        if (!slot.image) continue;
        const key = `${slot.subfolder}\u0000${slot.image}`;
        if (seen.has(key)) continue;
        seen.add(key);
        result.library.push({
            image: slot.image,
            subfolder: slot.subfolder,
            name: slot.image.split("/").pop() || slot.image,
            useForIdentity: true,
        });
    }
    return result;
}

function stateFromWidget(node, payload) {
    const widget = widgetOf(node, STATE_WIDGET);
    const rawText = String(widget?.value || "{}");
    let raw = {};
    try {
        raw = JSON.parse(rawText);
    } catch (error) {
        raw = {};
    }
    const templateId = String(raw?.templateId || raw?.template_id || payload.templates[0].id);
    const template = payload.templates.find((item) => item.id === templateId) || payload.templates[0];
    return normaliseState(raw, payload, template);
}

function queueStateSync(node, state) {
    const text = JSON.stringify(state);
    const widget = widgetOf(node, STATE_WIDGET);
    if (widget) widget.value = text;
    setWidgetValue(node, WIDTH_WIDGET, state.width);
    setWidgetValue(node, HEIGHT_WIDGET, state.height);
    clearTimeout(node.__ccsSyncTimer);
    node.__ccsSyncTimer = setTimeout(() => {
        refreshNode(node);
    }, 40);
}

function imageUrl(item) {
    if (!item?.image) return "";
    const params = new URLSearchParams({
        filename: item.image,
        type: "input",
        preview: "webp",
    });
    if (item.subfolder) params.set("subfolder", item.subfolder);
    const path = `/view?${params.toString()}`;
    try {
        return api.apiURL ? api.apiURL(path) : path;
    } catch (error) {
        return path;
    }
}

function imageItem(slot) {
    return { image: slot?.image || "", subfolder: slot?.subfolder || "" };
}

function templateFor(state, payload) {
    return payload.templates.find((item) => item.id === state.templateId) || payload.templates[0];
}

function formatDimensions(state) {
    return `${state.width} × ${state.height}`;
}

function makeField(label, control, top = false) {
    const row = el("div", `ccs-form-row${top ? " is-top" : ""}`);
    row.append(el("label", "", label), control);
    return row;
}

function makeSwitch(isOn, onChange, title = "") {
    const button = el("button", `ccs-switch${isOn ? " is-on" : ""}`);
    button.type = "button";
    if (title) button.title = title;
    button.addEventListener("click", () => {
        const next = !button.classList.contains("is-on");
        button.classList.toggle("is-on", next);
        onChange(next);
    });
    return button;
}

function makeTextarea(rows = 4) {
    const area = el("textarea", "ccs-textarea");
    area.rows = rows;
    area.spellcheck = false;
    return area;
}

function makeColorField(value, onChange, label = "") {
    const wrap = el("div", "ccs-color-field");
    if (label) wrap.append(el("div", "ccs-color-label", label));
    const picker = document.createElement("input");
    picker.type = "color";
    picker.value = /^#[0-9a-f]{6}$/i.test(value) ? value : "#d86b73";
    const text = el("input", "ccs-input");
    text.value = value || picker.value;
    picker.addEventListener("input", () => {
        text.value = picker.value;
        onChange(picker.value);
    });
    text.addEventListener("change", () => {
        const next = /^#[0-9a-f]{6}$/i.test(text.value) ? text.value : picker.value;
        text.value = next;
        picker.value = next;
        onChange(next);
    });
    wrap.append(picker, text);
    return wrap;
}

function buildTemplateMini(template) {
    const mini = el("div", "ccs-template-mini");
    mini.style.aspectRatio = `${template.width || 16} / ${template.height || 10}`;
    for (const cell of template.cells || []) {
        const block = el("span");
        block.style.left = `${cell.x * 100}%`;
        block.style.top = `${cell.y * 100}%`;
        block.style.width = `${cell.w * 100}%`;
        block.style.height = `${cell.h * 100}%`;
        block.style.background = cell.role === "hero" ? "#949ba5" : "#b1b7bf";
        mini.append(block);
    }
    return mini;
}

function buildUi(node, payload, state) {
    const root = el("div", "ccs-root");
    root.addEventListener("pointerdown", (event) => event.stopPropagation());
    root.addEventListener("wheel", (event) => event.stopPropagation(), { passive: true });

    const ui = {
        node,
        payload,
        state,
        root,
        selectedIndex: 0,
        activeTab: "cell",
        updating: false,
        toastTimer: null,
        boardObserver: null,
    };

    const topbar = el("div", "ccs-topbar");
    const brand = el("div", "ccs-brand");
    brand.append(el("div", "ccs-mark", "CC"));
    const brandCopy = el("div", "ccs-brand-copy");
    brandCopy.append(el("div", "ccs-brand-title", "角色卡工作台"), el("div", "ccs-brand-sub", "Qwen Image 2.1"));
    brand.append(brandCopy);

    const toolbar = el("div", "ccs-toolbar");
    const templateField = el("label", "ccs-field-inline");
    templateField.append(el("span", "ccs-field-label", "卡版"));
    const templateSelect = el("select", "ccs-select");
    templateSelect.style.minWidth = "154px";
    for (const template of payload.templates) {
        const option = document.createElement("option");
        option.value = template.id;
        option.textContent = template.name;
        templateSelect.append(option);
    }
    templateField.append(templateSelect);
    toolbar.append(templateField);

    const dimensions = el("div", "ccs-dimension", formatDimensions(state));
    toolbar.append(dimensions);
    toolbar.append(el("div", "ccs-toolbar-spacer"));

    const uploadButton = el("button", "ccs-btn ccs-btn--accent", "上传素材");
    uploadButton.type = "button";
    const copyButton = el("button", "ccs-btn", "复制 JSON");
    copyButton.type = "button";
    toolbar.append(uploadButton, copyButton);
    topbar.append(brand, toolbar);

    const body = el("div", "ccs-body");
    const stage = el("section", "ccs-stage");
    const stageHead = el("div", "ccs-stage-head");
    const stageTitle = el("div", "ccs-stage-title", "版式预览");
    const stageMeta = el("div", "ccs-stage-meta");
    const stageSpacer = el("div", "ccs-stage-spacer");
    const restoreButton = el("button", "ccs-btn ccs-btn--small", "一键恢复");
    restoreButton.type = "button";
    restoreButton.title = "重新启用所有画格";
    const fillEmptyButton = el("button", "ccs-btn ccs-btn--small", "顺序填充");
    fillEmptyButton.type = "button";
    stageHead.append(stageTitle, stageMeta, stageSpacer, restoreButton, fillEmptyButton);

    const boardWrap = el("div", "ccs-board-wrap");
    const board = el("div", "ccs-board");
    boardWrap.append(board);

    const templateStrip = el("div", "ccs-template-strip");
    stage.append(stageHead, boardWrap, templateStrip);

    const sidebar = el("aside", "ccs-sidebar");
    const tabs = el("div", "ccs-tabs");
    const cellTab = el("button", "ccs-tab is-active", "当前画格");
    const globalTab = el("button", "ccs-tab", "角色与输出");
    cellTab.type = "button";
    globalTab.type = "button";
    tabs.append(cellTab, globalTab);

    const cellPane = el("div", "ccs-pane");
    const globalPane = el("div", "ccs-pane");
    globalPane.hidden = true;
    sidebar.append(tabs, cellPane, globalPane);

    const library = el("div", "ccs-library");
    const libraryHead = el("div", "ccs-library-head");
    const libraryTitle = el("div", "ccs-library-title", "素材库");
    const libraryMeta = el("div", "ccs-library-meta", "0 张");
    const libraryUpload = el("button", "ccs-btn ccs-btn--small", "添加图片");
    libraryUpload.type = "button";
    libraryHead.append(libraryTitle, libraryMeta, libraryUpload);
    const libraryList = el("div", "ccs-library-list");
    library.append(libraryHead, libraryList);

    body.append(stage, sidebar);
    root.append(topbar, body, library);

    const fileInput = document.createElement("input");
    fileInput.type = "file";
    fileInput.accept = "image/*";
    fileInput.multiple = true;
    fileInput.className = "ccs-hidden-input";
    root.append(fileInput);

    const toast = el("div", "ccs-toast");
    root.append(toast);

    Object.assign(ui, {
        templateSelect,
        dimensions,
        uploadButton,
        copyButton,
        stageMeta,
        fillEmptyButton,
        restoreButton,
        boardWrap,
        board,
        templateStrip,
        cellTab,
        globalTab,
        cellPane,
        globalPane,
        libraryMeta,
        libraryUpload,
        libraryList,
        fileInput,
        toast,
    });

    ui.showToast = (message, isError = false) => {
        toast.textContent = message;
        toast.classList.toggle("is-error", Boolean(isError));
        toast.classList.add("is-visible");
        clearTimeout(ui.toastTimer);
        ui.toastTimer = setTimeout(() => toast.classList.remove("is-visible"), 2200);
    };

    buildCellPane(ui);
    buildGlobalPane(ui);

    templateSelect.addEventListener("change", () => {
        switchTemplate(ui, templateSelect.value);
    });
    uploadButton.addEventListener("click", () => openFilePicker(ui, null));
    libraryUpload.addEventListener("click", () => openFilePicker(ui, null));
    fileInput.addEventListener("change", async () => {
        const files = [...(fileInput.files || [])];
        fileInput.value = "";
        if (!files.length) return;
        const target = Number.isInteger(Number(fileInput.dataset.slotIndex))
            ? Number(fileInput.dataset.slotIndex)
            : null;
        await uploadFiles(ui, files, target);
    });
    cellTab.addEventListener("click", () => setActiveTab(ui, "cell"));
    globalTab.addEventListener("click", () => setActiveTab(ui, "global"));
    copyButton.addEventListener("click", () => copyState(ui));
    fillEmptyButton.addEventListener("click", () => fillEmptySlots(ui));
    restoreButton.addEventListener("click", () => {
        let count = 0;
        for (const slot of ui.state.slots) {
            if (slot.enabled === false) {
                slot.enabled = true;
                count++;
            }
        }
        commitUi(ui, { board: true, inspector: true, sync: true });
        ui.showToast(count ? `已恢复 ${count} 个画格` : "所有画格已启用");
    });

    ui.renderAll = () => {
        renderTemplateStrip(ui);
        renderBoard(ui);
        renderLibrary(ui);
        syncInspector(ui);
        syncHeader(ui);
    };
    ui.renderAll();
    bindBoardResize(ui);
    return ui;
}

function setActiveTab(ui, tab) {
    ui.activeTab = tab;
    ui.cellTab.classList.toggle("is-active", tab === "cell");
    ui.globalTab.classList.toggle("is-active", tab === "global");
    ui.cellPane.hidden = tab !== "cell";
    ui.globalPane.hidden = tab !== "global";
}

function buildCellPane(ui) {
    const pane = ui.cellPane;
    const state = ui.state;

    const mediaSection = el("div", "ccs-section");
    mediaSection.append(el("div", "ccs-section-label", "参考图"));
    const preview = el("div", "ccs-media-preview");
    const previewImage = el("img");
    previewImage.alt = "";
    const previewEmpty = el("div", "ccs-media-empty", "未选择图片");
    preview.append(previewImage, previewEmpty);
    const mediaActions = el("div", "ccs-media-actions");
    const replaceButton = el("button", "ccs-btn ccs-btn--small", "选择图片");
    const clearButton = el("button", "ccs-btn ccs-btn--icon", "×");
    const lockButton = el("button", "ccs-btn ccs-btn--icon", "ID");
    replaceButton.type = "button";
    clearButton.type = "button";
    lockButton.type = "button";
    clearButton.title = "清除当前画格图片";
    lockButton.title = "是否加入身份参考拼图";
    mediaActions.append(replaceButton, clearButton, lockButton);
    mediaSection.append(preview, mediaActions);

    const contentSection = el("div", "ccs-section");
    contentSection.append(el("div", "ccs-section-label", "画格设置"));
    const labelInput = el("input", "ccs-input");
    const roleSelect = el("select", "ccs-select");
    for (const [value, label] of [
        ["hero", "主视觉"],
        ["turnaround", "转面 / 全身"],
        ["portrait", "头像"],
        ["expression", "表情"],
        ["detail", "细节"],
        ["scene_anchor", "场景正面"],
        ["scene_view", "场景视角"],
        ["scene_detail", "场景材质"],
        ["custom", "自定义"],
    ]) {
        const option = document.createElement("option");
        option.value = value;
        option.textContent = label;
        roleSelect.append(option);
    }
    const promptArea = makeTextarea(5);
    const fitSelect = el("select", "ccs-select");
    for (const [value, label] of [["cover", "填满裁切"], ["contain", "完整显示"]]) {
        const option = document.createElement("option");
        option.value = value;
        option.textContent = label;
        fitSelect.append(option);
    }
    contentSection.append(
        makeField("名称", labelInput),
        makeField("类型", roleSelect),
        makeField("镜头描述", promptArea, true),
        makeField("图片适配", fitSelect),
    );

    const cropSection = el("div", "ccs-section");
    cropSection.append(el("div", "ccs-section-label is-teal", "构图微调"));
    const zoom = buildRange(0.5, 3, 0.05);
    const offsetX = buildRange(-1, 1, 0.01);
    const offsetY = buildRange(-1, 1, 0.01);
    cropSection.append(
        makeField("缩放", zoom.wrap),
        makeField("横向", offsetX.wrap),
        makeField("纵向", offsetY.wrap),
    );

    const moveSection = el("div", "ccs-section");
    moveSection.append(el("div", "ccs-section-label", "顺序"));
    const moveGrid = el("div", "ccs-action-grid");
    const leftButton = el("button", "ccs-btn ccs-btn--small", "左移");
    const rightButton = el("button", "ccs-btn ccs-btn--small", "右移");
    const copyImageButton = el("button", "ccs-btn ccs-btn--small", "复制图片引用");
    const clearAllButton = el("button", "ccs-btn ccs-btn--small ccs-btn--danger", "清空画格");
    leftButton.type = "button";
    rightButton.type = "button";
    copyImageButton.type = "button";
    clearAllButton.type = "button";
    moveGrid.append(leftButton, rightButton, copyImageButton, clearAllButton);
    moveSection.append(moveGrid);

    pane.append(mediaSection, contentSection, cropSection, moveSection);


    Object.assign(ui, {
        previewImage,
        previewEmpty,
        replaceButton,
        clearButton,
        lockButton,
        labelInput,
        roleSelect,
        promptArea,
        fitSelect,
        zoomRange: zoom.input,
        zoomValue: zoom.value,
        offsetXRange: offsetX.input,
        offsetXValue: offsetX.value,
        offsetYRange: offsetY.input,
        offsetYValue: offsetY.value,
        leftButton,
        rightButton,
        copyImageButton,
        clearAllButton,
    });

    replaceButton.addEventListener("click", () => openFilePicker(ui, ui.selectedIndex));
    clearButton.addEventListener("click", () => updateSelectedSlot(ui, (slot) => {
        slot.image = "";
        slot.subfolder = "";
    }, true));
    clearAllButton.addEventListener("click", () => updateSelectedSlot(ui, (slot) => {
        slot.image = "";
        slot.subfolder = "";
        slot.prompt = "";
    }, true));
    lockButton.addEventListener("click", () => updateSelectedSlot(ui, (slot) => {
        slot.lockIdentity = !slot.lockIdentity;
    }, true));
    labelInput.addEventListener("input", () => updateSelectedSlot(ui, (slot) => {
        slot.label = labelInput.value;
    }, false));
    roleSelect.addEventListener("change", () => updateSelectedSlot(ui, (slot) => {
        slot.role = roleSelect.value;
    }, false));
    promptArea.addEventListener("input", () => updateSelectedSlot(ui, (slot) => {
        slot.prompt = promptArea.value;
    }, false));
    fitSelect.addEventListener("change", () => updateSelectedSlot(ui, (slot) => {
        slot.fit = fitSelect.value;
    }, false));
    zoom.input.addEventListener("input", () => updateSelectedSlot(ui, (slot) => {
        slot.zoom = Number(zoom.input.value);
    }, false));
    offsetX.input.addEventListener("input", () => updateSelectedSlot(ui, (slot) => {
        slot.offsetX = Number(offsetX.input.value);
    }, false));
    offsetY.input.addEventListener("input", () => updateSelectedSlot(ui, (slot) => {
        slot.offsetY = Number(offsetY.input.value);
    }, false));
    leftButton.addEventListener("click", () => moveSelected(ui, -1));
    rightButton.addEventListener("click", () => moveSelected(ui, 1));
    copyImageButton.addEventListener("click", () => {
        const slot = selectedSlot(ui);
        if (!slot?.image) {
            ui.showToast("当前画格没有图片", true);
            return;
        }
        const target = ui.state.slots.find((item) => !item.image);
        if (!target) {
            ui.showToast("没有空闲画格", true);
            return;
        }
        target.image = slot.image;
        target.subfolder = slot.subfolder;
        target.fit = slot.fit;
        target.zoom = slot.zoom;
        target.offsetX = slot.offsetX;
        target.offsetY = slot.offsetY;
        commitUi(ui, { board: true, inspector: true, library: true });
        ui.showToast("已复制到下一个空画格");
    });
}

function buildRange(min, max, step) {
    const wrap = el("div", "ccs-range-row");
    const input = document.createElement("input");
    input.type = "range";
    input.className = "ccs-range";
    input.min = String(min);
    input.max = String(max);
    input.step = String(step);
    input.value = String(min <= 0 && max >= 0 ? 0 : (min + max) / 2);
    const value = el("div", "ccs-range-value");
    const sync = () => {
        value.textContent = Number(input.value).toFixed(step < 0.1 ? 2 : 1);
    };
    input.addEventListener("input", sync);
    wrap.append(input, value);
    sync();
    return { wrap, input, value };
}

function appendGlobalText(ui, parent, label, key, rows = 4) {
    const area = makeTextarea(rows);
    area.addEventListener("input", () => {
        ui.state[key] = area.value;
        queueStateSync(ui.node, ui.state);
    });
    parent.append(makeField(label, area, true));
    return area;
}

function buildGlobalPane(ui) {
    const pane = ui.globalPane;
    const state = ui.state;

    const identitySection = el("div", "ccs-section");
    identitySection.append(el("div", "ccs-section-label", "角色设定"));
    const titleInput = el("input", "ccs-input");
    const subtitleInput = el("input", "ccs-input");
    titleInput.addEventListener("input", () => {
        ui.state.title = titleInput.value;
        commitUi(ui, { board: true, sync: true });
    });
    subtitleInput.addEventListener("input", () => {
        ui.state.subtitle = subtitleInput.value;
        commitUi(ui, { board: true, sync: true });
    });
    identitySection.append(
        makeField("名称", titleInput),
        makeField("副标题", subtitleInput),
    );
    const identity = appendGlobalText(ui, identitySection, "身份 / 场景类型", "identity", 3);
    const appearance = appendGlobalText(ui, identitySection, "外貌 / 场景结构", "appearance", 4);
    const outfit = appendGlobalText(ui, identitySection, "服装 / 环境材质", "outfit", 4);
    const palette = appendGlobalText(ui, identitySection, "固定色板", "palette", 2);

    const styleSection = el("div", "ccs-section");
    styleSection.append(el("div", "ccs-section-label is-teal", "输出风格"));
    const style = appendGlobalText(ui, styleSection, "统一风格", "style", 3);
    const negative = appendGlobalText(ui, styleSection, "负面提示词", "negativePrompt", 3);

    const layoutSection = el("div", "ccs-section");
    layoutSection.append(el("div", "ccs-section-label", "版式"));
    const widthInput = el("input", "ccs-input");
    const heightInput = el("input", "ccs-input");
    widthInput.type = "number";
    heightInput.type = "number";
    widthInput.min = "512";
    widthInput.max = "4096";
    heightInput.min = "512";
    heightInput.max = "4096";
    widthInput.step = "16";
    heightInput.step = "16";
    const dimensionWrap = el("div", "ccs-color-row");
    const swapBtn = el("button", "ccs-swap-btn", "⇄");
    swapBtn.type = "button";
    swapBtn.title = "交换宽高（横竖屏切换）";
    swapBtn.addEventListener("click", () => {
        const w = ui.state.width;
        ui.state.width = ui.state.height;
        ui.state.height = w;
        widthInput.value = String(ui.state.width);
        heightInput.value = String(ui.state.height);
        commitUi(ui, { board: true, sync: true, header: true, inspector: true });
    });
    dimensionWrap.append(widthInput, swapBtn, heightInput);
    const writeDimension = () => {
        ui.state.width = roundDimension(widthInput.value);
        ui.state.height = roundDimension(heightInput.value);
        widthInput.value = String(ui.state.width);
        heightInput.value = String(ui.state.height);
        commitUi(ui, { board: true, sync: true, header: true });
    };
    widthInput.addEventListener("change", writeDimension);
    heightInput.addEventListener("change", writeDimension);
    const colorRow = el("div", "ccs-color-row");
    colorRow.append(
        makeColorField(state.background, (value) => {
            ui.state.background = value;
            commitUi(ui, { board: true, sync: true, inspector: true });
        }, "背景"),
        makeColorField(state.accent, (value) => {
            ui.state.accent = value;
            commitUi(ui, { board: true, sync: true, inspector: true });
        }, "强调色"),
    );
    const labelSwitch = makeSwitch(Boolean(state.showLabels), (next) => {
        ui.state.showLabels = next;
        commitUi(ui, { board: true, sync: true });
    }, "输出画面中是否生成中文标签");
    const labelRow = el("div", "ccs-check-row");
    labelRow.append(el("span", "", "生成画格标签"), labelSwitch);
    layoutSection.append(makeField("画布尺寸", dimensionWrap), makeField("背景 / 强调色", colorRow), labelRow);

    const actionSection = el("div", "ccs-section");
    actionSection.append(el("div", "ccs-section-label", "操作"));
    const actions = el("div", "ccs-action-grid");
    const resetButton = el("button", "ccs-btn ccs-btn--small", "重置卡版内容");
    const selectAllIdentity = el("button", "ccs-btn ccs-btn--small", "全部加入身份参考");
    const copyButton = el("button", "ccs-btn ccs-btn--small", "复制卡版 JSON");
    const clearLibraryButton = el("button", "ccs-btn ccs-btn--small ccs-btn--danger", "清空素材库");
    resetButton.type = "button";
    selectAllIdentity.type = "button";
    copyButton.type = "button";
    clearLibraryButton.type = "button";
    actions.append(resetButton, selectAllIdentity, copyButton, clearLibraryButton);
    actionSection.append(actions);

    pane.append(identitySection, styleSection, layoutSection, actionSection);

    Object.assign(ui, {
        titleInput,
        subtitleInput,
        identityArea: identity,
        appearanceArea: appearance,
        outfitArea: outfit,
        paletteArea: palette,
        styleArea: style,
        negativeArea: negative,
        widthInput,
        heightInput,
        labelSwitch,
    });

    resetButton.addEventListener("click", () => {
        const template = templateFor(ui.state, ui.payload);
        const library = clone(ui.state.library);
        ui.state = defaultState(template, ui.payload);
        ui.state.library = library;
        ui.selectedIndex = 0;
        commitUi(ui, { board: true, inspector: true, library: true, header: true, sync: true });
        ui.showToast("已重置卡版内容");
    });
    selectAllIdentity.addEventListener("click", () => {
        for (const item of ui.state.library) item.useForIdentity = true;
        for (const slot of ui.state.slots) slot.lockIdentity = true;
        queueStateSync(ui.node, ui.state);
        ui.showToast("主体参考已全选");
    });
    copyButton.addEventListener("click", () => copyState(ui));
    clearLibraryButton.addEventListener("click", () => {
        ui.state.library = [];
        queueStateSync(ui.node, ui.state);
        renderLibrary(ui);
        ui.showToast("素材库已清空");
    });
}

function selectedSlot(ui) {
    return ui.state.slots[ui.selectedIndex] || null;
}

function updateSelectedSlot(ui, updater, rerenderInspector) {
    const slot = selectedSlot(ui);
    if (!slot) return;
    updater(slot);
    commitUi(ui, { board: true, inspector: rerenderInspector, library: rerenderInspector });
}

function moveSelected(ui, direction) {
    const from = ui.selectedIndex;
    const to = from + direction;
    if (to < 0 || to >= ui.state.slots.length) return;
    moveSlot(ui, from, to);
}

function moveSlot(ui, from, to) {
    if (from === to) return;
    const [slot] = ui.state.slots.splice(from, 1);
    ui.state.slots.splice(to, 0, slot);
    ui.selectedIndex = to;
    commitUi(ui, { board: true, inspector: true, library: true, sync: true });
}

function assignImage(ui, imageIndex, targetIndex) {
    const item = ui.state.library[imageIndex];
    const slot = ui.state.slots[targetIndex];
    if (!item || !slot) return;
    slot.image = item.image;
    slot.subfolder = item.subfolder || "";
    ui.selectedIndex = targetIndex;
    setActiveTab(ui, "cell");
    commitUi(ui, { board: true, inspector: true, library: true, sync: true });
}

function commitUi(ui, options = {}) {
    if (options.board) renderBoard(ui);
    if (options.inspector) syncInspector(ui);
    if (options.library) renderLibrary(ui);
    if (options.header) { syncHeader(ui); renderTemplateStrip(ui); }
    if (options.sync !== false) queueStateSync(ui.node, ui.state);
    syncCellForm(ui);
}

function syncHeader(ui) {
    ui.templateSelect.value = ui.state.templateId;
    ui.dimensions.textContent = formatDimensions(ui.state);
    ui.stageMeta.textContent = `${templateFor(ui.state, ui.payload).name} · ${ui.state.slots.length} 格`;
    ui.widthInput.value = String(ui.state.width);
    ui.heightInput.value = String(ui.state.height);
    ui.root.classList.toggle("show-labels", Boolean(ui.state.showLabels));
    ui.board.style.setProperty("--ccs-board-accent", ui.state.accent);
}

function syncInspector(ui) {
    syncCellForm(ui);
    syncGlobalForm(ui);
}

function syncCellForm(ui) {
    const slot = selectedSlot(ui);
    ui.updating = true;
    if (!slot) {
        ui.updating = false;
        return;
    }
    const url = imageUrl(slot);
    if (url) {
        ui.previewImage.src = url;
        ui.previewImage.style.display = "block";
        ui.previewEmpty.style.display = "none";
    } else {
        ui.previewImage.removeAttribute("src");
        ui.previewImage.style.display = "none";
        ui.previewEmpty.style.display = "grid";
    }
    if (document.activeElement !== ui.labelInput) ui.labelInput.value = slot.label || "";
    if (document.activeElement !== ui.promptArea) ui.promptArea.value = slot.prompt || "";
    ui.roleSelect.value = slot.role || "custom";
    ui.fitSelect.value = slot.fit || "cover";
    ui.zoomRange.value = String(slot.zoom ?? 1);
    ui.zoomValue.textContent = Number(slot.zoom ?? 1).toFixed(2);
    ui.offsetXRange.value = String(slot.offsetX ?? 0);
    ui.offsetXValue.textContent = Number(slot.offsetX ?? 0).toFixed(2);
    ui.offsetYRange.value = String(slot.offsetY ?? 0);
    ui.offsetYValue.textContent = Number(slot.offsetY ?? 0).toFixed(2);
    ui.lockButton.title = slot.lockIdentity ? "已加入身份参考，点击关闭" : "未加入身份参考，点击开启";
    ui.lockButton.classList.toggle("ccs-btn--accent", Boolean(slot.lockIdentity));
    ui.leftButton.disabled = ui.selectedIndex <= 0;
    ui.rightButton.disabled = ui.selectedIndex >= ui.state.slots.length - 1;
    ui.updating = false;
}

function syncGlobalForm(ui) {
    const state = ui.state;
    ui.updating = true;
    if (document.activeElement !== ui.titleInput) ui.titleInput.value = state.title || "";
    if (document.activeElement !== ui.subtitleInput) ui.subtitleInput.value = state.subtitle || "";
    if (document.activeElement !== ui.identityArea) ui.identityArea.value = state.identity || "";
    if (document.activeElement !== ui.appearanceArea) ui.appearanceArea.value = state.appearance || "";
    if (document.activeElement !== ui.outfitArea) ui.outfitArea.value = state.outfit || "";
    if (document.activeElement !== ui.paletteArea) ui.paletteArea.value = state.palette || "";
    if (document.activeElement !== ui.styleArea) ui.styleArea.value = state.style || "";
    if (document.activeElement !== ui.negativeArea) ui.negativeArea.value = state.negativePrompt || "";
    if (document.activeElement !== ui.widthInput) ui.widthInput.value = String(state.width);
    if (document.activeElement !== ui.heightInput) ui.heightInput.value = String(state.height);
    ui.labelSwitch.classList.toggle("is-on", Boolean(state.showLabels));
    ui.updating = false;
}

function renderTemplateStrip(ui) {
    ui.templateStrip.textContent = "";
    for (const template of ui.payload.templates) {
        const card = el("button", `ccs-template-card${template.id === ui.state.templateId ? " is-active" : ""}`);
        card.type = "button";
        card.append(buildTemplateMini(template));
        const copy = el("div", "ccs-template-copy");
        copy.append(
            el("span", "ccs-template-name", template.name),
            el("span", "ccs-template-count", `${template.cells?.length || 0} 格`),
        );
        card.append(copy);
        card.addEventListener("click", () => switchTemplate(ui, template.id));
        ui.templateStrip.append(card);
    }
}

function switchTemplate(ui, templateId) {
    const template = ui.payload.templates.find((item) => item.id === templateId);
    if (!template) return;
    ui.state = defaultState(template, ui.payload, ui.state);
    ui.state.width = roundDimension(template.width);
    ui.state.height = roundDimension(template.height);
    ui.selectedIndex = 0;
    commitUi(ui, { board: true, inspector: true, library: true, header: true, sync: true });
    ui.showToast(`已切换到：${template.name}`);
}

function renderBoard(ui) {
    const board = ui.board;
    board.textContent = "";
    board.style.setProperty("--ccs-board-accent", ui.state.accent);
    board.classList.toggle("show-labels", Boolean(ui.state.showLabels));

    const rule = el("div", "ccs-board-rule");
    board.append(rule);
    if (ui.state.showLabels) {
        board.append(
            el("div", "ccs-board-title", ui.state.title || "未命名角色"),
            el("div", "ccs-board-subtitle", ui.state.subtitle || ""),
        );
    }

    const template = templateFor(ui.state, ui.payload);
    template.cells.forEach((cell, index) => {
        const slot = ui.state.slots[index] || slotFromCell(cell, index);
        const isDisabled = slot.enabled === false;
        const cellNode = el("div", `ccs-cell${index === ui.selectedIndex ? " is-selected" : ""}${isDisabled ? " is-disabled" : ""}`);
        cellNode.style.left = `${cell.x * 100}%`;
        cellNode.style.top = `${cell.y * 100}%`;
        cellNode.style.width = `${cell.w * 100}%`;
        cellNode.style.height = `${cell.h * 100}%`;
        cellNode.draggable = true;
        cellNode.dataset.index = String(index);

        const media = el("div", `ccs-cell-media${slot.fit === "contain" ? " is-contain" : ""}`);
        if (slot.image) {
            const image = el("img");
            image.alt = "";
            image.src = imageUrl(slot);
            image.draggable = false;
            image.style.transform = `translate(${Number(slot.offsetX || 0) * 40}%, ${Number(slot.offsetY || 0) * 40}%) scale(${Number(slot.zoom || 1)})${cell.mirror ? " scaleX(-1)" : ""}`;
            media.append(image);
        } else {
            const empty = el("div", "ccs-cell-empty");
            empty.append(el("div", "ccs-cell-empty-plus", "+"), el("div", "ccs-cell-empty-label", slot.label || cell.label));
            media.append(empty);
        }

        const indexBadge = el("div", "ccs-cell-index", String(index + 1).padStart(2, "0"));
        const caption = el("div", "ccs-cell-caption", slot.label || cell.label);
        const quick = el("div", "ccs-cell-quick");
        const toggle = el("button", `ccs-cell-toggle${isDisabled ? " is-off" : ""}`, isDisabled ? "🚫" : "👁");
        const replace = el("button", "", "↻");
        const clear = el("button", "", "×");
        toggle.type = "button";
        replace.type = "button";
        clear.type = "button";
        toggle.title = isDisabled ? "启用此画格" : "禁用此画格";
        replace.title = "替换图片";
        clear.title = "清空图片";
        toggle.addEventListener("click", (event) => {
            event.stopPropagation();
            slot.enabled = slot.enabled === false;
            commitUi(ui, { board: true, inspector: true, sync: true });
        });
        replace.addEventListener("click", (event) => {
            event.stopPropagation();
            openFilePicker(ui, index);
        });
        clear.addEventListener("click", (event) => {
            event.stopPropagation();
            slot.image = "";
            slot.subfolder = "";
            ui.selectedIndex = index;
            commitUi(ui, { board: true, inspector: true, library: true, sync: true });
        });
        quick.append(toggle, replace, clear);
        cellNode.append(media, indexBadge, caption, quick);

        cellNode.addEventListener("click", () => {
            ui.selectedIndex = index;
            setActiveTab(ui, "cell");
            for (const item of board.querySelectorAll(".ccs-cell")) item.classList.remove("is-selected");
            cellNode.classList.add("is-selected");
            syncCellForm(ui);
        });
        cellNode.addEventListener("dblclick", () => openFilePicker(ui, index));
        cellNode.addEventListener("dragstart", (event) => {
            event.dataTransfer.effectAllowed = "move";
            event.dataTransfer.setData(SLOT_MIME, String(index));
            event.dataTransfer.setData("text/plain", String(index));
            cellNode.classList.add("is-dragging");
        });
        cellNode.addEventListener("dragend", () => {
            cellNode.classList.remove("is-dragging");
            for (const item of board.querySelectorAll(".ccs-cell")) item.classList.remove("is-drop-target");
        });
        cellNode.addEventListener("dragover", (event) => {
            if (!event.dataTransfer) return;
            event.preventDefault();
            cellNode.classList.add("is-drop-target");
        });
        cellNode.addEventListener("dragleave", () => cellNode.classList.remove("is-drop-target"));
        cellNode.addEventListener("drop", (event) => {
            event.preventDefault();
            cellNode.classList.remove("is-drop-target");
            const slotSource = event.dataTransfer?.getData(SLOT_MIME);
            const imageSource = event.dataTransfer?.getData(IMAGE_MIME);
            if (slotSource !== undefined && slotSource !== "") {
                moveSlot(ui, Number(slotSource), index);
                return;
            }
            if (imageSource !== undefined && imageSource !== "") {
                assignImage(ui, Number(imageSource), index);
            }
        });
        board.append(cellNode);
    });
    requestAnimationFrame(() => updateBoardFrame(ui));
}

function bindBoardResize(ui) {
    if (typeof ResizeObserver === "function") {
        ui.boardObserver = new ResizeObserver(() => updateBoardFrame(ui));
        ui.boardObserver.observe(ui.boardWrap);
    }
}

function updateBoardFrame(ui) {
    const wrap = ui.boardWrap;
    if (!wrap || !ui.board) return;
    const compact = (ui.root?.clientWidth || 0) < 980;
    ui.root?.classList.toggle("is-compact", compact);
    const availableW = Math.max(120, wrap.clientWidth - 24);
    const availableH = Math.max(100, wrap.clientHeight - 24);
    const ratio = Math.max(0.2, Number(ui.state.width) / Math.max(1, Number(ui.state.height)));
    let width = availableW;
    let height = width / ratio;
    if (height > availableH) {
        height = availableH;
        width = height * ratio;
    }
    ui.board.style.width = `${Math.max(80, Math.floor(width))}px`;
    ui.board.style.height = `${Math.max(80, Math.floor(height))}px`;
}

function renderLibrary(ui) {
    ui.libraryMeta.textContent = `${ui.state.library.length} 张`;
    ui.libraryList.textContent = "";
    if (!ui.state.library.length) {
        ui.libraryList.append(el("div", "ccs-library-empty", "暂无素材"));
        return;
    }
    ui.state.library.forEach((item, index) => {
        const thumb = el("div", "ccs-thumb");
        thumb.draggable = true;
        thumb.title = item.name || item.image;
        const image = el("img");
        image.alt = "";
        image.src = imageUrl(item);
        image.draggable = false;
        const meta = el("div", "ccs-thumb-meta", item.name || item.image.split("/").pop() || item.image);
        const remove = el("button", "ccs-thumb-remove", "×");
        remove.type = "button";
        remove.title = "从素材库移除";
        remove.addEventListener("click", (event) => {
            event.stopPropagation();
            ui.state.library.splice(index, 1);
            queueStateSync(ui.node, ui.state);
            renderLibrary(ui);
        });
        thumb.append(image, meta, remove);
        thumb.addEventListener("click", () => {
            if (ui.selectedIndex >= 0) assignImage(ui, index, ui.selectedIndex);
        });
        thumb.addEventListener("dragstart", (event) => {
            event.dataTransfer.effectAllowed = "copy";
            event.dataTransfer.setData(IMAGE_MIME, String(index));
            event.dataTransfer.setData("text/plain", String(index));
        });
        ui.libraryList.append(thumb);
    });
}

function openFilePicker(ui, slotIndex) {
    if (slotIndex !== null && slotIndex !== undefined) {
        ui.fileInput.dataset.slotIndex = String(slotIndex);
    } else {
        delete ui.fileInput.dataset.slotIndex;
    }
    ui.fileInput.click();
}

async function uploadFiles(ui, files, targetIndex = null) {
    ui.uploadButton.disabled = true;
    ui.libraryUpload.disabled = true;
    let uploaded = 0;
    const uploadedItems = [];
    try {
        for (const file of files) {
            if (!file?.type?.startsWith("image/")) continue;
            const item = await uploadImageFile(file);
            if (!item) continue;
            const key = `${item.subfolder}\u0000${item.image}`;
            const exists = ui.state.library.some((entry) => `${entry.subfolder}\u0000${entry.image}` === key);
            if (!exists) ui.state.library.push(item);
            uploadedItems.push(item);
            uploaded += 1;
        }
        if (uploaded && targetIndex !== null && Number.isInteger(Number(targetIndex))) {
            const first = uploadedItems[0];
            const key = `${first.subfolder}\u0000${first.image}`;
            const libraryIndex = ui.state.library.findIndex(
                (entry) => `${entry.subfolder}\u0000${entry.image}` === key,
            );
            if (libraryIndex >= 0) assignImage(ui, libraryIndex, Number(targetIndex));
        } else if (uploaded) {
            fillEmptySlots(ui, true);
        }
        renderLibrary(ui);
        syncCellForm(ui);
        queueStateSync(ui.node, ui.state);
        ui.showToast(uploaded ? `已加入 ${uploaded} 张素材` : "没有可用的图片", !uploaded);
    } catch (error) {
        console.error("[CharacterCardStudio] Upload failed", error);
        ui.showToast("图片上传失败", true);
    } finally {
        ui.uploadButton.disabled = false;
        ui.libraryUpload.disabled = false;
    }
}

async function uploadImageFile(file) {
    const form = new FormData();
    form.append("image", file, file.name);
    form.append("type", "input");
    form.append("overwrite", "false");
    const response = await api.fetchApi("/upload/image", { method: "POST", body: form });
    if (!response.ok) throw new Error(`Upload failed: HTTP ${response.status}`);
    const data = await response.json();
    const name = String(data.name || file.name);
    return {
        image: name,
        subfolder: String(data.subfolder || ""),
        name: name.split("/").pop() || file.name,
        useForIdentity: true,
    };
}

function fillEmptySlots(ui, quiet = false) {
    let libraryIndex = 0;
    let filled = 0;
    for (const slot of ui.state.slots) {
        if (slot.image) continue;
        while (libraryIndex < ui.state.library.length && !ui.state.library[libraryIndex].image) libraryIndex += 1;
        if (libraryIndex >= ui.state.library.length) break;
        const item = ui.state.library[libraryIndex];
        slot.image = item.image;
        slot.subfolder = item.subfolder || "";
        libraryIndex += 1;
        filled += 1;
    }
    commitUi(ui, { board: true, inspector: true, library: true, sync: true });
    if (!quiet) ui.showToast(filled ? `已填充 ${filled} 个画格` : "没有可填充的空画格", !filled);
}

async function copyState(ui) {
    const text = JSON.stringify(ui.state, null, 2);
    try {
        await navigator.clipboard.writeText(text);
        ui.showToast("卡版 JSON 已复制");
    } catch (error) {
        const area = document.createElement("textarea");
        area.value = text;
        area.style.position = "fixed";
        area.style.left = "-9999px";
        document.body.append(area);
        area.select();
        try {
            document.execCommand("copy");
            ui.showToast("卡版 JSON 已复制");
        } catch (copyError) {
            ui.showToast("复制失败", true);
        }
        area.remove();
    }
}

function resizeNode(node) {
    const width = Math.max(Number(node.size?.[0]) || 0, 1080);
    const height = Math.max(Number(node.size?.[1]) || 0, 820);
    if (Math.abs(width - (node.size?.[0] || 0)) > 1 || Math.abs(height - (node.size?.[1] || 0)) > 1) {
        node.setSize?.([width, height]);
    }
}

async function setupNode(node) {
    if (!node || node.__ccsSetupStarted) return node.__ccsSetupPromise;
    node.__ccsSetupStarted = true;
    node.__ccsSetupPromise = (async () => {
        await ensureStyle();
        const payload = await loadPayload();
        const state = stateFromWidget(node, payload);
        hideNativeWidgets(node);
        const ui = buildUi(node, payload, state);
        node.__ccsUi = ui;

        if (typeof node.addDOMWidget === "function") {
            const domWidget = node.addDOMWidget("character_card_studio", "character_card_studio", ui.root, {
                serialize: false,
                getMinHeight: () => 760,
                afterResize: () => updateBoardFrame(ui),
            });
            if (domWidget) {
                domWidget.serialize = false;
                domWidget.type = "character_card_studio";
                node.__ccsDomWidget = domWidget;
            }
        }

        resizeNode(node);
        refreshVueWidgets(node);
        refreshNode(node);
        setTimeout(() => {
            updateBoardFrame(ui);
            resizeNode(node);
        }, 0);
        setTimeout(() => {
            updateBoardFrame(ui);
            resizeNode(node);
        }, 350);
        return ui;
    })();
    return node.__ccsSetupPromise;
}

function hideNativeWidgets(node) {
    for (const name of [STATE_WIDGET, WIDTH_WIDGET, HEIGHT_WIDGET]) {
        const widget = widgetOf(node, name);
        markWidgetHidden(widget);
    }
    refreshVueWidgets(node);
}

function reloadStateFromWidget(node, payload) {
    const ui = node.__ccsUi;
    if (!ui) return;
    const next = stateFromWidget(node, payload);
    ui.state = next;
    ui.selectedIndex = Math.max(0, Math.min(ui.selectedIndex, next.slots.length - 1));
    ui.renderAll();
    queueStateSync(node, next);
}

function installNode(nodeType, nodeData) {
    if (nodeData?.name !== NODE_ID) return;
    autoHideWidgets(nodeType, [STATE_WIDGET, WIDTH_WIDGET, HEIGHT_WIDGET]);

    const chain = (name, after) => {
        const original = nodeType.prototype[name];
        nodeType.prototype[name] = function (...args) {
            const result = original?.apply(this, args);
            try {
                after(this, args);
            } catch (error) {
                console.error("[CharacterCardStudio]", error);
            }
            return result;
        };
    };

    chain("onNodeCreated", (node) => {
        setupNode(node);
    });
    chain("onAdded", (node) => {
        setupNode(node);
    });
    chain("onConfigure", (node) => {
        setupNode(node).then(async () => {
            const payload = await loadPayload();
            reloadStateFromWidget(node, payload);
        });
        setTimeout(async () => {
            try {
                const payload = await loadPayload();
                reloadStateFromWidget(node, payload);
            } catch (error) {
                console.error("[CharacterCardStudio] Configure reload failed", error);
            }
        }, 120);
    });
    chain("onResize", (node) => {
        setTimeout(() => {
            updateBoardFrame(node.__ccsUi);
            refreshNode(node);
        }, 0);
    });
}

app.registerExtension({
    name: "AICG3D.CharacterCardStudio",
    setup() {
        ensureStyle();
        loadPayload();
    },
    beforeRegisterNodeDef(nodeType, nodeData) {
        installNode(nodeType, nodeData);
    },
    nodeCreated(node) {
        if (String(node?.comfyClass || node?.type || "") === NODE_ID) setupNode(node);
    },
    loadedGraphNode(node) {
        if (String(node?.comfyClass || node?.type || "") === NODE_ID) setupNode(node);
    },
});
