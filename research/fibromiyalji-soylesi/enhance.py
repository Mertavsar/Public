import cv2, numpy as np, sys, os
S="/tmp/claude-0/-home-user-Public/119613b5-b24d-5275-ab76-18cbd0d2ab95/"
IMG=S+"images/"; OUT=S+"scratchpad/edit/"
sr=cv2.dnn_superres.DnnSuperResImpl_create(); sr.readModel(S+"scratchpad/models/FSRCNN_x4.pb"); sr.setModel("fsrcnn",4)
def wb(img):  # gray-world beyaz dengesi, yumuşak
    f=img.astype(np.float32); m=f.reshape(-1,3).mean(0); g=m.mean()
    f=f*(1+0.6*(g/m-1)); return np.clip(f,0,255).astype(np.uint8)
def tone(img):
    lab=cv2.cvtColor(img,cv2.COLOR_BGR2LAB); l,a,b=cv2.split(lab)
    l=cv2.createCLAHE(clipLimit=1.15,tileGridSize=(8,8)).apply(l)
    img=cv2.cvtColor(cv2.merge([l,a,b]),cv2.COLOR_LAB2BGR)
    hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV).astype(np.float32); hsv[...,1]*=1.08
    img=cv2.cvtColor(np.clip(hsv,0,255).astype(np.uint8),cv2.COLOR_HSV2BGR)
    return cv2.convertScaleAbs(img,alpha=1.04,beta=6)
def sharpen(img,amt=0.6,r=1.2):
    bl=cv2.GaussianBlur(img,(0,0),r); return cv2.addWeighted(img,1+amt,bl,-amt,0)
def job(name,src,box,size):
    img=cv2.imread(IMG+src); x0,y0,x1,y1=box
    crop=img[y0:y1,x0:x1]
    crop=cv2.fastNlMeansDenoisingColored(crop,None,3,3,7,21)
    up=sr.upsample(crop)
    up=cv2.resize(up,size,interpolation=cv2.INTER_AREA if up.shape[1]>size[0] else cv2.INTER_CUBIC)
    up=tone(wb(up))
    # düz alanlarda bantlaşmayı yumuşat: düşük detaylı bölgeleri bulanıklaştır
    g=cv2.cvtColor(up,cv2.COLOR_BGR2GRAY).astype(np.float32)
    det=cv2.GaussianBlur(np.abs(cv2.Laplacian(g,cv2.CV_32F)),(0,0),6)
    m=np.clip((det-1.5)/4.0,0,1)[...,None]
    smooth=cv2.GaussianBlur(up,(0,0),5).astype(np.float32)
    up=(up.astype(np.float32)*m+smooth*(1-m))
    up=sharpen(np.clip(up,0,255).astype(np.uint8),0.45,1.0).astype(np.float32)
    rng=np.random.default_rng(7); up+=rng.normal(0,2.2,up.shape[:2])[...,None]
    up=np.clip(up,0,255).astype(np.uint8)
    cv2.imwrite(OUT+name,up,[cv2.IMWRITE_JPEG_QUALITY,95]); print(name,crop.shape,'->',up.shape)
job("A-hande.jpg","6.jpg",(195,700,755,1400),(1080,1350))
job("B-ferda.jpg","4.jpg",(130,650,690,1350),(1080,1350))
job("C-plaket.jpg","5.jpg",(240,820,880,1620),(1080,1350))
job("D-salon.jpg","6.jpg",(0,520,923,1674),(1080,1350))
job("E-ferda2.jpg","3.jpg",(130,640,690,1340),(1080,1350))
