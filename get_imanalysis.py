from market_research.analysis import ImgAnalysis

ima = ImgAnalysis()

url_list = []
url_list.extend(list(ima.preset_video_dict.values()))

for url in url_list:
    video_path= ima.download_video_from_yt(url)

video_paths = ima.read_files_from_inputpath(docs_type='video')

for video_path in video_paths:
    ima.process_video(video_path, skip_interval=30, showmode=False)


image_list = ima.read_files_from_inputpath()
image_list.sort()


ima.to_lab_images(image_list, showmode=True)