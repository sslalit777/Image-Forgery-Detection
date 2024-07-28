from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from optparse import OptionParser

from flask_sqlalchemy import SQLAlchemy

import double_jpeg_compression
import image_extraction
import image_meta_data_extraction
import cfa_artifact
import noise_inconsistency
import error_level_analysis
import string_extraction
import copy_move_detection

from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil import tz
from sqlalchemy import or_

app = Flask(__name__)

app.config['INPUT_DIR'] = 'static/input'
app.config['OUTPUT_DIR'] = 'static/output'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/image_forgery'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class ImageProcessingHistory(db.Model):
    __tablename__ = 'history'
    id = db.Column(db.Integer, primary_key=True)
    input = db.Column(db.String(500))
    output = db.Column(db.String(500))
    output_type = db.Column(db.String(10))
    action = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"ImageProcessingHistory(id={self.id}, input={self.input}, output={self.output}, output_type={self.output_type}, action={self.action}, timestamp={self.timestamp})"

cmd = OptionParser("usage: %prog image_file [options]")
cmd.add_option('', '--imauto',
               help='Automatically search identical regions. (default: %default)', default=1)
cmd.add_option('', '--imblev',
               help='Blur level for degrading image details. (default: %default)', default=8)
cmd.add_option('', '--impalred',
               help='Image palette reduction factor. (default: %default)', default=15)
cmd.add_option(
    '', '--rgsim', help='Region similarity threshold. (default: %default)', default=5)
cmd.add_option(
    '', '--rgsize', help='Region size threshold. (default: %default)', default=1.5)
cmd.add_option(
    '', '--blsim', help='Block similarity threshold. (default: %default)', default=200)
cmd.add_option('', '--blcoldev',
               help='Block color deviation threshold. (default: %default)', default=0.2)
cmd.add_option(
    '', '--blint', help='Block intersection threshold. (default: %default)', default=0.2)
opt, args = cmd.parse_args()

@app.template_filter('humanize')
def humanize_time_difference_filter(target_time):
    return humanize_time_difference(target_time)

@app.route('/')
def home():
    data = ImageProcessingHistory.query.order_by(ImageProcessingHistory.timestamp.desc()).all()
    return render_template('history.html', data=data, app=app)

@app.route('/detect')
def detect():
    return render_template('detect.html')

@app.route('/history')
def history():
    action = request.args.get('action')
    if action:
        data = ImageProcessingHistory.query.filter(or_(
            ImageProcessingHistory.action.like(f'%{action}%')
        )).order_by(ImageProcessingHistory.timestamp.desc()).all()
    else:
        data = ImageProcessingHistory.query.order_by(ImageProcessingHistory.timestamp.desc()).all()
    return render_template('history.html', data=data, app=app)

@app.route('/samples')
def samples():
    action = request.args.get('action')
    samples = {
        'compression_detection': [
            "static/samples/images/compression_detection/sample1.jpg",
            "static/samples/images/compression_detection/sample2.jpg",
            "static/samples/images/compression_detection/sample3.jpg",
            "static/samples/images/compression_detection/sample4.jpg",
        ],
        'meta_data_analysis': [
            "static/samples/images/meta_data_analysis/sample1.jpg",
            "static/samples/images/meta_data_analysis/sample2.jpg",
            "static/samples/images/meta_data_analysis/sample3.jpg",
            "static/samples/images/meta_data_analysis/sample4.jpg",
            "static/samples/images/meta_data_analysis/sample5.jpg",
        ],
        'cfa_artifact_detection': [
            "static/samples/images/cfa_artifact_detection/sample1.jpeg",
            "static/samples/images/cfa_artifact_detection/sample2.jpg",
            "static/samples/images/cfa_artifact_detection/sample3.jpg",
            "static/samples/images/cfa_artifact_detection/sample4.jpeg",
            "static/samples/images/cfa_artifact_detection/sample5.jpeg",
            "static/samples/images/cfa_artifact_detection/sample6.jpeg",
        ],
        'noise_inconsistency': [
            "static/samples/images/noise_inconsistency/sample1.png",
            "static/samples/images/noise_inconsistency/sample2.jpg",
        ],
        'error_level_analysis': [
            "static/samples/images/error_level_analysis/sample1.jpg",
            "static/samples/images/error_level_analysis/sample2.jpg",
        ],
        'image_extraction': [
            "static/samples/images/image_extraction/sample1.png",
        ],
        'string_extraction': [
            "static/samples/images/string_extraction/sample1.jpg",
            "static/samples/images/string_extraction/sample2.jpg",
            "static/samples/images/string_extraction/sample3.jpg",
        ],
        'copy_move_detection': [
            "static/samples/images/copy_move_detection/sample1.png",
            "static/samples/images/copy_move_detection/sample2.jpg",
            "static/samples/images/copy_move_detection/sample3.jpeg",
            "static/samples/images/copy_move_detection/sample4.jpeg",
            "static/samples/images/copy_move_detection/sample5.jpeg",
        ],
    }
    if action:
        data = samples.get(action, [])
    else:
        data = []
    return render_template('samples.html', data=data)

