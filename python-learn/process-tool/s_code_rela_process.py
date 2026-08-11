"""
经纪业务线个人客户S码编制流程 - 时序图生成器
运行后生成 s_code_flow.html，浏览器打开即可查看。
"""

from dataclasses import dataclass, field
from typing import List


# ── 数据模型 ──────────────────────────────────────────────

@dataclass
class Participant:
    label: str
    caption: str
    role: str = "neutral"          # focus | neutral | external


@dataclass
class Message:
    from_idx: int                  # 发送方索引
    to_idx: int                    # 接收方索引（self-call 时与 from_idx 相同）
    label: str                     # 主标签（箭头上方胶囊内）
    desc: str = ""                 # 描述文字（箭头下方，可选）
    msg_type: str = "request"      # request | return
    focus: bool = False


@dataclass
class PhaseChip:
    label: str
    x: int
    width: int = 148


@dataclass
class DetailItem:
    step: int
    title: str
    desc: str


# ── 流程数据 ──────────────────────────────────────────────

TITLE = "经纪业务线个人客户S码编制流程"
BADGE = ""

PARTICIPANTS: List[Participant] = [
    Participant("数仓",       "数据整合与服务", role="focus"),
    Participant("CCRM 系统",  "编码与关系维护", role="neutral"),
    Participant("下游系统",    "数据消费方",     role="external"),
]

MESSAGES: List[Message] = [
    Message(from_idx=0, to_idx=1, label="下发客户信息表",
            desc="维护：客户号<->一账通码",
            msg_type="request", focus=True),
    Message(from_idx=1, to_idx=0, label="回流S码映射关系",
            desc="维护：一账通码<->S码",
            msg_type="return"),
    Message(from_idx=0, to_idx=0, label="整合至ECIF表",
            desc="维护：客户号<->S码",
            msg_type="request"),
    Message(from_idx=0, to_idx=2, label="提供数据服务",
            desc="视图：客户号<->S码映射关系",
            msg_type="request"),
]

PHASE_CHIPS: List[PhaseChip] = [
    PhaseChip("① 数据整合与下发", x=48),
    PhaseChip("② S码生成与回流", x=286),
    PhaseChip("③ 数据服务输出",  x=524),
]

DETAILS: List[DetailItem] = [
    DetailItem(1, "数据整合与下发",
               "数仓基于统一账户系统，生成 CCRM 编码使用个人客户信息表"
               "（dwmdata.m_cust_ccrm_encode_used_indv_info），下发至 CCRM 系统。"),
    DetailItem(2, "S码生成与回流",
               "CCRM 根据证件类型和号码分配S码，在 personal_cust_system_relation "
               "表中维护\"一账通码 ↔ S码\"映射，回流至数仓。"),
    DetailItem(3, "数据整合与输出",
               "数仓将映射关系整合至 ECIF 客户关系表（dwmdata.m_cust_ecif_rela），"
               "维护\"客户号 ↔ S码\"视图，为下游系统提供数据服务。"),
]


# ── 布局参数 ──────────────────────────────────────────────

class Layout:
    SVG_WIDTH      = 720
    PART_W         = 116
    PART_H         = 56
    PART_Y         = 62
    PART_GAP       = 59           # 参与者水平间距（自动计算后微调）
    LIFELINE_TOP   = PART_Y + PART_H + 4     # 122
    ROW_PITCH      = 80           # 消息行间距（含描述文字空间）
    FIRST_MSG_Y    = 146
    DESC_OFFSET    = 16           # 描述文字相对箭头 y 的偏移
    ACTIVATION_W   = 18
    ACTIVATION_RX  = 6
    LABEL_H        = 24
    LABEL_RX       = 8
    SELF_CALL_DX   = 32           # self-call 向右偏移
    SELF_CALL_DY   = 28
    CHIP_Y         = 18
    CHIP_H         = 26
    CHIP_RX        = 13

    @classmethod
    def center_x(cls, idx: int) -> int:
        """第 idx 个参与者的中心 x 坐标"""
        x0 = 42 + idx * (cls.PART_W + cls.PART_GAP)
        return x0 + cls.PART_W // 2

    @classmethod
    def part_x(cls, idx: int) -> int:
        return 42 + idx * (cls.PART_W + cls.PART_GAP)

    @classmethod
    def msg_y(cls, idx: int) -> int:
        return cls.FIRST_MSG_Y + idx * cls.ROW_PITCH

    @classmethod
    def svg_height(cls) -> int:
        last_y = cls.msg_y(len(MESSAGES) - 1)
        return last_y + 72        # 底部留白


