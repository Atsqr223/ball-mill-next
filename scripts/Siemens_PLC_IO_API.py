from flask import Flask, request, jsonify
import snap7
from snap7.util import set_bool
import snap7.type

app = Flask(__name__)

PLC_IP = '10.135.114.201'
RACK = 0
SLOT = 1

# Keep the PLC client as a global singleton
plc = snap7.client.Client()
plc.connect(PLC_IP, RACK, SLOT)

def write_m0_0(value):
    byte_index = 0
    bit_index = 0
    data = plc.read_area(snap7.type.Areas.MK, 0, byte_index, 1)
    set_bool(data, 0, bit_index, value)
    plc.write_area(snap7.type.Areas.MK, 0, byte_index, data)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010) 