import cv2
import os
import numpy as np
import matplotlib.pyplot as plt
from pytube import YouTube
from ._analysis_scheme import Analysis
from tqdm import tqdm


class ImgAnalysis(Analysis):
    def __init__(self,
                 export_prefix="text_", intput_folder_path="input", output_folder_path="results"):
        super().__init__(export_prefix=export_prefix, intput_folder_path=intput_folder_path,
                         output_folder_path=output_folder_path)

        self.preset_video_dict={"elemental":"https://www.youtube.com/watch?v=hXzcyx9V0xw",
                   "supermario":"https://www.youtube.com/watch?v=RjNcTBXTk4I",
                   "spideman1_1":"https://www.youtube.com/watch?v=g4Hbz2jLxvQ",
                   "spideman1_2":"https://www.youtube.com/watch?v=tg52up16eq0",
                   "spideman2_1":"https://www.youtube.com/watch?v=cqGjhVJWtEg&t=74s",
                   "spideman2_2":"https://www.youtube.com/watch?v=shW9i6k8cB0",
                   "arcane1":"https://www.youtube.com/watch?v=fXmAurh012s",
                   "arcane2":"https://www.youtube.com/watch?v=xISkcHi7djw"}


    def read_files_from_inputpath(self, docs_type="img"):

        file_type = {"img": ['.png', '.jpeg'],
                     "video": ['.mp4', ]
                     }
        file_list = self.intput_folder.glob('*')

        files = [file for file in file_list if file.suffix in file_type.get(docs_type)]
        return files

    def download_video_from_yt(self, url):
        file_path = None
        yt = YouTube(url)
        print(f"Downloading {yt.title}...")
        for _ in range(10):
            try:
                video_stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by(
                    'resolution').desc().first()
                video_stream.download(output_path=self.intput_folder)
                filename = video_stream.default_filename
                file_path = os.path.join(os.getcwd(), f"{filename}")
                break
            except Exception as e:
                pass

        return file_path

    def to_lab_images(self, image_list, showmode=True):
        for filename in tqdm(image_list):
            image_path = str(filename)
            title = filename.name.split(".")[0]
            image_BGR = cv2.imread(image_path)
            for _ in range(10):
                try:
                    _ = self.to_lab_image(image=image_BGR, save_title=title, showmode=showmode)


                    break
                except:
                    pass

    def to_lab_image(self, image, input_type='BGR', save_title: str = None, showmode=True):

        if showmode:
            # BGR을 RGB로 변환
            img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            plt.imshow(img_rgb)
            plt.axis('off')
            plt.show()

        conversion = cv2.COLOR_BGR2LAB if input_type == 'BGR' else cv2.COLOR_RGB2LAB
        image_LAB = cv2.cvtColor(image, conversion)

        y, x, z = image_LAB.shape
        LAB_flat = np.reshape(image_LAB, [y * x, z])

        colors = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) if input_type == 'BGR' else image
        colors = np.reshape(colors, [y * x, z]) / 255.

        l = LAB_flat[:, 0]
        a = LAB_flat[:, 1]
        b = LAB_flat[:, 2]

        fig = plt.figure(figsize=(12, 6))

        ax1 = fig.add_subplot(121, projection='3d')
        ax1.scatter(ys=b, xs=a, zs=l, s=10, c=colors, lw=0)
        ax1.set_xlabel('B')
        ax1.set_ylabel('A')
        ax1.set_zlabel('L')
        ax1.set_xlim([0, 255])
        ax1.set_ylim([0, 255])
        ax1.set_zlim([0, 255])
        ax1.set_title('3D Plot')
        ax1.xaxis.pane.fill = False
        ax1.yaxis.pane.fill = False
        ax1.zaxis.pane.fill = False
        ax1.grid(False)
        ax1.set_xticks([])
        ax1.set_yticks([])
        ax1.set_zticks([])

        # 두 번째 서브플롯 (2D scatter plot)
        ax2 = fig.add_subplot(122)
        ax2.scatter(y=b, x=a, s=10, c=colors, lw=0)
        ax2.set_xlabel('B')
        ax2.set_ylabel('A')
        ax2.set_xlim([0, 255])
        ax2.set_ylim([0, 255])
        ax2.set_title('2D Plot')

        plt.tight_layout()

        if save_title is not None:
            plt.savefig(os.path.join(self.output_folder, f'{save_title}.png'))

        if showmode:
            plt.show()
            print("=" * 150)
            return None

        else:
            fig = plt.gcf()
            fig.canvas.draw()
            img_array = np.array(fig.canvas.renderer.buffer_rgba())
            return img_array

    def _resize_window(self, window_name, width, height):
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, width, height)

    def _extract_color(self, frame, lower_bound, upper_bound):
        color_mask = cv2.inRange(frame, lower_bound, upper_bound)
        color_extraction = cv2.bitwise_and(frame, frame, mask=color_mask)
        return color_extraction

    def process_video(self, file_path, frame_interval=60, showmode=False):
        video_path = str(file_path)
        title = file_path.name.split(".")[0].replace(" ", "_")
        print(title)
        frame_filenames =[]

        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            print("Error: Could not open video.")
            exit()

        if showmode:
            self._resize_window('Original Video', 800, 600)
            self._resize_window('Gray Video', 800, 600)
            # self._resize_window('Red Extraction', 800, 600)
            # self._resize_window('Green Extraction', 800, 600)
            # self._resize_window('Blue Extraction', 800, 600)
        frame_count = 0
        while True:
            ret, frame = cap.read()

            if not ret:
                break

            # 프레임 파일로 저장
            if frame_count % frame_interval == 0:
                frame_filename = os.path.join(self.intput_folder, f'{title}_frame_{frame_count:04d}.png')
                cv2.imwrite(frame_filename, frame)
                frame_filenames.append(frame_filename)
            # 다음 프레임으로 진행
            frame_count += 1

            if showmode:
                # red_extraction = self._extract_color(frame, np.array([0, 0, 100]), np.array([100, 100, 255]))
                # green_extraction = self._extract_color(frame, np.array([0, 100, 0]), np.array([100, 255, 100]))
                # blue_extraction = self._extract_color(frame, np.array([100, 0, 0]), np.array([255, 100, 100]))

                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                cv2.imshow('Original Video', frame)
                cv2.imshow('Gray Video', gray_frame)
                # cv2.imshow('Green Extraction', green_extraction)
                # cv2.imshow('Blue Extraction', blue_extraction)

            if cv2.waitKey(25) & 0xFF == ord('q'):
                break

        cap.release()
        if showmode:
            cv2.destroyAllWindows()
        else:
            frame_filenames