@app.route('/processCompressDetection', methods=['POST'])
def processCompressDetection():
    try:
        if 'image' not in request.files:
            return jsonify({'status': False, 'type':'danger', 'message': 'No Image Selected', 'data': 'No image file provided!'})

        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'status': False, 'type':'danger', 'message': 'Invalid Image', 'data': 'Invalid image file!'})
                
        original_filename = secure_filename(file.filename)

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{original_filename}"
        
        file.save(os.path.join(app.config['INPUT_DIR'], filename))
        
        double_compressed = double_jpeg_compression.detect(app.config['INPUT_DIR'],app.config['OUTPUT_DIR'], filename)
        
        if double_compressed:
            output = "Double Compression Found"
            response = {'status': True, 'type':'danger', 'message': 'Double Compression Found', 'data': 'The image is double compressed!', 'image': os.path.join(app.config['OUTPUT_DIR'], filename)}
        else:
            output = "Single Compression Found"
            response = {'status': True, 'type':'success', 'message': 'Single Compression Found', 'data': 'The image is single compressed!', 'image': os.path.join(app.config['OUTPUT_DIR'], filename)}
        
        history_entry = ImageProcessingHistory(input=filename, output_type="image", output=filename, action="Compression Detection")
        db.session.add(history_entry)
        db.session.commit()
        
        return jsonify(response)

    except Exception as e:
        return jsonify({'status': False, 'type':'danger', 'message': "Error Exception", 'data': str(e)})
    
@app.route('/processMetaDataAnalysis', methods=['POST'])
def processMetaDataAnalysis():
    try:
        if 'image' not in request.files:
            return jsonify({'status': False, 'type':'danger', 'message': 'No Image Selected', 'data': 'No image file provided!'})

        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'status': False, 'type':'danger', 'message': 'Invalid Image', 'data': 'Invalid image file!'})
                
        original_filename = secure_filename(file.filename)

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{original_filename}"
        
        file.save(os.path.join(app.config['INPUT_DIR'], filename))
                
        image_meta_data_extracted = image_meta_data_extraction.detect(app.config['INPUT_DIR'],app.config['OUTPUT_DIR'], filename)
        
        history_entry = ImageProcessingHistory(input=filename, output_type="text", output=image_meta_data_extracted, action="Meta Data Extraction")
        db.session.add(history_entry)
        db.session.commit()
                
        if image_meta_data_extracted:
            return jsonify({'status': True, 'type':'success', 'message': 'Meta Data Found', 'data': image_meta_data_extracted})
        else:
            return jsonify({'status': True, 'type':'danger', 'message': 'No Mata Data Found', 'data': 'No mata data found associated with image!'})

    except Exception as e:
        return jsonify({'status': False, 'type':'danger', 'message': "Error Exception", 'data': str(e)})
    
@app.route('/processCfaArtifactDetection', methods=['POST'])
def processCfaArtifactDetection():
    try:
        if 'image' not in request.files:
            return jsonify({'status': False, 'type':'danger', 'message': 'No Image Selected', 'data': 'No image file provided!'})

        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'status': False, 'type':'danger', 'message': 'Invalid Image', 'data': 'Invalid image file!'})
                
        original_filename = secure_filename(file.filename)

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{original_filename}"
        
        file.save(os.path.join(app.config['INPUT_DIR'], filename))
                
        image_cfa_artifact = cfa_artifact.detect(app.config['INPUT_DIR'],app.config['OUTPUT_DIR'], filename, opt, args)
        
        history_entry = ImageProcessingHistory(input=filename, output_type="image", output=filename, action="CFA Artifact Detection")
        db.session.add(history_entry)
        db.session.commit()
                
        if image_cfa_artifact:
            return jsonify({'status': True, 'type':'danger', 'message': 'CFA Artifacts Detected', 'data': str(image_cfa_artifact) + ' CFA artifacts detected!', 'image': os.path.join(app.config['OUTPUT_DIR'], filename)})
        else:
            return jsonify({'status': True, 'type':'success', 'message': 'No CFA Artifacts Detected', 'data': 'No CFA artifacts detected!', 'image': os.path.join(app.config['OUTPUT_DIR'], filename)})

    except Exception as e:
        return jsonify({'status': False, 'type':'danger', 'message': "Error Exception", 'data': str(e)})
    
