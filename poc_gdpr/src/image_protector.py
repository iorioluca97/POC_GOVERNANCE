import cv2
from PIL import Image
import numpy as np
from IPython.display import display


class ImageProtector:
  def __init__(self, image_path):
    self.image_path = image_path
    self.image = cv2.imread(image_path)
    self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

  def _save_image(self, img, save_path):
    cv2.imwrite(save_path, img)
    print(f"Immagine salvata in: {save_path}")

  def blur_faces(self, save_path="./data/blurred_images/blurred_image.jpg"):
    img = cv2.imread(self.image_path)
    faces = self.face_cascade.detectMultiScale(img, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    print(str(len(faces)) + " faces detected.")

    for (x, y, w, h) in faces:
        face_roi = img[y:y+h, x:x+w]
        blurred_roi = cv2.GaussianBlur(face_roi, (99, 99), 30)
        img[y:y+h, x:x+w] = blurred_roi

    # Save locally the result
    self._save_image(img, save_path)

  def pixellate_faces(self, 
      block_size = (30, 30), 
      save_path="./data/pixellated_images/pixellated_image.jpg"):
    img = cv2.imread(self.image_path)
    faces = self.face_cascade.detectMultiScale(img, scaleFactor=1.1, minNeighbors=5, minSize=block_size)

    print(str(len(faces)) + " faces detected.")

    for (x, y, w, h) in faces:
        # select region of interest to blur
        face_roi = img[y:y+h, x:x+w]

        small = cv2.resize(face_roi, (10,10))
        pixelated_roi = cv2.resize(small, (w,h), interpolation=cv2.INTER_NEAREST)

        # Replace the original region of interest with the blurred one
        img[y:y+h, x:x+w] = pixelated_roi

    # Save locally the result
    self._save_image(img, save_path)

def get_image(url, save_path="./data/input_images/input_image.jpg"):
  import requests
  from io import BytesIO

  try:
    # fetch image from the web
    res = requests.get(url)
    res.raise_for_status() # raise HTTP errors

    # convert to PIL image
    img = Image.open(BytesIO(res.content))

    img_to_save = np.array(img)
    img_to_save = cv2.cvtColor(img_to_save, cv2.COLOR_RGB2BGR)
    # Save locally the result
    cv2.imwrite(save_path, img_to_save)
    print(f"Immagine salvata in: {save_path}")

    return img

  except requests.RequestException as e:
    print(f"Error fetching image: {e}")
    return None

def display_image(img):
  # convert BGR to RGB
  image_np = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

  # convert back to PIL image and display it
  display(Image.fromarray(image_np))


# Example usage
img = get_image('https://images.pexels.com/photos/3812743/pexels-photo-3812743.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1')
image_protector = ImageProtector("./data/input_images/input_image.jpg")
image_protector.blur_faces()
image_protector.pixellate_faces()