L = Layout


# ── SVG 构建 ──────────────────────────────────────────────

def _esc(text: str) -> str:
    """转义 XML 特殊字符"""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def build_defs() -> str:
    return """\
        <defs>
          <marker id="seqArr" viewBox="0 0 8 8" refX="7" refY="4"
                  markerWidth="8" markerHeight="8" markerUnits="userSpaceOnUse" orient="auto">
            <path class="arrowHeadPath" d="M1 1 L7 4 L1 7 Z" />
          </marker>
          <marker id="seqArrF" viewBox="0 0 8 8" refX="7" refY="4"
                  markerWidth="8" markerHeight="8" markerUnits="userSpaceOnUse" orient="auto">
            <path class="arrowHeadPath" data-focus="true" d="M1 1 L7 4 L1 7 Z" />
          </marker>
        </defs>"""


def build_phase_chips() -> str:
    lines = []
    for chip in PHASE_CHIPS:
        cx = chip.x + chip.width // 2
        lines.append(
            f'        <rect class="phaseChip" x="{chip.x}" y="{L.CHIP_Y}" '
            f'width="{chip.width}" height="{L.CHIP_H}" rx="{L.CHIP_RX}" />'
        )
        lines.append(
            f'        <text class="phaseText" x="{cx}" y="{L.CHIP_Y + 18}" '
            f'text-anchor="middle">{_esc(chip.label)}</text>'
        )
    return "\n".join(lines)


def build_participants() -> str:
    lines = []
    for i, p in enumerate(PARTICIPANTS):
        px = L.part_x(i)
        cx = L.PART_W // 2
        lines.append(
            f'        <g class="participant" data-role="{p.role}" transform="translate({px} {L.PART_Y})">'
        )
        lines.append(
            f'          <rect class="participantBox" width="{L.PART_W}" height="{L.PART_H}" rx="8" />'
        )
        lines.append(
            f'          <text class="participantLabel" x="{cx}" y="24" '
            f'text-anchor="middle">{_esc(p.label)}</text>'
        )
        lines.append(
            f'          <text class="participantCaption" x="{cx}" y="44" '
            f'text-anchor="middle">{_esc(p.caption)}</text>'
        )
        lines.append("        </g>")
    return "\n".join(lines)


def build_lifelines() -> str:
    bottom = L.svg_height() - 40
    lines = []
    for i in range(len(PARTICIPANTS)):
        cx = L.center_x(i)
        lines.append(
            f'        <path class="lifeline" d="M{cx} {L.LIFELINE_TOP} V{bottom}" fill="none" />'
        )
    return "\n".join(lines)


def _estimate_label_width(text: str) -> int:
    """估算中文标签宽度（12px 字号，约 13px/汉字 + 16px 内边距）"""
    return len(text) * 13 + 16


def _estimate_text_width(text: str) -> int:
    """估算文本宽度：中文约13px/字，英文约7px/字，含内边距"""
    w = 0
    for ch in text:
        if '\u4e00' <= ch <= '\u9fff':
            w += 13
        else:
            w += 7
    return w + 16


