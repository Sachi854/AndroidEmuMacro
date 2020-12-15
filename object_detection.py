import cv2
import numpy as np


class ObjectDetection:
    def __init__(self):
        pass

    # ここに画像のセーブ機能をマージしてしまう
    # てか保持してるフィールドを減らす
    # まず,　フィールドを整理する
    def __pre_calc_akaze(self, query_img_path: str, train_img_path: str) -> list:
        gray1 = cv2.imread(query_img_path, 0)
        gray2 = cv2.imread(train_img_path, 0)

        detector = cv2.AKAZE_create()
        kp1, des1 = detector.detectAndCompute(gray1, None)
        kp2, des2 = detector.detectAndCompute(gray2, None)

        return [kp1, des1, kp2, des2]

    #  こっちのマッチングはたぶん使わない
    def __match_akaze(self, query_img_path: str, train_img_path: str) -> list:
        kp1, des1, kp2, des2 = self.__pre_calc_akaze(query_img_path, train_img_path)

        bf = cv2.BFMatcher_create(cv2.NORM_HAMMING, True)
        matches = bf.match(des1, des2)
        matches = sorted(matches, key=lambda x: x.distance)

        return [matches, kp1, des1, kp2, des2]

    def __match_knn_akaze(self, query_img_path: str, train_img_path: str) -> list:
        kp1, des1, kp2, des2 = self.__pre_calc_akaze(query_img_path, train_img_path)
        bf = cv2.BFMatcher_create(cv2.NORM_HAMMING)
        matches = bf.knnMatch(des1, des2, 2)

        return [matches, kp1, des1, kp2, des2]

    # akazeはグレースケールでマッチングさせるので色で判別できないので注意
    # ratio testで振り分ける方を採用(今後は一番いい順と組み合わせて精度上げたい)
    def __match_img_akaze(self, query_img_path: str, train_img_path: str, ratio=0.5) -> list:
        result = self.__match_knn_akaze(query_img_path, train_img_path)

        good = []
        for m, n in result[0]:
            if m.distance < ratio * n.distance:
                good.append(m)

        good = sorted(good, key=lambda x: x.distance)

        coordinate = []
        for elem in good:
            coordinate.append(result[1][elem.queryIdx].pt)

        return coordinate

    def match_img_feature(self, query_img_path: str, train_img_path: str, threshold=4, sample_num=20,
                          ratio=0.5) -> list:
        mr = self.__match_img_akaze(query_img_path, train_img_path, ratio)[:sample_num]

        # もっとましな方法あるはずだから要検討
        # 高精度でマッチングした点が4以上であれば処理をする
        if len(mr) >= threshold:
            r_std = np.std(np.array(mr), axis=0)
            r_average = np.average(np.array(mr), axis=0)

            # 標準偏差以上に差がある座標を削除
            result = list(
                filter(lambda x: np.abs(r_average[0] - x[0]) < r_std[0] and np.abs(r_average[1] - x[1]) < r_std[1], mr))

            return [True, np.average(np.array(result), axis=0).tolist]
        else:
            return [False, [None, None]]

    # ここに画像のセーブ機能をマージしてしまう <- 頭悪い設計
    def match_img_template(self, query_img_path: str, train_img_path: str, threshold=0.8) -> list:
        img1 = cv2.imread(query_img_path, 1)
        img2 = cv2.imread(train_img_path, 1)

        s, w, h = img2.sharp[::-1]
        # TM_CCOEFF_NORMED(相関係数法(正規化))が一番精度いいらしい, 他には相互関数, 最小二乗法等がある
        # 予測精度は1に近いほどよい(最小二乗法は0に近いほうがよい)
        res = cv2.matchTemplate(img1, img2, cv2.TM_CCOEFF_NORMED)

        loc = np.where(res >= threshold)
        # debug
        img = img0.copy()

# debug
if __name__ == '__main__':
    od = ObjectDetection()
    cd = od.match_img_feature("img/screenshot.png", "img/screenshot3.png")
    for elem in cd:
        print(elem)