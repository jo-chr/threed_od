import datetime
import json
import os, sys
import logging
import logging.handlers as handlers
import numpy as np
import time
import open3d as o3d
import math
import argparse
import importlib
from os import environ
from os import path

from flask import Flask
from flask import make_response
from flask import request, send_from_directory
from flask import abort
from flask import jsonify
from PIL import Image
from scipy.special import softmax

import torch
import torch.nn as nn
import torch.optim as optim

from _version import __version__

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = BASE_DIR
sys.path.append(os.path.join(ROOT_DIR, 'utils'))
sys.path.append(os.path.join(ROOT_DIR, 'models'))
sys.path.append(os.path.join(ROOT_DIR, 'data'))
from pc_util import random_sampling, read_ply
from ap_helper import parse_predictions
from detection_dataset import DC # dataset config


app = Flask(__name__)

def get_appsetting():
    with open('appsettings.json') as config_file:
        data = json.load(config_file)
    return data

def get_model_path():
    config = get_appsetting()
    modelPath = config['WebApiSettings']['ModelPath']
    return modelPath

def create_logger():
    config = get_appsetting()
    logLevel = config['Logging']['LogLevel']
    logLevel = logging.getLevelName(logLevel)
    logPath = config['Logging']['LogPath']

    if path.exists(logPath)==True:
        pass
    else:
        os.mkdir(logPath)
    #setup logger
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger('PyTorch_API_Logger')
    logger.setLevel(logLevel)

    #log to console
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(formatter)
    #log to file
    fileHandler = handlers.TimedRotatingFileHandler(logPath+'/timed_app.log', when='midnight', interval=1)
    fileHandler.setFormatter(formatter)
    #add handlers to logger
    logger.addHandler(consoleHandler)
    logger.addHandler(fileHandler)
    #disable werkzeug logs
    log = logging.getLogger('werkzeug')
    log.disabled = True

    return logger

logger = create_logger()
logger.info('PyTorch Web-API started.')


def get_models_config():
    #returns all models from the config file
    with open(get_model_path() + '/modelconfig.json') as config_file:
        data = json.load(config_file)
    return data

def get_object_from_config(model_id):
    #returns a specific model (by model_id)
    with open(get_model_path() + '/modelconfig.json') as config_file:
        conf = json.load(config_file)
    for model in conf['models']:
        if model['id'] == model_id:
            return model    
    
def check_model_id(model_id):
    '''validates model id
    :model_id empty --> HTTP 400
    :model_id not in the config.json --> HTTP 404
    '''
    conf = get_models_config()
    registered_models=[]
    for x in conf['models']:
        registered_models.append(x['id'])
    
    if not model_id:
        return abort(400, 'Model_ID is missing')
    elif model_id not in registered_models:
        return abort(404, 'Model with ID not found')
    else:
        pass

def get_cloud(request):
    '''get the cloud file from request
    :no file or wrong key --> HTTP 400
    '''
    try:
        cloud_file = request.files['file']
        return cloud_file
    except KeyError:
        return abort(400, 'KeyError') 

def check_file(cloud_file):
    '''checks the image file format
    :wrong format --> HTTP 415
    '''
    if cloud_file.content_type == 'application/octet-stream':
        pass
    else:
        return abort(415, 'Wrong file format. Clouds must be .ply.')

def create_response(content):
    '''create the JSON-Response of the models
    return: JSON response
    '''
    response = app.response_class(
        response=content,
        status=200,
        mimetype='application/json'
    )
    return response

def preprocess_point_cloud(point_cloud):
    ''' Prepare the numpy point cloud (N,3) for forward pass '''
    point_cloud = point_cloud[:,0:3] # do not use color for now
    floor_height = np.percentile(point_cloud[:,2],0.99)
    height = point_cloud[:,2] - floor_height
    point_cloud = np.concatenate([point_cloud, np.expand_dims(height, 1)],1) # (N,4) or (N,7)
    #point_cloud = random_sampling(point_cloud, FLAGS.num_point)
    point_cloud = random_sampling(point_cloud, 20000)
    pc = np.expand_dims(point_cloud.astype(np.float32), 0) # (1,40000,4)
    return pc