def build_messages() -> str:
    lines = []
    for idx, msg in enumerate(MESSAGES):
        y = L.msg_y(idx)
        from_cx = L.center_x(msg.from_idx)
        to_cx   = L.center_x(msg.to_idx)

        focus_attr = ' data-focus="true"' if msg.focus else ""
        marker     = "url(#seqArrF)" if msg.focus else "url(#seqArr)"
        type_attr  = f' data-type="{msg.msg_type}"' if msg.msg_type == "return" else ""

        label_w = _estimate_label_width(msg.label)

        if msg.from_idx == msg.to_idx:
            # ── self-call：U 形回路 ──
            dx = L.SELF_CALL_DX
            dy = L.SELF_CALL_DY
            path_d = f"M{from_cx} {y} H{from_cx + dx} V{y + dy} H{from_cx}"
            label_x = from_cx + dx + 6
            label_cx = label_x + label_w // 2
            label_y_top = y + 2
            label_y_text = y + 17

            lines.append(
                f'        <path class="messagePath"{type_attr} d="{path_d}" '
                f'marker-end="{marker}" fill="none" />'
            )
            lines.append(
                f'        <rect class="labelBg"{focus_attr} x="{label_x}" y="{label_y_top}" '
                f'width="{label_w}" height="{L.LABEL_H}" rx="{L.LABEL_RX}" />'
            )
            lines.append(
                f'        <text class="messageLabel"{focus_attr} x="{label_cx}" y="{label_y_text}" '
                f'text-anchor="middle">{_esc(msg.label)}</text>'
            )
            # 描述文字
            if msg.desc:
                desc_w = _estimate_text_width(msg.desc)
                desc_x = label_cx - desc_w // 2
                desc_y = label_y_top + L.LABEL_H + L.DESC_OFFSET
                lines.append(
                    f'        <text class="messageDesc" x="{label_cx}" y="{desc_y}" '
                    f'text-anchor="middle">{_esc(msg.desc)}</text>'
                )
        else:
            # ── 普通箭头 ──
            from_act_left = from_cx - L.ACTIVATION_W // 2
            from_act_right = from_cx + L.ACTIVATION_W // 2
            to_act_left = to_cx - L.ACTIVATION_W // 2
            to_act_right = to_cx + L.ACTIVATION_W // 2

            if from_cx < to_cx:
                start_x = from_act_right
                end_x = to_act_left
            else:
                start_x = from_act_left
                end_x = to_act_right

            path_d = f"M{start_x} {y} H{end_x}"

            mid_x = (start_x + end_x) // 2
            label_x = mid_x - label_w // 2
            label_y_top = y - 14
            label_y_text = y + 3

            lines.append(
                f'        <path class="messagePath"{focus_attr}{type_attr} d="{path_d}" '
                f'marker-end="{marker}" fill="none" />'
            )
            lines.append(
                f'        <rect class="labelBg"{focus_attr} x="{label_x}" y="{label_y_top}" '
                f'width="{label_w}" height="{L.LABEL_H}" rx="{L.LABEL_RX}" />'
            )
            lines.append(
                f'        <text class="messageLabel"{focus_attr} x="{mid_x}" y="{label_y_text}" '
                f'text-anchor="middle">{_esc(msg.label)}</text>'
            )
            # 描述文字
            if msg.desc:
                desc_w = _estimate_text_width(msg.desc)
                desc_x = mid_x - desc_w // 2
                desc_y = label_y_top + L.LABEL_H + L.DESC_OFFSET
                lines.append(
                    f'        <text class="messageDesc" x="{mid_x}" y="{desc_y}" '
                    f'text-anchor="middle">{_esc(msg.desc)}</text>'
                )
    return "\n".join(lines)


def build_activations() -> str:
    """根据消息自动计算每个参与者的激活条高度"""
    # 记录每个参与者的激活起止行
    activation_map: dict[int, list[int]] = {}
    for idx, msg in enumerate(MESSAGES):
        for pi in (msg.from_idx, msg.to_idx):
            if pi not in activation_map:
                activation_map[pi] = []
            activation_map[pi].append(idx)

    lines = []
    for pi, rows in activation_map.items():
        if not rows:
            continue
        y_start = L.msg_y(min(rows)) - 10
        y_end   = L.msg_y(max(rows)) + 10
        cx = L.center_x(pi)
        x = cx - L.ACTIVATION_W // 2
        h = y_end - y_start
        role_attr = ' data-role="focus"' if PARTICIPANTS[pi].role == "focus" else ""
        lines.append(
            f'        <rect class="activation"{role_attr} x="{x}" y="{y_start}" '
            f'width="{L.ACTIVATION_W}" height="{h}" rx="{L.ACTIVATION_RX}" />'
        )
    return "\n".join(lines)


def build_detail_panel() -> str:
    items = []
    for d in DETAILS:
        items.append(f"""\
      <div class="detailItem">
        <span class="detailStep">{d.step}</span>
        <span class="detailTitle">{_esc(d.title)}</span>
        <div class="detailDesc">{_esc(d.desc)}</div>
      </div>""")
    return "\n".join(items)


# ── 完整 HTML 模板 ────────────────────────────────────────

