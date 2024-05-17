import os
import subprocess
from zipfile import ZipFile
from flask import Flask, request, send_file, jsonify, render_template, redirect, url_for, after_this_request
from werkzeug.utils import secure_filename
from multiprocessing import Queue
import threading
import logging
import uuid
import cv2

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)

# Global variables
task_queue = Queue()
processing_status = {}

class WorkerThread(threading.Thread):
    def __init__(self, task_queue):
        threading.Thread.__init__(self)
        self.task_queue = task_queue

    def run(self):
        while True:
            task = self.task_queue.get()
            if task is None:
                break
            task_id, images, operation, image_ids = task
            if len(images) == 1:
                self.process_single_image(task_id, images, operation, image_ids)
            else:
                self.distribute_tasks(task_id, images, operation, image_ids)

    def process_single_image(self, task_id, images, operation, image_ids):
        num_nodes = 3

        # Split the single image into parts
        parts = self.split_image(images[0], num_nodes)

        # Save each part to a file and log the assignment
        for i, part in enumerate(parts):
            part_filename = f'/shared/{task_id}_part{i}.jpg'
            cv2.imwrite(part_filename, part)
            logging.info(f"Part {i} of image {task_id} assigned to machine: n{i+1}")

            # Execute MPI process for each part
            mpi_command = [
                'mpirun', '-np', '1',
                '--host', f'n{i+1}',
                'python3', '/shared/slave_process.py', operation, f'{task_id}_part{i}.jpg'
            ]
            subprocess.run(mpi_command)

        processing_status[task_id] = {'total': 1, 'completed': 1}

    def distribute_tasks(self, task_id, images, operation, image_ids):
        num_nodes = 3
        chunk_size = len(images) // num_nodes
        remainder = len(images) % num_nodes  # Remainder for uneven distribution

        # Distribute tasks among nodes
        start_index = 0
        for i in range(num_nodes):
            end_index = start_index + chunk_size
            if i < remainder:  # Distribute remaining images
                end_index += 1
            chunk = images[start_index:end_index]
            start_index = end_index
            with open(f'/shared/chunk_{i}.txt', 'w') as f:
                f.write('\n'.join(chunk))
            logging.info(f"Chunk {i} assigned to machine: n{i+1}")

        mpi_command = [
            'mpirun', '-np', str(num_nodes),
            '--host', 'n1,n2,n3',
            'python3', '/shared/slave_process.py', operation, ' '.join(image_ids)
        ]
        subprocess.run(mpi_command)
        processing_status[task_id] = {'total': len(images), 'completed': len(images)}

    def split_image(self, image, num_parts):
        # Load the image
        img = cv2.imread(image, cv2.IMREAD_COLOR)
        height, width, _ = img.shape

        # Calculate the width of each part
        part_width = width // num_parts

        parts = []
        for i in range(num_parts):
            start_col = i * part_width
            end_col = start_col + part_width
            part_img = img[:, start_col:end_col, :]
            parts.append(part_img)

        return parts

@app.before_request
def log_request_info():
    app.logger.info('Request received: %s %s', request.method, request.url)

@app.after_request
def log_response_info(response):
    app.logger.info('Response sent: %s', response.status)
    return response

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files[]' not in request.files:
        return jsonify({'error': 'No file part'})
    
    files = request.files.getlist('files[]')
    if len(files) == 0:
        return jsonify({'error': 'No files selected'})

    image_ids = []
    filenames = []
    if len(files) == 1:
        # Rename the single image to 2.jpg
        file = files[0]
        if file.filename == '':
            return jsonify({'error': 'No file selected'})
        filename = '2.jpg'
        filepath = os.path.join('/shared', filename)
        file.save(filepath)
        image_id = '2'
        image_ids.append(image_id)
        filenames.append(filepath)
    else:
        for file in files:
            if file.filename == '':
                continue
            filename = secure_filename(file.filename)
            filepath = os.path.join('/shared', filename)
            file.save(filepath)
            image_id = os.path.splitext(filename)[0]
            image_ids.append(image_id)
            filenames.append(filepath)

    task_id = uuid.uuid4().hex  # Generate unique task ID
    processing_status[task_id] = {'total': len(files), 'completed': 0}

    task_queue.put((task_id, filenames, request.form['operation'], image_ids))
    
    return redirect(url_for('processing_page', task_id=task_id))

@app.route('/status/<task_id>')
def check_status(task_id):
    status = processing_status.get(task_id, {})
    return jsonify(status)

@app.route('/processing/<task_id>')
def processing_page(task_id):
    return render_template('processing.html', task_id=task_id)

@app.route('/result/<task_id>')
def get_result(task_id):
    zip_filename = f'{task_id}_processed.zip'
    zip_filepath = os.path.join('/shared', zip_filename)
    with ZipFile(zip_filepath, 'w') as zipf:
        for filename in os.listdir('/shared'):
            if filename.endswith('_processed.jpg'):
                zipf.write(os.path.join('/shared', filename), filename)

    @after_this_request
    def delete_files(response):
        try:
            result = subprocess.run(['/shared/del_jpg.sh'], check=True, capture_output=True, text=True)
            app.logger.info('Deletion script output: %s', result.stdout)
            app.logger.info('Deletion script error (if any): %s', result.stderr)
            app.logger.info('All files deleted successfully after download.')
        except subprocess.CalledProcessError as e:
            app.logger.error('Error executing deletion script: %s', e)
            app.logger.error('Deletion script output: %s', e.output)
        return response

    return send_file(zip_filepath, as_attachment=True)

if __name__ == '__main__':
    # Create worker threads
    num_workers = 1  # Single-threaded processing
    workers = [WorkerThread(task_queue) for _ in range(num_workers)]
    for worker in workers:
        worker.start()

    app.run(host='0.0.0.0', port=5000)
