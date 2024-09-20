from flask import Flask, request, render_template, send_from_directory
import os
from werkzeug.utils import secure_filename
from DeepImageSearch import Load_Data, Search_Setup
import pandas as pd

image_list = Load_Data().from_folder(['static/images/'])


image_names = [os.path.basename(image) for image in image_list]


st = Search_Setup(image_list=image_list, model_name='vgg19', pretrained=True, image_count=9843)

st.run_index()

metadata = st.get_image_metadata_file()

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part"
        file = request.files['file']
        if file.filename == '':
            return "No selected file"
        
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            similar_images_dict = st.get_similar_images(image_path=file_path, number_of_images=15)
            similar_images = list(similar_images_dict.values())
            
            #similar_images = [image_names[index] for index in similar_images_indices]

            return render_template('result.html', uploaded_image=filename, similar_images=similar_images)
            

    return render_template('index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)