CSS = """\
:root {
  color-scheme: light;
  --surface: #FFFFFF;
  --surface-muted: #F7F7F8;
  --text: #171717;
  --text-muted: #52525B;
  --border: rgba(23, 23, 23, 0.12);
  --brand: #4B3FE3;
  --brand-soft: #F2F7FF;
  --brand-soft-strong: #E5EAFF;
  --brand-text: #1A1759;
  --brand-on: #FFFFFF;
  --chart-series-1: #3C2ECA;
  --chart-series-2: #A9AEFF;
  --chart-series-3: #6F6FFF;
  --chart-series-4: #22A5F7;
  --chart-other: #D3D4DA;
  --accent: #27D2BF;
  --accent-soft: #EAFBF8;
  --accent-text: #0F766E;
  --success: #1DC981;
  --warning: #EFAA17;
  --danger: #E8463A;
  --radius: 8px;
  --radius-card: 12px;
  --radius-full: 999px;
  --spacer-4: 4px;
  --spacer-8: 8px;
  --spacer-12: 12px;
  --spacer-16: 16px;
  --spacer-20: 20px;
  --spacer-24: 24px;
  --font-sans: "SF Pro Text", "PingFang SC", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  --font-metric: "Inter", "SF Pro Text", "PingFang SC", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  --font-mono: "JetBrains Mono", ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  --weight-regular: 400;
  --weight-medium: 500;
  --weight-strong: 600;
  --text-caption: 12px/18px;
  --text-body: 14px/20px;
  --text-title: 16px/24px;
  --text-code: 13px/20px;
}

@media (prefers-color-scheme: dark) {
  :root {
    color-scheme: dark;
    --surface: #FFFFFF;
    --surface-muted: #F7F7F8;
    --text: #171717;
    --text-muted: #52525B;
    --border: rgba(23, 23, 23, 0.12);
    --brand: #4B3FE3;
    --brand-soft: #F2F7FF;
    --brand-soft-strong: #E5EAFF;
    --brand-text: #1A1759;
    --brand-on: #FFFFFF;
  }
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  background: #FFFFFF;
  color: var(--text);
  font: var(--weight-regular) var(--text-body) var(--font-sans);
  padding: var(--spacer-24);
}

.widget {
  color: var(--text);
  background: transparent;
  font: var(--weight-regular) var(--text-body) var(--font-sans);
  letter-spacing: 0;
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
}

.sequenceCard {
  box-sizing: border-box;
  width: 100%;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-card);
  padding: var(--spacer-20);
}

.sequenceHeader {
  display: flex;
  align-items: start;
  justify-content: space-between;
  gap: var(--spacer-16);
}

.sequenceTitleGroup {
  display: grid;
  gap: var(--spacer-4);
  min-width: 0;
}

.sequenceTitle {
  margin: 0;
  color: var(--text);
  font: var(--weight-medium) var(--text-title) var(--font-sans);
}

.sequenceBadge {
  flex: 0 0 auto;
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 var(--spacer-12);
  color: var(--brand-text);
  background: var(--surface-muted);
  border: 1px solid color-mix(in srgb, var(--border) 88%, transparent);
  border-radius: var(--radius-full);
  font: var(--weight-medium) var(--text-caption) var(--font-sans);
}

.sequenceCanvas {
  margin-top: var(--spacer-16);
  overflow: hidden;
  background: var(--surface-muted);
  border: 1px solid color-mix(in srgb, var(--border) 70%, transparent);
  border-radius: var(--radius);
}

.sequenceSvg {
  display: block;
  width: 100%;
  height: auto;
}

.participantBox {
  fill: var(--surface);
  stroke: color-mix(in srgb, var(--border) 92%, transparent);
  stroke-width: 1;
}

.participant[data-role="focus"] .participantBox {
  fill: color-mix(in srgb, var(--brand) 7%, var(--surface));
  stroke: color-mix(in srgb, var(--brand) 72%, var(--border));
}

.participant[data-role="external"] .participantBox {
  stroke: color-mix(in srgb, var(--text-muted) 42%, var(--border));
}

.participantLabel {
  fill: var(--text);
  font: var(--weight-medium) var(--text-body) var(--font-sans);
}

.participantCaption {
  fill: var(--text-muted);
  font: var(--weight-regular) var(--text-caption) var(--font-sans);
}

.participant[data-role="focus"] .participantLabel {
  fill: var(--brand-text);
}

.participant[data-role="focus"] .participantCaption {
  fill: var(--brand);
}

.lifeline {
  fill: none;
  stroke: color-mix(in srgb, var(--text-muted) 42%, transparent);
  stroke-width: 1.2;
  stroke-dasharray: 5 7;
  stroke-linecap: round;
}

.activation {
  fill: var(--surface);
  stroke: color-mix(in srgb, var(--border) 92%, transparent);
  stroke-width: 1;
}

.activation[data-role="focus"] {
  fill: color-mix(in srgb, var(--brand) 8%, var(--surface));
  stroke: color-mix(in srgb, var(--brand) 62%, var(--border));
}

.messagePath {
  fill: none;
  stroke: var(--text-muted);
  stroke-width: 1.5;
  stroke-linecap: butt;
  stroke-linejoin: round;
}

.messagePath[data-type="return"] {
  stroke-dasharray: 7 6;
}

.messagePath[data-focus="true"] {
  stroke: var(--brand);
  stroke-width: 1.8;
}

.arrowHeadPath {
  fill: var(--text-muted);
}

.arrowHeadPath[data-focus="true"] {
  fill: var(--brand);
}

.labelBg {
  fill: var(--surface);
  stroke: color-mix(in srgb, var(--border) 76%, transparent);
}

.labelBg[data-focus="true"] {
  fill: var(--brand-soft);
  stroke: color-mix(in srgb, var(--brand) 42%, var(--border));
}

.messageLabel {
  fill: var(--text);
  font: var(--weight-medium) var(--text-caption) var(--font-sans);
}

.messageLabel[data-focus="true"] {
  fill: var(--brand-text);
}

.messageDesc {
  fill: var(--text-muted);
  font: var(--weight-regular) var(--text-caption) var(--font-mono);
  opacity: 0.8;
}

.phaseChip {
  fill: color-mix(in srgb, var(--surface-muted) 56%, var(--surface));
  stroke: color-mix(in srgb, var(--border) 68%, transparent);
}

.phaseText {
  fill: var(--text-muted);
  font: var(--weight-medium) var(--text-caption) var(--font-sans);
}

.detailPanel {
  margin-top: var(--spacer-16);
  display: grid;
  gap: var(--spacer-12);
}

.detailItem {
  padding: var(--spacer-12) var(--spacer-16);
  background: var(--surface-muted);
  border: 1px solid color-mix(in srgb, var(--border) 86%, transparent);
  border-radius: var(--radius);
}

.detailStep {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  color: var(--brand-on);
  background: var(--brand);
  border-radius: var(--radius-full);
  font: var(--weight-medium) var(--text-caption) var(--font-sans);
  margin-right: var(--spacer-8);
}

.detailTitle {
  color: var(--text);
  font: var(--weight-medium) var(--text-body) var(--font-sans);
  display: inline;
}

.detailDesc {
  margin-top: var(--spacer-4);
  color: var(--text-muted);
  font: var(--weight-regular) var(--text-caption) var(--font-sans);
  padding-left: 30px;
}"""