@app.route('/processNoiseInconsistency', methods=['POST'])
def processNoiseInconsistency():
    try:
        if 'image' not in request.files:
            return jsonify({'status': False, 'type':'danger', 'message': 'No Image Selected', 'data': 'No image file provided!'})

        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'status': False, 'type':'danger', 'message': 'Invalid Image', 'data': 'Invalid image file!'})
                
        original_filename = secure_filename(file.filename)

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{original_filename}"
        
        file.save(os.path.join(app.config['INPUT_DIR'], filename))
                
        image_noise_inconsistency = noise_inconsistency.detect(app.config['INPUT_DIR'],app.config['OUTPUT_DIR'], filename)
        
        if image_noise_inconsistency:
            output = "Noise Inconsistency Found"
            response = {'status': True, 'type':'danger', 'message': 'Noise Inconsistency Found', 'data': 'Noise inconsistency found!'}
        else:
            output = "No Noise Inconsistency Found"
            response = {'status': True, 'type':'success', 'message': 'No Noise Inconsistency Found', 'data': 'No noise inconsistency found with image!'}
        
        history_entry = ImageProcessingHistory(input=filename, output_type="text", output=output, action="Noise Inconsistency Detection")
        db.session.add(history_entry)
        db.session.commit()
                
        return jsonify(response)

    except Exception as e:
        return jsonify({'status': False, 'type':'danger', 'message': "Error Exception", 'data': str(e)})
    
@app.route('/processErrorLevelAnalysis', methods=['POST'])
def processErrorLevelAnalysis():
    try:
        if 'image' not in request.files:
            return jsonify({'status': False, 'type':'danger', 'message': 'No Image Selected', 'data': 'No image file provided!'})

        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'status': False, 'type':'danger', 'message': 'Invalid Image', 'data': 'Invalid image file!'})
                
        original_filename = secure_filename(file.filename)

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{original_filename}"
        
        file.save(os.path.join(app.config['INPUT_DIR'], filename))
                
        image_error_level_analysis = error_level_analysis.detect(app.config['INPUT_DIR'],app.config['OUTPUT_DIR'], filename)
                
        history_entry = ImageProcessingHistory(input=filename, output_type="image", output=filename, action="Error Level Analysis")
        db.session.add(history_entry)
        db.session.commit()
        
        if image_error_level_analysis:
            return jsonify({'status': True, 'type':'success', 'message': 'Image Error Level Analysis Completed', 'data': 'Image error level analysis completed successfuly!', 'image': os.path.join(app.config['OUTPUT_DIR'], filename)})
        else:
            return jsonify({'status': False, 'type':'danger', 'message': 'Image Error Level Analysis Failed', 'data': 'Image error level analysis failed due to some error!'})

    except Exception as e:
        return jsonify({'status': False, 'type':'danger', 'message': "Error Exception", 'data': str(e)})

@app.route('/processImageExtraction', methods=['POST'])
def processImageExtraction():
    try:
        if 'image' not in request.files:
            return jsonify({'status': False, 'type':'danger', 'message': 'No Image Selected', 'data': 'No image file provided!'})

        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'status': False, 'type':'danger', 'message': 'Invalid Image', 'data': 'Invalid image file!'})
                
        original_filename = secure_filename(file.filename)

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{original_filename}"
        
        file.save(os.path.join(app.config['INPUT_DIR'], filename))
                
        image_extracted = image_extraction.detect(app.config['INPUT_DIR'],app.config['OUTPUT_DIR'], filename)
        
        history_entry = ImageProcessingHistory(input=filename, output_type="image", output=filename, action="Image Extraction")
        db.session.add(history_entry)
        db.session.commit()
        
        if image_extracted:
            return jsonify({'status': True, 'type':'success', 'message': 'Image Extracted Successfuly', 'data': 'Image extracted successfuly!', 'image': os.path.join(app.config['OUTPUT_DIR'], filename)})
        else:
            return jsonify({'status': False, 'type':'danger', 'message': 'Image Extraction Failed', 'data': 'Image extraction failed due to some error!'})

    except Exception as e:
        return jsonify({'status': False, 'type':'danger', 'message': "Error Exception", 'data': str(e)})
    
