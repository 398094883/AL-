import math
import streamlit as s

# 设置网页标题与布局
s.set_page_config(
    page_title="航空货舱载荷与操作指引系统", page_icon="✈️", layout="centered"
)

# 机型及舱位限制数据库
DATABASE = {
    "B777-200LR / 300 / 300ER": {
        "FWD Cargo Hold": {
            "linear": 53.1,
            "area": 90.7,
            "notes": "Stn 899.7~998.0 为 78.9kg/in",
        },
        "AFT Cargo Hold": {
            "linear": 53.1,
            "area": 90.7,
            "notes": "特殊区域可达 78.9kg/in",
        },
        "BULK Hold": {
            "linear": 30.3,
            "area": 68.0,
            "notes": "线性递减至 15.8kg/in",
        },
    },
    "A350-900": {
        "FWD Cargo Hold": {"linear": 53.1, "area": 61.2, "notes": ""},
        "AFT Cargo Hold": {"linear": 53.1, "area": 61.2, "notes": ""},
        "BULK Hold": {"linear": None, "area": 38.5, "notes": "线载荷未列出"},
    },
    "A380-800 HD/LD/CRC": {
        "FWD Cargo Hold": {"linear": 52.5, "area": 61.2, "notes": ""},
        "AFT Cargo Hold": {"linear": 52.5, "area": 61.2, "notes": ""},
        "BULK Hold": {
            "linear": None,
            "area": None,
            "notes": "请联系 EKAS CLC 获取信息",
        },
    },
}

s.title("✈️ 航空货舱载荷智能核算系统")
s.markdown("---")

# 1. 飞机与舱位选择
s.subheader("1. 飞机与舱位选择")
col1, col2 = s.columns(2)
with col1:
  selected_ac = s.selectbox("选择机型 (Aircraft):", list(DATABASE.keys()))
with col2:
  selected_comp = s.selectbox(
      "选择舱位 (Compartment):", list(DATABASE[selected_ac].keys())
  )

# 显示舱位备注
notes = DATABASE[selected_ac][selected_comp]["notes"]
if notes:
  s.info(f"💡 **舱位说明**: {notes}")

s.markdown("---")

# 2. 货物参数输入
s.subheader("2. 货物参数输入")
col3, col4 = s.columns(2)
with col3:
  selected_unit = s.selectbox("尺寸单位:", ["厘米 (cm)", "英寸 (inch)"])
with col4:
  weight = s.number_input("货物总重 (kg):", min_value=0.0, value=4000.0, step=10.0)

col5, col6 = s.columns(2)
with col5:
  raw_length = s.number_input(
      "接触长度 (Length):", min_value=0.0, value=140.0, step=1.0
  )
with col6:
  raw_width = s.number_input(
      "接触宽度 (Width):", min_value=0.0, value=120.0, step=1.0
  )

s.markdown("---")

# 计算逻辑与触发按钮
if s.button("🚀 开始智能计算核对", type="primary", use_container_width=True):
  if raw_length <= 0 or raw_width <= 0 or weight <= 0:
    s.error("错误：重量和尺寸必须大于 0！")
  else:
    # 单位换算
    if "厘米" in selected_unit:
      length = raw_length / 2.54
      width = raw_width / 2.54
      unit_note = f"输入 {raw_length}cm × {raw_width}cm 自动换算为 {length:.2f}in × {width:.2f}in"
    else:
      length = raw_length
      width = raw_width
      unit_note = "按英寸计算"

    limits = DATABASE[selected_ac][selected_comp]
    lin_limit = limits["linear"]
    area_limit = limits["area"]

    # 载荷计算
    contact_area_sqft = (length * width) / 144.0
    calc_area = weight / contact_area_sqft
    calc_lin = weight / length

    # 结果展示区
    s.subheader("3. 核查结果与操作指引")

    with s.container(border=True):
      s.write(f"**机型舱位**: {selected_ac} - {selected_comp}")
      s.write(f"**尺寸单位**: {selected_unit} ({unit_note})")
      s.write(
          f"• **实际线载荷**: `{calc_lin:.2f} kg/in` (限制:"
          f" `{lin_limit if lin_limit else '未列出'} kg/in`)"
      )
      s.write(
          f"• **接触面积**: `{contact_area_sqft:.2f} sq.ft` | **实际面载荷**:"
          f" `{calc_area:.2f} kg/sq.ft`"
      )

      s.markdown("---")
      s.markdown("### 📌 操作指引结果：")

      if calc_area <= 90.7:
        s.success(
            f"🟢 **[正常]** 当前面载荷 {calc_area:.2f} kg/sq.ft ≤ 90.7，符合安全标准！"
        )
      elif 90.7 < calc_area <= 136:
        s.error(
            f"🔴 **[需加垫板]** 当前面载荷 {calc_area:.2f} kg/sq.ft (介于 90.7 ~"
            " 136 之间)，需要加装垫板！"
        )
      else:
        s.error(
            f"🚨 **[需要向 SLE 发邮箱申请]** 当前面载荷 {calc_area:.2f} kg/sq.ft"
            " 超过 136，必须向 SLE 发送邮件申请审批！"
        )