@app.route('/api/models', methods=['GET'])
def get_models():
    ''' Request for getting all available models from the config.json
    return: JSON of available models (id, name and type)
    '''
    data = get_models_config()
    models=[]
    for x in data['models']:
        models.append({'id': x['id'], 'name': x['name'], 'type': x['type']})

    #create response
    output = json.dumps(models, separators=(',', ':'))
    return create_response(output)

@app.route('/api/detect', methods=['POST'])
def detect_cloud():

    model_id = request.args.get('model_id')
    check_model_id(model_id)    

    model_conf = get_object_from_config(model_id)
    if model_conf['type'] == '3d_detection':
        pass
    else:
        return abort(400, 'The desired model does not support detection.')

    #get and validate cloud file
    cloud_file = get_cloud(request)
    #check_file(cloud_file)

    checkpoint_path = os.path.join(get_model_path(), model_conf['model_path'])

    eval_config_dict = {'remove_empty_box': True, 'use_3d_nms': True, 'nms_iou': 0.25,
        'use_old_type_nms': False, 'cls_nms': False, 'per_class_proposal': False,
        'conf_thresh': 0.15, 'dataset_config': DC}

    # Init the model and optimzier
    MODEL = importlib.import_module('votenet') # import network module
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    net = MODEL.VoteNet(num_proposal=256, input_feature_dim=1, vote_factor=1,
        sampling='seed_fps', num_class=DC.num_class,
        num_heading_bin=DC.num_heading_bin,
        num_size_cluster=DC.num_size_cluster,
        mean_size_arr=DC.mean_size_arr).to(device)
    print('Constructed model.')
    
    # Load checkpoint
    optimizer = optim.Adam(net.parameters(), lr=0.01)
    checkpoint = torch.load(checkpoint_path)
    net.load_state_dict(checkpoint['model_state_dict'])
    optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    epoch = checkpoint['epoch']
    print("Loaded checkpoint %s (epoch: %d)"%(checkpoint_path, epoch))
   
    # Load and preprocess input point cloud 
    net.eval() # set model to eval mode (for bn and dp)
    

    point_cloud = read_ply(cloud_file)
    pc = preprocess_point_cloud(point_cloud)
    print('Loaded point cloud data: %s'%(cloud_file))
   
    # Model inference
    inputs = {'point_clouds': torch.from_numpy(pc).to(device)}
    tic = time.time()
    with torch.no_grad():
        end_points = net(inputs)
    
    toc = time.time()
    print('Inference time: %f'%(toc-tic))
    end_points['point_clouds'] = inputs['point_clouds']
    pred_map_cls = parse_predictions(end_points, eval_config_dict)
    logger.debug(pred_map_cls)
    print('Finished detection. %d object detected.'%(len(pred_map_cls[0])))

    print(pred_map_cls[0][0][1])

    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(pred_map_cls[0][0][1])
    pcd.rotate(pcd.get_rotation_matrix_from_xyz([300,0,0]), center=False)
    coords = np.asarray(pcd.points)
    print(coords)

    output = []
    
    for i in range(len(pred_map_cls[0])):
        prediction = {'class':'box', 'confidence':np.float64(pred_map_cls[0][i][2]),
        'coordinates':{j:k for j,k in enumerate(coords.tolist())}}
        output.append(prediction)
    
    return jsonify(output)

