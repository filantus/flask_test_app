import os
from flask import Flask, request, Response, jsonify, render_template, send_from_directory
from models import db_init, Car, Component


app = Flask(__name__, static_url_path='', template_folder='./templates/')
app.config.from_object('config')
db_init(app)


@app.route('/static/<path:path>')
def send_static(path):
    if os.path.exists('./static/%s' % path):
        return send_from_directory('./static/', path)
    print('File not found: /static/%s' % path)
    return ''


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', cars=Car.all(), components=Component.all())


@app.route('/api/car/<uuid:car_uuid>', methods=['GET'])
def get_car(car_uuid):
    if not Car.where(uid=car_uuid).count():
        return Response('Car not found', status=404)

    car = Car.where(uid=car_uuid).first()
    return jsonify(car.data())


@app.route('/api/car', methods=['POST', 'PUT', 'PATCH'])
def create_car():
    input_data = request.get_json() if request.is_json else request.form.to_dict()
    if not input_data:
        Response('Data not provided!', status=400)

    keys = [col.key for col in Car.__table__.columns]
    data = {k: input_data.get(k) or None for k in keys}

    car = Car(**data)
    car.save()

    return jsonify(car.data())


@app.route('/api/component/<uuid:component_uuid>', methods=['GET'])
def get_component(component_uuid):
    if not Component.where(uid=component_uuid).count():
        return Response('Component not found', status=404)

    component = Component.where(uid=component_uuid).first()
    return jsonify(component.data())


@app.route('/api/component', methods=['POST', 'PUT', 'PATCH'])
def create_component():
    input_data = request.get_json() if request.is_json else request.form.to_dict()
    if not input_data:
        Response('Data not provided!', status=400)

    keys = [col.key for col in Component.__table__.columns]
    data = {k: input_data.get(k) or None for k in keys}

    component = Component(**data)
    component.save()

    return jsonify(component.data())


if __name__ == '__main__':
    app.run(port=80, threaded=True)