@app.route('/processStringExtraction', methods=['POST'])
def processStringExtraction():
    try:
        if 'image' not in request.files:
            return jsonify({'status': False, 'type':'danger', 'message': 'No Image Selected', 'data': 'No image file provided!'})

        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'status': False, 'type':'danger', 'message': 'Invalid Image', 'data': 'Invalid image file!'})
                
        original_filename = secure_filename(file.filename)

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{original_filename}"
        
        file.save(os.path.join(app.config['INPUT_DIR'], filename))
                
        image_string_extraction = string_extraction.detect(app.config['INPUT_DIR'],app.config['OUTPUT_DIR'], filename)
        
        if image_string_extraction:
            output_filename = filename.split('.')[0]
            with open(os.path.join(app.config['OUTPUT_DIR'], output_filename + '.txt'), 'w') as f:
                image_string_extraction_data = image_string_extraction.replace('<pre>', '').replace('</pre>', '')
                f.write(image_string_extraction_data)
            history_entry = ImageProcessingHistory(input=filename, output_type="file", output=output_filename + '.txt', action="String Extraction")
            db.session.add(history_entry)
            db.session.commit()
            return jsonify({'status': True, 'type':'success', 'message': "Image String Extracted", 'data': image_string_extraction})
        else:
            history_entry = ImageProcessingHistory(input=filename, output_type="text", output="String Extraction Failed", action="String Extraction")
            db.session.add(history_entry)
            db.session.commit()
            return jsonify({'status': False, 'type':'danger', 'message': 'Image String Extraction Failed', 'data': 'Image string extraction failed due to some error!'})

    except Exception as e:
        return jsonify({'status': False, 'type':'danger', 'message': "Error Exception", 'data': str(e)})
    
@app.route('/processCopyMoveDetection', methods=['POST'])
def processCopyMoveDetection():
    try:
        if 'image' not in request.files:
            return jsonify({'status': False, 'type':'danger', 'message': 'No Image Selected', 'data': 'No image file provided!'})

        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'status': False, 'type':'danger', 'message': 'Invalid Image', 'data': 'Invalid image file!'})
                
        original_filename = secure_filename(file.filename)

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{original_filename}"
        
        file.save(os.path.join(app.config['INPUT_DIR'], filename))
                
        image_copy_move_detection = copy_move_detection.detect(app.config['INPUT_DIR'],app.config['OUTPUT_DIR'], filename)
        
        history_entry = ImageProcessingHistory(input=filename, output_type="image", output=filename, action="Copy Move Detection")
        db.session.add(history_entry)
        db.session.commit()
        
        if image_copy_move_detection:
            return jsonify({'status': True, 'type':'danger', 'message': 'Copy Move Forgery Detected', 'data': 'Copy move forgery detected in image!', 'image': os.path.join(app.config['OUTPUT_DIR'], filename)})
        else:
            return jsonify({'status': True, 'type':'success', 'message': 'No Copy Move Detected', 'data': 'No copy move detection found!', 'image': os.path.join(app.config['INPUT_DIR'], filename)})

    except Exception as e:
        return jsonify({'status': False, 'type':'danger', 'message': "Error Exception", 'data': str(e)})



def humanize_time_difference(target_time):
    now = datetime.now(target_time.tzinfo)  # Ensure both times are in the same timezone
    diff = relativedelta(now, target_time)
    
    if diff.years > 0:
        return f"{diff.years} {'year' if diff.years == 1 else 'years'} ago"
    elif diff.months > 0:
        return f"{diff.months} {'month' if diff.months == 1 else 'months'} ago"
    elif diff.days > 0:
        return f"{diff.days} {'day' if diff.days == 1 else 'days'} ago"
    elif diff.hours > 0:
        return f"{diff.hours} {'hour' if diff.hours == 1 else 'hours'} ago"
    elif diff.minutes > 0:
        return f"{diff.minutes} {'minute' if diff.minutes == 1 else 'minutes'} ago"
    else:
        return "Just now"
    
if __name__ == '__main__':
    app.run(debug=True)
