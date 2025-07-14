import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
load_dotenv()

#All this has been commented out because we are not using the PLC directly.
#We are using the Azure VM to control the PLC. 

# import snap7
# from snap7.util import set_bool, get_bool
# import snap7.type

app = Flask(__name__)

# PLC_IP = os.environ.get('PLC_IP', '10.135.114.201')
# RACK = int(os.environ.get('PLC_RACK', 0))
# SLOT = int(os.environ.get('PLC_SLOT', 1))

# # Keep the PLC client as a global singleton
# plc = snap7.client.Client()
# plc.connect(PLC_IP, RACK, SLOT)

compressor_state = False  # Store compressor state in memory

def write_m0_0(value):
    # byte_index = 0
    # bit_index = 0
    # data = plc.read_area(snap7.type.Areas.MK, 0, byte_index, 1)
    # set_bool(data, 0, bit_index, value)
    # plc.write_area(snap7.type.Areas.MK, 0, byte_index, data)
    global compressor_state
    compressor_state = value

def read_m0_0():
    # byte_index = 0
    # bit_index = 0
    # data = plc.read_area(snap7.type.Areas.MK, 0, byte_index, 1)
    # return get_bool(data, 0, bit_index)
    return compressor_state

@app.route('/plc-io', methods=['POST'])
def plc_io():
    try:
        req = request.get_json()
        value = req.get('value')
        if value is None:
            return jsonify({'error': 'Missing value'}), 400
        write_m0_0(bool(value))
        return jsonify({'success': True, 'value': value})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    try:
        state = read_m0_0()
        return jsonify({'compressor': state})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    host = os.environ.get('PLC_SERVER_HOST', '0.0.0.0')
    port = int(os.environ.get('PLC_SERVER_PORT', 5010))
    app.run(host=host, port=port) 