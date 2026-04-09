import chainlit as cl


USER_TYPE_LABELS = {
    "nguoi_dung": "👤 Hành khách",
    "tai_xe_taxi": "🚖 Tài xế Taxi",
    "tai_xe_bike": "🛵 Tài xế Bike",
    "nha_hang": "🍜 Nhà hàng",
}


async def ask_user_type():
    actions = [
        cl.Action(name="set_type", value=key, label=label, payload={"value": key})
        for key, label in USER_TYPE_LABELS.items()
    ]
    await cl.Message(
        content="Xin chào! Trợ lý ảo XanhSM đã sẵn sàng hỗ trợ bạn!\nVui lòng mô tả vai trò của bạn:",
        actions=actions,
    ).send()


@cl.action_callback("set_type")
async def on_set_type(action: cl.Action):
    user_type = action.payload["value"]
    label = USER_TYPE_LABELS.get(user_type, user_type)
    cl.user_session.set("user_type", user_type)
    cl.user_session.set("history", [])
    await cl.Message(
        content=f"Đã xác nhận: **{label}**. Bạn có thể đặt câu hỏi ngay bây giờ!"
    ).send()
