#导入cv模块
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt 

filename = "20201121_GF_2/20201121_GF_2/2020112100533.tif"

img = cv.imread(filename,-1)

#img_scaled = cv.normalize(img, dst=None, alpha=0, beta=65535, norm_type=cv.NORM_MINMAX)


plt.imshow(img, cmap="gray", vmin=0, vmax=4096)
plt.show()

#plt.imshow(img_scaled)
#plt.show()


#outputImg8U = cv.convertScaleAbs(img, alpha=(255.0/65535.0))
#在这里一开始我写成了img.shape（），报错因为img是一个数组不是一个函数，只有函数才可以加()表示请求执行，
#参考http://blog.csdn.net/a19990412/article/details/78283742
'''
print (img.shape)
print (img.dtype )
print (img.min())
print (img.max())
#创建窗口并显示图像
cv.namedWindow("Image")
cv.imshow("Image",img)
cv.waitKey(0)#释放窗口
cv.destroyAllWindows() 
'''