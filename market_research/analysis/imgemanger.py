import cv2
import os
import numpy as np
import matplotlib.pyplot as plt
from pytube import YouTube
from PIL import Image
import colour
# from colour import MSDS_CMFS, SPECTRAL_SHAPE_DEFAULT
from ._analysis_scheme import Analysis
from tqdm import tqdm


class ImgAnalysis(Analysis):
    def __init__(self,
                 export_prefix="text_", intput_folder_path="input", output_folder_path="results"):
        super().__init__(export_prefix=export_prefix, intput_folder_path=intput_folder_path,
                         output_folder_path=output_folder_path)

        self.preset_video_dict={
                                # 'elemental1_1': 'https://www.youtube.com/watch?v=JK29WoCFZ4c',
                                'supermario1_1': 'https://www.youtube.com/watch?v=rhKeo86YpyE',
                                'spideman1_1':'https://www.youtube.com/watch?v=tumNjgEfXz0',
                                # 'spideman1_2': 'https://www.youtube.com/watch?v=3N0wxkPtzVs',
                                # 'spideman1_3': 'https://www.youtube.com/watch?v=7F0GITe1UWk',
                                'spideman2-1':'https://www.youtube.com/watch?v=4RlYCscGLHg&t=76s',
                                # 'spideman2-2': 'https://www.youtube.com/watch?v=eIPkkK85bl0',
                                # 'lgoled_2023_1': 'https://www.youtube.com/watch?v=xT6NbiPqsT0',
                                # 'lgoled_2023_2': 'https://youtu.be/TA1jS07SfeU?si=HtO83elrrSo6_yRM',
                                # 'lgoled_2023_3': 'https://youtu.be/xT6NbiPqsT0?si=2wMoWauuEqiBbXsE',
                                'oled_4k': 'https://youtu.be/kF-0q042Jjk?si=OLsUt7koxNHdLOA-',
                                'barbie 4k':'https://www.youtube.com/watch?v=z5-Y7O4s8D4',
                                # 'topgun 4k':'https://www.youtube.com/watch?v=szXQBwmjAOo',
                                'avata 4k': 'https://www.youtube.com/watch?v=rJNBGqiBI7s',
                                # 'end game 4k':'https://www.youtube.com/watch?v=rrGMENN1iaY'
                                }

    def read_files_from_inputpath(self, docs_type="img"):

        file_type = {"img": ['.png', '.jpeg'],
                     "video": ['.mp4', '.webm']
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
                video_stream = yt.streams.filter().order_by('resolution').desc().first()
                video_stream.download(output_path=self.intput_folder)
                filename = video_stream.default_filename
                file_path = os.path.join(os.getcwd(), f"{filename}")
                break
            except Exception as e:
                pass

        return file_path

        # ============================================
        # cal color temperature
        # ============================================

    # def _calculate_average_color(self, image):
    #     # 이미지를 numpy 배열로 변환
    #     np_img = np.array(image)
    #
    #     # RGBA 이미지인 경우 RGB로 변환
    #     if np_img.shape[2] == 4:
    #         np_img = np_img[:, :, :3]
    #
    #     # 평균 색상 계산
    #     average_color = np.mean(np_img, axis=(0, 1))
    #     return average_color

    # def _map_color_to_temperature(self, average_color):
    #     # RGB를 XYZ로 변환
    #     XYZ = colour.sRGB_to_XYZ(average_color / 255)
    #
    #     # cmfs 설정 (CIE 1931 2도 표준 관찰자)
    #     cmfs = (
    #         MSDS_CMFS["CIE 1931 2 Degree Standard Observer"]
    #         .copy()
    #         .align(SPECTRAL_SHAPE_DEFAULT)
    #     )
    #
    #     # 관련 색온도(CCT)와 델타 UV 추정 (Ohno 2013 방법 사용)
    #     CCT, delta_uv = colour.temperature.XYZ_to_CCT_Ohno2013(XYZ, cmfs=cmfs)
    #     return CCT, delta_uv

    # def estimate_color_temperature(self, image_path):
    #     with Image.open(image_path) as img:
    #         average_color = self._calculate_average_color(img)
    #         CCT, delta_uv = self._map_color_to_temperature(average_color)
    #         return int(CCT), delta_uv

    # ============================================

    def to_lab_images(self, image_list, showmode=True):
        for filename in tqdm(image_list):
            image_path = str(filename)
            title = filename.name.split(".")[0]
            image_BGR = cv2.imread(image_path)
            for _ in range(10):
                try:
                    # color_temp, delta_uv = self.estimate_color_temperature(image_path)  ##색온도
                    _ = self.to_lab_image(image=image_BGR, save_title=title, showmode=showmode)


                    break
                except Exception as e:
                    print(e)
                    pass

    def to_lab_image(self, image, input_type='BGR', save_title: str = None, showmode=True):
        if showmode:
            # BGR을 RGB로 변환
            img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            plt.imshow(img_rgb)
            plt.axis('off')
            plt.show()

        conversion = cv2.COLOR_BGR2Luv if input_type == 'BGR' else cv2.COLOR_RGB2Luv
        image_LUV = cv2.cvtColor(image, conversion)

        y, x, z = image_LUV.shape
        LUV_flat = np.reshape(image_LUV, [y * x, z])

        colors = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) if input_type == 'BGR' else image
        colors = np.reshape(colors, [y * x, z]) / 255.


        l = LUV_flat[:, 0]
        u = LUV_flat[:, 1]
        v = LUV_flat[:, 2]

        # l_max = max(l)
        # u_max = max(u)
        # v_max = max(v)

        fig = plt.figure(figsize=(12, 12))

        ax1 = fig.add_subplot(221, projection='3d')
        ax1.scatter(xs=u,ys=v, zs=l, s=10, c=colors, lw=0)
        ax1.set_xlabel('u')
        ax1.set_ylabel('v')
        ax1.set_zlabel('l')
        ax1.set_xlim([0, 255])
        ax1.set_ylim([0, 255])
        ax1.set_zlim([0, 255])
        ax1.set_title('L-U-V')
        # ax1.xaxis.pane.fill = False
        # ax1.yaxis.pane.fill = False
        # ax1.zaxis.pane.fill = False
        # ax1.grid(False)
        ax1.set_xticks([])
        ax1.set_yticks([])
        ax1.set_zticks([])

        # 두 번째 서브플롯 (2D scatter plot)
        ax2 = fig.add_subplot(222)
        ax2.scatter(y=v, x=u, s=10, c=colors, lw=0)
        ax2.set_xlabel('u')
        ax2.set_ylabel('v')
        ax2.set_xlim([0, 255])
        ax2.set_ylim([0, 255])
        ax2.set_xticks([])
        ax2.set_yticks([])
        ax2.set_title('U-V')

        # 두 번째 서브플롯 (2D scatter plot)
        ax3 = fig.add_subplot(223)
        ax3.scatter(x=u, y=l, s=10, c=colors, lw=0)
        ax3.set_xlabel('u')
        ax3.set_ylabel('l')
        ax3.set_xlim([0, 255])
        ax3.set_ylim([0, 255])
        ax3.set_xticks([])
        ax3.set_yticks([])
        ax3.set_title('L-U')


        # 두 번째 서브플롯 (2D scatter plot)
        ax4 = fig.add_subplot(224)
        ax4.scatter(x=v, y=l, s=10, c=colors, lw=0)
        ax4.set_xlabel('v')
        ax4.set_ylabel('l')
        ax4.set_xlim([0, 255])
        ax4.set_ylim([0, 255])
        ax4.set_xticks([])
        ax4.set_yticks([])
        ax4.set_title('L-V')
        plt.tight_layout()

        if save_title is not None:
            plt.savefig(os.path.join(self.output_folder, f'{save_title}.png'))

        if showmode:
            plt.show()
            print("=" * 150)
            return None


    def _resize_window(self, window_name, width, height):
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, width, height)

    def _extract_color(self, frame, lower_bound, upper_bound):
        color_mask = cv2.inRange(frame, lower_bound, upper_bound)
        color_extraction = cv2.bitwise_and(frame, frame, mask=color_mask)
        return color_extraction

    def process_video(self, file_path, skip_interval =60, showmode=False):
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
        frame_number = 0
        while True:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = cap.read()

            if not ret:
                break

            # 프레임 파일로 저장

            frame_filename = os.path.join(self.intput_folder, f'{title}_frame_{frame_number:04d}.png')
            cv2.imwrite(frame_filename, frame)
            # 다음 프레임으로 진행
            frame_number += skip_interval

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
            return frame_filenames