@app.route('/api/detect_dump_results', methods=['POST'])
def detect_cloud_dump():

    model_id = request.args.get('model_id')
    check_model_id(model_id)    

    model_conf = get_object_from_config(model_id)
    if model_conf['type'] == '3d_detection':
        pass
    else:
        return abort(400, 'The desired model does not support detection.')

    #get and validate cloud file
    cloud_file = get_cloud(request)
    #check_file(cloud_file)

    checkpoint_path = os.path.join(get_model_path(), model_conf['model_path'])

    eval_config_dict = {'remove_empty_box': True, 'use_3d_nms': True, 'nms_iou': 0.25,
        'use_old_type_nms': False, 'cls_nms': False, 'per_class_proposal': False,
        'conf_thresh': 0.15, 'dataset_config': DC}

    # Init the model and optimzier
    MODEL = importlib.import_module('votenet') # import network module
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    net = MODEL.VoteNet(num_proposal=256, input_feature_dim=1, vote_factor=1,
        sampling='seed_fps', num_class=DC.num_class,
        num_heading_bin=DC.num_heading_bin,
        num_size_cluster=DC.num_size_cluster,
        mean_size_arr=DC.mean_size_arr).to(device)
    print('Constructed model.')
    
    # Load checkpoint
    optimizer = optim.Adam(net.parameters(), lr=0.01)
    checkpoint = torch.load(checkpoint_path)
    net.load_state_dict(checkpoint['model_state_dict'])
    optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    epoch = checkpoint['epoch']
    print("Loaded checkpoint %s (epoch: %d)"%(checkpoint_path, epoch))
   
    # Load and preprocess input point cloud 
    net.eval() # set model to eval mode (for bn and dp)
    

    point_cloud = read_ply(cloud_file)
    pc = preprocess_point_cloud(point_cloud)
    print('Loaded point cloud data: %s'%(cloud_file))
   
    # Model inference
    inputs = {'point_clouds': torch.from_numpy(pc).to(device)}
    tic = time.time()
    with torch.no_grad():
        end_points = net(inputs)
    
    toc = time.time()
    print('Inference time: %f'%(toc-tic))
    end_points['point_clouds'] = inputs['point_clouds']
    pred_map_cls = parse_predictions(end_points, eval_config_dict)
    logger.debug(pred_map_cls)
    print('Finished detection. %d object detected.'%(len(pred_map_cls[0])))

    dump_dir = os.path.join('../dump/')
    if not os.path.exists(dump_dir): os.mkdir(dump_dir) 
    MODEL.dump_results(end_points, dump_dir, DC, True)
    print('Dumped detection results to folder %s'%(dump_dir))

    output = []
    
    for i in range(len(pred_map_cls[0])):
        prediction = {'class_id':pred_map_cls[0][i][0], 'confidence':np.float64(pred_map_cls[0][i][2]),
        'coordinates':{j:k for j,k in enumerate(pred_map_cls[0][i][1].tolist())}}
        output.append(prediction)
    
    return jsonify(output)

@app.route('/api/version', methods=['GET'])
def get_api_version():
    ''' Request for getting the current API version
    return: API-Version
    '''
    version = __version__
    
    #create response
    output = json.dumps(version, separators=(',', ':'))
    return create_response(output)

@app.before_request
def before_request():
    logger.debug(request.method + request.path)

@app.after_request
def after_request(response):
    if response.status_code == 200:
        logger.debug(response.status + ', response:' + str(response.data.decode('utf-8')))
    return response

#error handler
@app.errorhandler(Exception)
def handle_unexpected_error(error):
    logger.error(error, exc_info=True)
    return make_response('An unexpected error has occurred.', 500)

@app.errorhandler(500)
def internal_error(error):
    logger.error(str(error))
    return make_response(str(error), 500)

@app.errorhandler(400)
def bad_request(error):
    logger.error(str(error))
    return make_response(str(error), 400)

@app.errorhandler(404)
def not_found(error):
    logger.error(str(error))
    return make_response(str(error), 404)

@app.errorhandler(415)
def unsuported_media_type(error):
    logger.error(str(error))
    return make_response(str(error), 415)


#main method to run the server
if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='PyTorch WebAPI')
    parser.add_argument('--V','--version', action='version',version='%(prog)s ' + __version__)
    args = parser.parse_args()
    
    if args == 'version':
        parser.parse_args(['--version'])
    else:
        from waitress import serve
        serve(app, host="0.0.0.0", port=8080)
    '''
    if args == 'version':
        parser.parse_args(['--version'])
    else:
        app.run(debug=True)
    '''