def generate_html() -> str:
    svg_h = L.svg_height()
    return f"""\
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{_esc(TITLE)}</title>
<style>
{CSS}
</style>
</head>
<body>
<div class="widget" data-dynamic-ui-widget data-template="sequence-diagram">
  <section class="sequenceCard" aria-label="S码编制流程时序图">
    <div class="sequenceHeader">
      <div class="sequenceTitleGroup">
        <h3 class="sequenceTitle">{_esc(TITLE)}</h3>
      </div>
      <div class="sequenceBadge">{_esc(BADGE)}</div>
    </div>
    <div class="sequenceCanvas">
      <svg class="sequenceSvg" viewBox="0 0 {L.SVG_WIDTH} {svg_h}" role="img"
           aria-label="数仓、CCRM系统、下游系统之间的S码编制流程">
{build_defs()}

        <!-- Phase chips -->
{build_phase_chips()}

        <!-- Participants -->
{build_participants()}

        <!-- Lifelines -->
{build_lifelines()}

        <!-- Activation bars -->
{build_activations()}

        <!-- Messages -->
{build_messages()}
      </svg>
    </div>

    <!-- Detail panel -->
    <div class="detailPanel">
{build_detail_panel()}
    </div>
  </section>
</div>
</body>
</html>"""


# ── 入口 ──────────────────────────────────────────────────

if __name__ == "__main__":
    import os

    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(output_dir, "s_code_flow.html")

    html = generate_html()
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"已生成流程图: {output_path}")
