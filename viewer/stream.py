from viewer.YouTube import YTViewer


def stream():
    controller = YTViewer()
    controller.create_stealth_session()
    controller.stream_video()
    controller.destroy_session()